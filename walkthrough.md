# MOT-X OS — Fonctionnement Pas à Pas

## 🏗️ Architecture Globale

```mermaid
graph TB
    subgraph "UTILISATEUR"
        U["👤 Vous"]
        B["🌐 Navigateur (localhost:5173)"]
        N["📁 Dossier MOT-X_Nexus"]
        T["💻 Terminal (CLI)"]
    end
    
    subgraph "FRONTEND (Vite/React - Port 5173)"
        FE["App.jsx"]
        FE -->|"proxy /api/*"| FA
        FE -->|"proxy /ws/*"| WS
    end
    
    subgraph "BACKEND (FastAPI/Uvicorn - Port 8000)"
        FA["fastapi_server.py"]
        WS["WebSocket /ws/{id}"]
        FA --> SM["Shadow Mode Engine"]
        FA --> LD["Look & Do Engine"]
        FA --> SR["Semantic Rewind"]
        FA --> LO["Liquid OS"]
        FA --> BH["Black Hole Folder"]
    end
    
    subgraph "INTELLIGENCE (Ollama - Port 11434)"
        LLM["🧠 llama2:latest"]
    end
    
    U --> B
    U --> N
    U --> T
    T --> ENG["engine.py + cognitive_layer.py"]
    ENG --> LLM
```

---

## Étape 1 : Le Démarrage

Quand vous lancez `python -m src.motx_os_bridge.main`, voici ce qui se passe :

```mermaid
sequenceDiagram
    participant User as Terminal
    participant Main as main.py
    participant Engine as MOTXAutomationEngine
    participant FastAPI as fastapi_server.py
    participant Uvicorn as Uvicorn (Thread)
    participant BH as BlackHoleFolder
    
    User->>Main: python -m src.motx_os_bridge.main
    Main->>Engine: MOTXAutomationEngine(interactive=True)
    Note over Engine: Charge les plugins, se connecte à Ollama
    Main->>Main: load_settings() → lit config.yaml
    Main->>Uvicorn: start_fastapi_server(host, port)
    Note over Uvicorn: Nouveau Thread daemon lancé
    Uvicorn->>FastAPI: uvicorn.run(app, port=8000)
    FastAPI->>FastAPI: @on_event("startup")
    FastAPI->>BH: asyncio.create_task(watch_nexus_folder())
    Note over BH: 👁️ Surveillance du dossier ~/MOT-X_Nexus
    Main->>User: "📝 MOT-X > " (attend vos commandes)
```

**En résumé :**
1. `main.py` crée le moteur d'automatisation et se connecte à Ollama (LLM local).
2. Il lance **FastAPI dans un thread séparé** via Uvicorn sur le port 8000.
3. Au démarrage de FastAPI, le **Black Hole Folder** commence à surveiller `~/MOT-X_Nexus` en arrière-plan.
4. Le terminal affiche le prompt `📝 MOT-X >` et attend vos commandes CLI.

> [!IMPORTANT]
> Le terminal (`input()`) et FastAPI tournent dans **deux boucles séparées**. C'est pour cela que le Black Hole fonctionne : il vit dans la boucle asyncio de FastAPI (non-bloquée), pas dans celle du terminal (bloquée par `input()`).

---

## Étape 2 : Le Frontend React

Quand vous ouvrez `http://localhost:5173` dans votre navigateur :

```mermaid
sequenceDiagram
    participant Browser as Navigateur
    participant Vite as Vite Dev Server (5173)
    participant FastAPI as FastAPI (8000)
    
    Browser->>Vite: GET http://localhost:5173
    Vite->>Browser: index.html + App.jsx (React)
    
    Note over Browser: L'app React se charge...
    
    Browser->>Vite: GET /api/status
    Vite->>FastAPI: Proxy → GET http://localhost:8000/api/status
    FastAPI->>Vite: {"status": "ok", "service": "MOT-X Ambient API"}
    Vite->>Browser: Réponse JSON
    Note over Browser: ✅ Statut = Connecté
    
    Browser->>Vite: WebSocket /ws/user_123
    Vite->>FastAPI: Proxy → ws://localhost:8000/ws/user_123
    FastAPI->>Browser: WebSocket accepté
    Note over Browser: 🟢 Connexion temps réel établie
```

