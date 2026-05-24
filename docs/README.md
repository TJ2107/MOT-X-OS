# MOT-X OS Automation Bridge

Système d’automatisation locale sécurisé et fusionnable avec votre OS.

## Installation

1. Crée un environnement virtuel Python 3.10+ :

```bash
python -m venv .venv
```

2. Active-le :

- Windows PowerShell : `.\venv\Scripts\Activate.ps1`
- Windows cmd : `.\venv\Scripts\activate.bat`
- macOS/Linux : `source .venv/bin/activate`

3. Installe les dépendances :

```bash
pip install -r requirements.txt
```

4. Lance l’application :

```bash
python -m src.motx_os_bridge.main
```

Ou installe le package localement :

```bash
pip install .
motx-os
```

## Fonctionnement

- `python -m src.motx_os_bridge.main` : lance l’interface en ligne de commande et le serveur API.
- `motx-os` : lance l’application si le package est installé.

## API

- `GET /status` ou `GET /health` : vérifie le service.
- `GET /history` : récupère l’historique des tâches.
- `GET /config` : retourne la configuration active.
- `GET /tasks` : liste les types de tâches supportés.
- `GET /dashboard` : ouvre le tableau de bord web simple.
- `POST /execute` : exécute une instruction via JSON.

### Authentification API

Configure un token dans `src/motx_os_bridge/config/settings.yaml` :

```yaml
api:
  enabled: true
  host: "127.0.0.1"
  port: 8000
  token: "mon-secret-token"
```

Appel sécurisé :

```bash
curl -X POST http://127.0.0.1:8000/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mon-secret-token" \
  -d '{"instruction":"surveiller cpu"}'
```

## Cas d’usage rapides

- Ouvrir Notepad :

```bash
curl -X POST http://127.0.0.1:8000/execute \
  -H "Authorization: Bearer mon-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"ouvrir notepad"}'
```

- Créer un dossier :

```bash
curl -X POST http://127.0.0.1:8000/execute \
  -H "Authorization: Bearer mon-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"créer un dossier \"projet\""}'
```

- Traduire du texte :

```bash
curl -X POST http://127.0.0.1:8000/execute \
  -H "Authorization: Bearer mon-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"traduire \"hello world\" en français"}'
```

- Prendre une note :

```bash
curl -X POST http://127.0.0.1:8000/execute \
  -H "Authorization: Bearer mon-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"prendre une note \"Vérifier les logs du serveur\""}'
```

- Accéder à la dashboard :

```bash
open http://127.0.0.1:8000/dashboard
```

## Structure du projet

```text
src/motx_os_bridge/
├── api/
├── config/
├── core/
├── plugins/
├── tests/
```

## Notes

- L’historique des tâches est persisté dans `src/motx_os_bridge/config/history.json`.
- Le planificateur utilise désormais un backend LLM local lorsqu’il est disponible, avec une chute automatique vers la logique rule-based si nécessaire.
- La dashboard est accessible via `GET /dashboard`.
- La configuration de sécurité supporte `allowed_paths` et `blocked_paths`.
- Les scripts `scripts/start.ps1` et `scripts/start.sh` permettent de lancer rapidement l’application.
curl -X POST http://127.0.0.1:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"instruction":"ouvrir notepad"}'