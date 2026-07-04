# AUTO+ — ML

Environnement Python 3.10 dédié aux notebooks d'exploration et futurs modèles ML
(pricing véhicule, recommandation garage, détection faux avis).

## Setup

```powershell
py -3.10 -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\jupyter notebook notebooks/01_exploration.ipynb
```

> Sur ce poste, Avast (SSL/TLS scanning) intercepte les connexions HTTPS avec son propre
> certificat racine, ce qui fait échouer `pip` (`CERTIFICATE_VERIFY_FAILED`) car pip ne lit pas
> le magasin de certificats Windows. Si ça se reproduit, définir `PIP_CERT` vers un bundle
> combinant `certifi` + le certificat racine Avast avant d'installer :
> ```powershell
> $env:PIP_CERT = "chemin\vers\combined-cacert.pem"
> ```
