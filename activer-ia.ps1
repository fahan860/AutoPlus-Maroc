# AUTO+ : active la recommandation de garages (Modele B) et l'Assistant IA.
# A lancer apres lancer-tlf.ps1, avec Docker demarre :
#   powershell -ExecutionPolicy Bypass -File .\activer-ia.ps1
# Relancable sans risque (tout est idempotent).

$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
function Step($msg) { Write-Host "`n=== $msg" -ForegroundColor Cyan }
function Fail($msg) { Write-Host "ERREUR : $msg" -ForegroundColor Red; exit 1 }
$DB_URL = "postgres://autoplus:autoplus@db:5432/autoplus"

function Psql($sql) { docker exec autoplus-db psql -U autoplus -d autoplus -tAc $sql }

Step "Verification de la base"
docker exec autoplus-db pg_isready -U autoplus *> $null
if ($LASTEXITCODE -ne 0) { Fail "autoplus-db ne tourne pas. Lance d'abord lancer-tlf.ps1." }

# 1. pgvector (fourni par l'image db/Dockerfile)
Step "Extension pgvector"
$dispo = Psql "SELECT 1 FROM pg_available_extensions WHERE name='vector'"
if ("$dispo".Trim() -ne "1") {
  Fail "pgvector absent : la base tourne encore sur l'ancienne image. Lance : docker compose up -d --build db  (puis relance ce script)"
}
Write-Host "  pgvector disponible." -ForegroundColor Green

# Si la base vient de l'ancienne image (Debian 11) : mettre a jour PostGIS et les index texte
$collation = Psql "SELECT datcollversion IS DISTINCT FROM pg_database_collation_actual_version(oid) FROM pg_database WHERE datname='autoplus'"
if ("$collation".Trim() -eq "t") {
  Write-Host "  Base issue de l'ancienne image : mise a jour PostGIS et reindexation (une seule fois)..."
  Psql "SELECT postgis_extensions_upgrade();" | Out-Null
  Psql "REINDEX DATABASE autoplus;" | Out-Null
  Psql "ALTER DATABASE autoplus REFRESH COLLATION VERSION;" | Out-Null
}

# 2. Tables base_pannes, kb_documents, kb_chunks
Step "Creation des tables IA"
foreach ($f in @("data\pannes\schema.sql", "ai\db\schema.sql")) {
  Write-Host "  - $f"
  Get-Content $f -Raw | docker exec -i autoplus-db psql -q -U autoplus -d autoplus -v ON_ERROR_STOP=1 | Out-Null
  if ($LASTEXITCODE -ne 0) { Fail "$f en erreur." }
}

# 3. Cle LLM pour l'Assistant (lue par ml-api dans api\.env)
Step "Cle LLM de l'Assistant"
$envFile = "api\.env"
$aCle = (Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^(GROQ|MISTRAL)_API_KEY=\S+' -Quiet)
if ($aCle) {
  Write-Host "  Cle deja presente dans api\.env." -ForegroundColor Green
} else {
  Write-Host "  Cree une cle gratuite sur https://console.groq.com/keys (sans carte bancaire)."
  $cle = Read-Host "  Colle ta cle Groq (gsk_...), ou Entree pour passer"
  if ($cle) {
    Add-Content -Path $envFile -Value "GROQ_API_KEY=$($cle.Trim())"
    Add-Content -Path $envFile -Value "LLM_FOURNISSEUR=groq"
    Write-Host "  Cle enregistree dans api\.env (fichier ignore par git)." -ForegroundColor Green
  } else {
    Write-Host "  Pas de cle : la recommandation marchera, l'Assistant restera indisponible." -ForegroundColor Yellow
  }
}

# 4. Chargement des donnees, dans le conteneur ml-api (Python, PyTorch et e5-large y sont deja)
function RunPy($script) {
  Write-Host "  - $script"
  docker compose run --rm --no-deps -v "${PWD}:/repo" -e DATABASE_URL=$DB_URL -e PYTHONIOENCODING=utf-8 -e HF_HUB_DISABLE_XET=1 -e HF_HUB_DOWNLOAD_TIMEOUT=60 `
    --entrypoint python ml-api "/repo/$script"
  if ($LASTEXITCODE -ne 0) { Fail "$script en erreur (voir le message ci-dessus)." }
}
Step "Chargement des pannes, des specialites et de la base de connaissance"
# Le volume hf-cache peut avoir ete cree par Docker avec root comme proprietaire : ml-api
# (utilisateur appuser) ne pourrait alors pas y telecharger e5-large -> on corrige les droits.
docker compose run --rm --no-deps --user root --entrypoint chown ml-api -R appuser:appuser /home/appuser/.cache/huggingface
if ($LASTEXITCODE -ne 0) { Fail "Impossible de corriger les droits du volume hf-cache." }
Write-Host "  (1re fois : telechargement du modele e5-large ~2 Go si pas encore en cache)" -ForegroundColor Yellow
RunPy "data/pannes/load_embeddings.py"
RunPy "data/scraping/enrich_garages.py"
RunPy "ai/scripts/load_kb_corpus.py"

$res = Psql "SELECT (SELECT count(*) FROM base_pannes) || ' pannes, ' || (SELECT count(*) FROM kb_chunks) || ' passages KB, ' || (SELECT count(*) FROM garages WHERE specialites IS NOT NULL) || ' garages avec specialites'"
Write-Host "  $res" -ForegroundColor Green

# 5. Redemarrage de ml-api pour qu'il charge les modeles
Step "Redemarrage de ml-api"
docker compose up -d --force-recreate ml-api | Out-Null
$h = $null
for ($i = 0; $i -lt 60; $i++) {
  try { $h = Invoke-RestMethod http://localhost:8000/health -TimeoutSec 3; if ($h) { break } } catch { Start-Sleep -Seconds 3 }
}
if (-not $h) { Fail "ml-api ne repond pas. Voir : docker compose logs ml-api" }
Write-Host ($h | ConvertTo-Json -Depth 3)
if ($h.status -eq 'ok') {
  Write-Host "`nTout est actif. Sur le telephone : 'Trouver un garage' et l'onglet Assistant." -ForegroundColor Green
} else {
  Write-Host "`nUn modele manque encore (valeur null ci-dessus). Envoie : docker compose logs ml-api | Select-String 'non charg'" -ForegroundColor Yellow
}

exit 0
