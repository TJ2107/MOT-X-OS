# MOT-X OS — Ambient Cognitive Operating System

> **L'ordinateur qui disparaît, devient invisible, et pense à ta place avant même que tu le saches.**

MOT-X OS est un pont d'automatisation locale intelligent qui fusionne IA locale (Ollama), interface web temps réel et intelligence ambiante pour transformer votre poste de travail en un assistant cognitif invisible.

---

## ✨ Fonctionnalités

| Pilier | Description |
|--------|-------------|
| 🕵️ **Shadow Mode** | Observe silencieusement vos actions et génère automatiquement des workflows |
| 🎯 **Look & Do** | Interface multimodale (eye-tracking + voix) pour interagir sans friction |
| 🧠 **Semantic Rewind** | Mémoire épisodique — retrouvez n'importe quoi par association d'idées |
| 🌀 **Liquid OS** | L'environnement se transforme selon votre état cognitif (Focus, Créatif, Réunion…) |
| 🕳️ **Black Hole Folder** | Jetez vos fichiers dans `~/MOT-X_Nexus`, ils disparaissent mais restent retrouvables à jamais |

### Fonctionnalités de base
- 🤖 Exécution de commandes système via IA locale (Ollama / llama2)
- 🔒 Couche de sécurité avec chemins bloqués et mode Dry Run
- 📊 Dashboard analytique temps réel
- 🧬 Architecture multi-agents cognitifs
- 🎮 Système de gamification intégré
- 🔌 Architecture de plugins extensible

---

## 🏗️ Architecture

```
UTILISATEUR
    ↓
┌─────────────────────────────────────────────────┐
│  Frontend React (Vite) — localhost:5173         │
│  Dashboard • Exécution • Agents • Analytics     │
└──────────────────────┬──────────────────────────┘
                       │ proxy /api + /ws
┌──────────────────────▼──────────────────────────┐
│  Backend FastAPI (Uvicorn) — localhost:8000      │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Shadow   │ │ Look &   │ │ Semantic Rewind  │ │
│  │ Mode     │ │ Do       │ │ (Mémoire)        │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Liquid   │ │ Black    │ │ WebSocket        │ │
│  │ OS       │ │ Hole     │ │ (Temps réel)     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│                                                  │
│  Engine • Planner • Executor • Security          │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  Ollama (LLM Local) — localhost:11434            │
│  llama2:latest                                   │
└─────────────────────────────────────────────────┘
```

---

## 📁 Structure du Projet

```
MOT-X OS/
├── docs/                    # Documentation (PLUGINS.md)
├── logs/                    # Journaux du serveur
├── motx-frontend/           # Interface React (Vite)
│   ├── src/
│   │   ├── App.jsx          # Composant principal
│   │   └── ...
│   ├── package.json
│   └── vite.config.js       # Proxy vers le backend
├── resources/               # Ressources statiques
├── scripts/                 # Scripts de démarrage
│   ├── start.ps1            # Windows
│   └── start.sh             # Linux/Mac
├── src/
│   └── motx_os_bridge/
│       ├── api/
│       │   ├── fastapi_server.py   # Serveur principal (FastAPI)
│       │   └── server.py           # Serveur legacy (http.server)
│       ├── core/
│       │   ├── engine.py           # Moteur d'automatisation
│       │   ├── cognitive_layer.py  # Couche cognitive (IA)
│       │   ├── planner.py          # Planificateur de tâches
│       │   ├── executor.py         # Exécuteur de tâches
│       │   └── security.py         # Sécurité et validation
│       ├── plugins/
│       │   ├── shadow_mode_engine.py      # 🕵️ Pilier 1
│       │   ├── look_and_do_engine.py      # 🎯 Pilier 2
│       │   ├── semantic_rewind_engine.py  # 🧠 Pilier 3
│       │   ├── liquid_os_engine.py        # 🌀 Pilier 4
│       │   ├── black_hole_folder.py       # 🕳️ Killer Feature
│       │   ├── websocket_manager.py       # WebSocket
│       │   ├── filesystem.py              # Gestion fichiers
│       │   ├── shell.py                   # Commandes shell
│       │   └── ...
│       ├── utils/
│       │   ├── llm_client.py       # Client LLM (Ollama)
│       │   └── config_loader.py    # Chargement config
│       └── main.py                 # Point d'entrée
├── tests/                   # Tests unitaires
├── pyproject.toml           # Configuration projet
├── docker-compose.yml       # Orchestration Docker
└── Dockerfile.backend       # Image Docker
```

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) avec le modèle `llama2`

### Installation

```bash
# 1. Cloner le projet
git clone <repo-url>
cd MOT-X OS

# 2. Créer l'environnement virtuel et installer les dépendances
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .

# 3. Installer le frontend
cd motx-frontend
npm install
cd ..

# 4. S'assurer qu'Ollama tourne
ollama pull llama2
```

### Lancement

```bash
# Terminal 1 — Backend
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
.venv\Scripts\python -m src.motx_os_bridge.main

# Terminal 2 — Frontend
cd motx-frontend
npm run dev
```

Ouvrez **http://localhost:5173** dans votre navigateur.

---

## 🕳️ Le Black Hole Folder

Le dossier magique où vous ne triez **jamais** vos fichiers :

1. Créez `C:\Users\<VOTRE_USER>\MOT-X_Nexus`
2. Déposez n'importe quel fichier dedans
3. Il **disparaît** en moins de 2 secondes
4. Plus tard, retrouvez-le via l'API :
   ```
   GET http://localhost:8000/api/nexus/search?q=facture+mars
   ```
5. Restaurez-le :
   ```
   POST http://localhost:8000/api/nexus/recover/{file_id}
   ```

---

## 📡 API Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/status` | Statut du système |
| `GET` | `/api/analytics/dashboard` | Tableau de bord |
| `POST` | `/api/shadow/start` | Démarrer l'observation silencieuse |
| `POST` | `/api/shadow/stop` | Arrêter et générer les workflows |
| `POST` | `/api/cognitive/state` | Détecter l'état cognitif |
| `POST` | `/api/multimodal/voice` | Commande vocale |
| `GET` | `/api/memory/search?q=...` | Recherche mémoire épisodique |
| `GET` | `/api/memory/recover/{id}` | Récupérer un moment passé |
| `POST` | `/api/nexus/upload` | Upload vers le Black Hole |
| `GET` | `/api/nexus/search?q=...` | Chercher un fichier disparu |
| `POST` | `/api/nexus/recover/{id}` | Faire réapparaître un fichier |
| `GET` | `/docs` | Swagger UI (documentation interactive) |

---

## 🔒 Sécurité

- **Mode Dry Run** : Simulation sans exécution réelle
- **Chemins bloqués** : Interdiction d'accès aux dossiers système critiques
- **Validation des tâches** : Filtrage des commandes dangereuses
- **Audit Log** : Journalisation de toutes les actions
- **Exécution locale uniquement** : Aucune donnée ne quitte votre machine

---

## 📜 Licence

Projet propriétaire — © NDAYA Teddy Jordan
