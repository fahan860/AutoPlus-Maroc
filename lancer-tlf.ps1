# AUTO+ : premier lancement complet (ou relance) pour tester l'app sur telephone :
# backend Docker, migrations, garages, donnees IA (activer-ia.ps1), puis Expo.
# Usage (PowerShell, depuis le dossier AutoPlus-Maroc) :
#   powershell -ExecutionPolicy Bypass -File .\lancer-tlf.ps1
# Options : -SkipPull (ne pas faire git pull), -SkipBuild (pas de --build Docker)
param([switch]$SkipPull, [switch]$SkipBuild)

$ErrorActionPreference = 'Continue'  # on teste $LASTEXITCODE nous-memes (PS 5.1 transforme le stderr de docker/git en erreurs)
Set-Location $PSScriptRoot

function Step($msg) { Write-Host "`n=== $msg" -ForegroundColor Cyan }
function Fail($msg) { Write-Host "ERREUR : $msg" -ForegroundColor Red; exit 1 }

# 1. Docker Desktop doit tourner
Step "Verification de Docker"
docker info *> $null
if ($LASTEXITCODE -ne 0) { Fail "Docker Desktop n'est pas lance. Ouvre-le, attends qu'il soit pret, puis relance ce script." }

# 2. Mettre le code a jour (ta copie locale n'a pas encore la migration 009 ni l'onglet Assistant)
if (-not $SkipPull) {
  Step "Mise a jour du code (git pull)"
  git pull --ff-only
  if ($LASTEXITCODE -ne 0) {
    Write-Host "git pull a echoue (souvent a cause de package-lock.json modifies)." -ForegroundColor Yellow
    Write-Host "Essaie : git checkout -- api/package-lock.json mobile/package-lock.json ; puis relance." -ForegroundColor Yellow
    Write-Host "Ou relance avec -SkipPull pour continuer avec le code actuel." -ForegroundColor Yellow
    exit 1
  }
}

# 3. .env
if (-not (Test-Path .env)) { Step "Creation du .env"; Copy-Item .env.example .env }

# 4. Conteneurs
Step "Demarrage de db, redis, api, ml-api (le 1er build peut etre long)"
if ($SkipBuild) { docker compose up -d } else { docker compose up -d --build --renew-anon-volumes }  # renouvelle le node_modules du conteneur api (sinon "Cannot find module")
if ($LASTEXITCODE -ne 0) { Fail "docker compose up a echoue. Voir : docker compose logs" }

Step "Attente de PostgreSQL"
$ok = $false
for ($i = 0; $i -lt 60; $i++) {
  docker exec autoplus-db pg_isready -U autoplus *> $null
  if ($LASTEXITCODE -eq 0) { $ok = $true; break }
  Start-Sleep -Seconds 2
}
if (-not $ok) { Fail "PostgreSQL ne repond pas. Voir : docker compose logs db" }

# 5. Migrations (toutes idempotentes : on peut les rejouer sans risque)
Step "Application des migrations"
Get-ChildItem api\migrations\*.sql | Sort-Object Name | ForEach-Object {
  Write-Host "  - $($_.Name)"
  Get-Content $_.FullName -Raw | docker exec -i autoplus-db psql -q -U autoplus -d autoplus -v ON_ERROR_STOP=1 | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "Migration $($_.Name) en erreur." }
}

# 6. Garages (UPSERT : relancer ne cree pas de doublons)
Step "Import des garages"
Push-Location api
if (-not (Test-Path node_modules)) { npm install }
$env:DATABASE_URL = "postgres://autoplus:autoplus@localhost:5432/autoplus"
node scripts/import_garages_csv.js ../data/scraping/garages_clean.csv
$importExit = $LASTEXITCODE
Pop-Location
if ($importExit -ne 0) { Fail "Import des garages en erreur." }

# 7. API
Step "Test de l'API"
$apiOk = $false
for ($i = 0; $i -lt 30; $i++) {
  try { $h = Invoke-RestMethod http://localhost:3000/health -TimeoutSec 3; $apiOk = $true; break } catch { Start-Sleep -Seconds 2 }
}
if (-not $apiOk) { Fail "L'API ne repond pas sur le port 3000. Voir : docker compose logs api" }
Write-Host "  API OK : $($h | ConvertTo-Json -Compress)" -ForegroundColor Green

# 8. Pare-feu (le telephone doit pouvoir joindre le port 3000)
Step "Pare-feu Windows (port 3000)"
$rule = Get-NetFirewallRule -DisplayName "AutoPlus API 3000" -ErrorAction SilentlyContinue
if ($rule) {
  Write-Host "  Regle deja presente." -ForegroundColor Green
} else {
  $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if ($isAdmin) {
    New-NetFirewallRule -DisplayName "AutoPlus API 3000" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow -Profile Private | Out-Null
    Write-Host "  Regle creee." -ForegroundColor Green
  } else {
    Write-Host "  Pas de regle et pas admin : si le telephone n'atteint pas l'API, relance ce script UNE fois en administrateur." -ForegroundColor Yellow
  }
}

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -in 'Dhcp','Manual' -and $_.IPAddress -notlike '169.*' -and $_.InterfaceAlias -notmatch 'vEthernet|VirtualBox|WSL|Loopback' } | Select-Object -First 1).IPAddress
Write-Host "`nTest depuis le telephone (navigateur) : http://${ip}:3000/health" -ForegroundColor Magenta

# 9. Donnees IA : pgvector, pannes, specialites des garages, base de connaissance, cle LLM
Step "Activation de la recommandation et de l'Assistant (activer-ia.ps1)"
& "$PSScriptRoot\activer-ia.ps1"
if ($LASTEXITCODE -ne 0) { Fail "activer-ia.ps1 a echoue (voir ci-dessus)." }
Set-Location $PSScriptRoot

# 10. Expo
Step "Demarrage d'Expo : scanne le QR code avec Expo Go"
Set-Location mobile
if (-not (Test-Path node_modules)) { npm install }
npx expo start