**Le rôle de Vite :** C'est un "passe-plat". Il sert les fichiers React au navigateur, et **redirige automatiquement** toutes les requêtes `/api/*` et `/ws/*` vers FastAPI sur le port 8000. L'utilisateur ne voit qu'un seul port (5173).

---

## Étape 3 : Le Black Hole Folder (La Killer Feature)

C'est le composant le plus spectaculaire. Voici exactement ce qui se passe quand vous déposez un fichier :

```mermaid
sequenceDiagram
    participant User as Vous
    participant Folder as ~/MOT-X_Nexus
    participant Watcher as watch_nexus_folder()
    participant Ingest as ingest_file()
    participant DB as semantic_database {}
    
    User->>Folder: Dépose "facture_mars.txt"
    
    loop Toutes les 2 secondes
        Watcher->>Folder: os.listdir() → quoi de neuf ?
    end
    
    Watcher->>Watcher: Détecte "facture_mars.txt" (nouveau!)
    Watcher->>Ingest: ingest_file(path, filename)
    
    Note over Ingest: 1. Lit le contenu du fichier
    Note over Ingest: 2. Extrait les métadonnées (taille, date)
    Note over Ingest: 3. Vectorise le contenu (embedding 768D)
    Note over Ingest: 4. Crée un record complet
    
    Ingest->>DB: Stocke le record (contenu + vecteur + metadata)
    Ingest->>Folder: os.remove("facture_mars.txt")
    
    Note over Folder: ✨ Le fichier DISPARAÎT
    Note over DB: 💾 Mais son contenu vit dans la mémoire
```

