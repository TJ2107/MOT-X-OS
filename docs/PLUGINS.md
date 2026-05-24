# Développement de Plugins pour MOT-X OS

L'architecture de MOT-X OS est conçue pour être modulaire et extensible via des plugins. Les plugins permettent d'ajouter de nouvelles capacités cognitives, de nouvelles interactions avec l'OS ou de nouvelles interfaces avec des services tiers sans modifier le cœur de l'application.

## Architecture

Tous les plugins se trouvent dans le dossier `src/motx_os_bridge/plugins/`.
Le cœur du système (`CognitiveOperatingLayer` et `MOTXAutomationEngine`) est conçu pour pouvoir instancier et utiliser ces modules.

### Structure d'un Plugin Type

Un plugin standard est un fichier Python (ex: `mon_plugin.py`) contenant une ou plusieurs classes qui encapsulent la logique métier.

```python
# src/motx_os_bridge/plugins/mon_plugin.py

class MonPlugin:
    def __init__(self, config=None):
        self.config = config or {}
        
    def execute_action(self, parameters):
        # Logique de l'action
        return {"status": "success", "data": "..."}
```

## Types de Plugins existants

MOT-X OS inclut déjà de nombreux plugins avancés que vous pouvez utiliser comme modèles :

1. **Plugins Cognitifs** (`cognitive_emergence.py`, `predictive_intelligence.py`) : Moteurs d'inférence avancés, génération de plans, raisonnement.
2. **Plugins d'Interface et d'Utilisateur** (`gamification_engine.py`, `multi_user_collaboration.py`, `immersive_interface.py`) : Ajoutent des éléments interactifs, de suivi ou de rendu VR/3D.
3. **Plugins Système** (`advanced_filesystem.py`, `system_info.py`) : Extensions des capacités natives de lecture, écriture et monitoring de l'OS cible.
4. **Plugins d'I/O et de Communication** (`communication.py`, `websocket_manager.py`, `web.py`) : Gèrent les flux de données entrants et sortants.

## Bonnes Pratiques de Création

1. **Isolation :** Un plugin ne doit pas dépendre fortement de l'état interne de `MOTXAutomationEngine` sauf si cette dépendance est explicitement injectée.
2. **Gestion des Erreurs :** Les actions exécutées par un plugin doivent retourner des objets ou dictionnaires décrivant le succès ou l'échec, sans faire planter l'application entière (`try...except`).
3. **Documentation :** Ajoutez des docstrings claires pour expliquer l'utilité du plugin, particulièrement si ses fonctionnalités peuvent être appelées par le module cognitif (LLM) qui s'appuiera sur cette documentation pour planifier.

## Intégration dans le flux d'exécution

Actuellement, les plugins sont importés et instanciés là où le système en a besoin. Pour qu'une nouvelle fonctionnalité soit prise en charge par le planificateur naturel (LLM), vous devez :

1. Créer le plugin dans `src/motx_os_bridge/plugins/`.
2. L'importer dans `src/motx_os_bridge/core/executor.py` ou `planner.py`.
3. Informer le système (via les prompts systèmes dans `cognitive_layer.py`) de la disponibilité de cette nouvelle action.