**Le cycle de vie d'un fichier :**
1. **Détection** : Le watcher compare `os.listdir()` toutes les 2 secondes avec la liste précédente.
2. **Lecture** : Le contenu du fichier est lu intégralement en mémoire.
3. **Vectorisation** : Le texte est converti en un vecteur de 768 dimensions (simulation NumPy actuellement, en production ce serait un vrai modèle d'embedding comme `all-MiniLM-L6`).
4. **Archivage** : Le contenu brut + le vecteur + les métadonnées sont stockés dans un dictionnaire Python en mémoire.
5. **Suppression** : Le fichier original est supprimé du disque. Il "disparaît".
6. **Recherche** : Plus tard, quand vous cherchez "facture", le système compare votre requête vectorisée avec tous les vecteurs stockés (similarité cosinus) et retrouve le fichier.

---

## Étape 4 : Le Shadow Mode

Le Shadow Mode observe silencieusement votre travail pour apprendre vos habitudes :

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Recording: POST /api/shadow/start
    
    state Recording {
        [*] --> ScreenMonitor
        [*] --> MouseKeyboard
        [*] --> AppSwitching
        [*] --> PatternAnalysis
        
        ScreenMonitor: 📹 Capture écran (toutes les 2s)
        MouseKeyboard: 🖱️ Clics + Frappes clavier
        AppSwitching: 🔄 Changements d'application
        PatternAnalysis: 🧠 Analyse des séquences (toutes les 30 actions)
    }
    
    Recording --> Analysis: POST /api/shadow/stop
    Analysis --> WorkflowGeneration: Séquences répétitives détectées
    WorkflowGeneration --> [*]: Workflows proposés
```

**Fonctionnement :**
1. Vous démarrez le mode via `POST /api/shadow/start`.
2. **4 tâches asynchrones** tournent en parallèle : surveillance de l'écran, du clavier/souris, des changements d'application, et analyse des patterns.
3. Quand vous stoppez (`POST /api/shadow/stop`), le moteur cherche des **séquences d'actions répétitives** (≥3 occurrences similaires).
4. Si un pattern a une confiance > 75%, il génère un workflow automatisable.

---

## Étape 5 : Le Liquid OS (Environnement Adaptatif)

```mermaid
graph LR
    A["Activité détectée"] --> B{"Quel état cognitif ?"}
    B -->|"VSCode, Terminal"| C["💻 CODING"]
    B -->|"Figma, Adobe"| D["🎨 CREATIVE"]
    B -->|"Zoom, Teams"| E["📞 MEETING"]
    B -->|"App unique, pas de notifs"| F["🎯 FOCUS"]
    B -->|"YouTube, Spotify"| G["😌 RELAXATION"]
    
    C --> H["Dark Pro + Distractions off"]
    D --> I["Vibrant + Flexibilité max"]
    E --> J["Pro + Notes visibles"]
    F --> K["Monochrome + Tout caché"]
    G --> L["Warm + Entertainment"]
```

Quand vous appelez `POST /api/cognitive/state` avec vos applications ouvertes, le Liquid OS :
1. Analyse l'activité courante.
2. Détermine votre état cognitif (CODING, CREATIVE, FOCUS, etc.).
3. Applique des transformations visuelles adaptées (couleurs, layout, notifications).

---

## Étape 6 : Le Semantic Rewind (Mémoire Épisodique)

```mermaid
graph TB
    subgraph "Enregistrement"
        A["Capture du moment"] --> B["Screen + Apps + Texte OCR"]
        B --> C["Contexte: heure, météo, humeur"]
        C --> D["Vectorisation → embedding 768D"]
        D --> E["Stockage dans episodic_memory[]"]
    end
    
    subgraph "Recherche"
        F["'Le truc que je faisais mardi'"] --> G["Vectorisation de la requête"]
        G --> H["Comparaison cosinus avec tous les épisodes"]
        H --> I["Top 5 résultats par similarité"]
    end
    
    subgraph "Récupération"
        I --> J["recover_episode(id)"]
        J --> K["Restaurer apps + fichiers + état"]
    end
```

C'est comme une **machine à remonter le temps** pour votre bureau. Chaque "moment" est enregistré avec son contexte complet, et vous pouvez le retrouver par association d'idées plutôt que par chemin de fichier.

---

## 🔗 Flux Complet : Du Fichier au Néant et Retour

Voici le parcours complet quand vous jetez un fichier et le retrouvez plus tard :

```
1. VOUS          →  Glissez "rapport_Q2.pdf" dans ~/MOT-X_Nexus
2. WATCHER       →  Détecte le nouveau fichier (polling 2s)
3. INGEST        →  Lit le contenu, extrait les métadonnées
4. VECTORIZE     →  Convertit en vecteur 768D
5. ARCHIVE       →  Stocke tout en mémoire (semantic_database)
6. DELETE        →  Supprime le fichier du disque ✨
7. ...3 semaines plus tard...
8. VOUS          →  GET /api/nexus/search?q=rapport+trimestriel
9. SEARCH        →  Vectorise "rapport trimestriel"
10. COMPARE      →  Similarité cosinus avec tous les fichiers archivés
11. MATCH        →  rapport_Q2.pdf → score 0.85 ✅
12. RETRIEVE     →  POST /api/nexus/recover/file_xxx
13. RESTORE      →  Le fichier réapparaît dans ~/MOT-X_Nexus 🎉
```

---

## 📡 Carte des Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/status` | Statut du système |
| `GET` | `/api/analytics/dashboard` | Tableau de bord |
| `POST` | `/api/shadow/start` | Démarrer l'observation silencieuse |
| `POST` | `/api/shadow/stop` | Arrêter et générer les workflows |
| `POST` | `/api/cognitive/state` | Détecter l'état cognitif |
| `POST` | `/api/multimodal/voice` | Commande vocale |
| `GET` | `/api/memory/search?q=...` | Recherche dans la mémoire épisodique |
| `GET` | `/api/memory/recover/{id}` | Récupérer un moment passé |
| `POST` | `/api/nexus/upload` | Upload fichier au Black Hole |
| `GET` | `/api/nexus/search?q=...` | Chercher un fichier disparu |
| `POST` | `/api/nexus/recover/{id}` | Faire réapparaître un fichier |
| `WS` | `/ws/{client_id}` | WebSocket temps réel |
| `WS` | `/ws/ambient/{user_id}` | WebSocket ambiant (état cognitif) |
| `GET` | `/docs` | Swagger UI (documentation interactive) |
