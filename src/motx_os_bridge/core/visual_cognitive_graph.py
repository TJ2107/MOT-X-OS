"""
Visual Cognitive Graph - Interface graphique pour visualiser le graphe cognitif en temps réel.
"""

import networkx as nx
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class NodeType(Enum):
    """Types de nœuds dans le graphe cognitif."""
    FILESYSTEM = "filesystem"
    BROWSER = "browser"
    SECURITY = "security"
    RESEARCH = "research"
    DEVELOPMENT = "development"
    MONITORING = "monitoring"
    VOICE = "voice"
    VISION = "vision"
    TASK = "task"
    MEMORY = "memory"
    USER = "user"


@dataclass
class CognitiveNode:
    """Représente un nœud dans le graphe cognitif."""
    id: str
    node_type: NodeType
    label: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    activation_count: int = 0
    last_activated: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Tuple[float, float]] = None


@dataclass
class CognitiveEdge:
    """Représente une connexion entre deux nœuds."""
    source: str
    target: str
    weight: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    activation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class VisualCognitiveGraph:
    """Graphe cognitif visuel avec NetworkX."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, CognitiveNode] = {}
        self.edges: Dict[Tuple[str, str], CognitiveEdge] = {}
        self.layout_algorithm = "spring"
        
        # Nœuds de base (système)
        self._initialize_base_nodes()
    
    def _initialize_base_nodes(self):
        """Initialise les nœuds de base du système."""
        base_nodes = [
            (NodeType.FILESYSTEM, "FileSystem", {"color": "#3498db"}),
            (NodeType.BROWSER, "Browser", {"color": "#e74c3c"}),
            (NodeType.SECURITY, "Security", {"color": "#f39c12"}),
            (NodeType.RESEARCH, "Research", {"color": "#9b59b6"}),
            (NodeType.DEVELOPMENT, "Development", {"color": "#1abc9c"}),
            (NodeType.MONITORING, "Monitoring", {"color": "#34495e"}),
            (NodeType.VOICE, "Voice", {"color": "#e91e63"}),
            (NodeType.VISION, "Vision", {"color": "#00bcd4"}),
            (NodeType.MEMORY, "Memory", {"color": "#607d8b"}),
            (NodeType.USER, "User", {"color": "#ff5722"}),
        ]
        
        for node_type, label, metadata in base_nodes:
            node_id = node_type.value
            self.add_node(node_id, node_type, label, metadata)
    
    def add_node(self, node_id: str, node_type: NodeType, label: str, 
                 metadata: Dict[str, Any] = None) -> CognitiveNode:
        """Ajoute un nœud au graphe."""
        if node_id in self.nodes:
            return self.nodes[node_id]
        
        node = CognitiveNode(
            id=node_id,
            node_type=node_type,
            label=label,
            metadata=metadata or {}
        )
        
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.metadata)
        
        return node
    
    def add_edge(self, source: str, target: str, weight: float = 1.0, 
                 metadata: Dict[str, Any] = None) -> CognitiveEdge:
        """Ajoute une connexion entre deux nœuds."""
        edge_key = (source, target)
        
        if edge_key in self.edges:
            # Renforcer la connexion existante
            self.edges[edge_key].weight += weight
            self.edges[edge_key].activation_count += 1
            self.graph[source][target]['weight'] = self.edges[edge_key].weight
            return self.edges[edge_key]
        
        edge = CognitiveEdge(
            source=source,
            target=target,
            weight=weight,
            metadata=metadata or {}
        )
        
        self.edges[edge_key] = edge
        self.graph.add_edge(source, target, weight=weight, **edge.metadata)
        
        return edge
    
    def activate_node(self, node_id: str, context: Dict[str, Any] = None):
        """Active un nœud (simule une activité cognitive)."""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        node.activation_count += 1
        node.last_activated = datetime.now().isoformat()
        
        if context:
            node.metadata.update(context)
        
        # Propagation de l'activation aux nœuds connectés
        self._propagate_activation(node_id)
    
    def _propagate_activation(self, node_id: str, depth: int = 2):
        """Propage l'activation aux nœuds voisins."""
        if depth <= 0:
            return
        
        for neighbor in self.graph.neighbors(node_id):
            if neighbor in self.nodes:
                self.nodes[neighbor].activation_count += 1
                self._propagate_activation(neighbor, depth - 1)
    
    def record_task(self, task_type: str, related_nodes: List[str] = None):
        """Enregistre une tâche et crée les connexions appropriées."""
        # Créer un nœud pour la tâche
        task_id = f"task_{len(self.nodes)}"
        task_node = self.add_node(
            task_id,
            NodeType.TASK,
            task_type,
            {"color": "#95a5a6", "shape": "diamond"}
        )
        
        # Connecter au nœud User
        self.add_edge("user", task_id, weight=1.0)
        
        # Connecter aux nœuds pertinents
        if related_nodes:
            for node_id in related_nodes:
                if node_id in self.nodes:
                    self.add_edge(task_id, node_id, weight=1.0)
        
        # Activer le nœud
        self.activate_node(task_id)
        
        return task_node
    
    def get_graph_data(self) -> Dict[str, Any]:
        """Retourne les données du graphe pour la visualisation."""
        # Calcul du layout
        if self.layout_algorithm == "spring":
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif self.layout_algorithm == "circular":
            pos = nx.circular_layout(self.graph)
        else:
            pos = nx.kamada_kawai_layout(self.graph)
        
        # Sérialisation des nœuds
        nodes_data = []
        for node_id, node in self.nodes.items():
            position = pos.get(node_id, (0, 0))
            node_data = {
                "id": node_id,
                "type": node.node_type.value,
                "label": node.label,
                "activation_count": node.activation_count,
                "last_activated": node.last_activated,
                "x": float(position[0]),
                "y": float(position[1]),
                "color": node.metadata.get("color", "#95a5a6"),
                "shape": node.metadata.get("shape", "circle")
            }
            nodes_data.append(node_data)
        
        # Sérialisation des arêtes
        edges_data = []
        for edge_key, edge in self.edges.items():
            edge_data = {
                "source": edge.source,
                "target": edge.target,
                "weight": edge.weight,
                "activation_count": edge.activation_count
            }
            edges_data.append(edge_data)
        
        # Statistiques
        stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "most_active_node": max(self.nodes.values(), key=lambda n: n.activation_count).label if self.nodes else None,
            "strongest_connection": max(self.edges.values(), key=lambda e: e.weight).source if self.edges else None
        }
        
        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "stats": stats,
            "layout": self.layout_algorithm
        }
    
    def export_graph(self, filepath: str):
        """Exporte le graphe en JSON."""
        data = self.get_graph_data()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_graph(self, filepath: str):
        """Importe un graphe depuis JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruction du graphe
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        
        for node_data in data["nodes"]:
            node = CognitiveNode(
                id=node_data["id"],
                node_type=NodeType(node_data["type"]),
                label=node_data["label"],
                activation_count=node_data["activation_count"],
                last_activated=node_data["last_activated"],
                metadata={"color": node_data["color"], "shape": node_data["shape"]}
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.metadata)
        
        for edge_data in data["edges"]:
            edge = CognitiveEdge(
                source=edge_data["source"],
                target=edge_data["target"],
                weight=edge_data["weight"],
                activation_count=edge_data["activation_count"]
            )
            self.edges[(edge.source, edge.target)] = edge
            self.graph.add_edge(edge.source, edge.target, weight=edge.weight)
    
    def set_layout_algorithm(self, algorithm: str):
        """Change l'algorithme de layout."""
        self.layout_algorithm = algorithm
    
    def get_node_insights(self, node_id: str) -> Dict[str, Any]:
        """Retourne des insights sur un nœud spécifique."""
        if node_id not in self.nodes:
            return {"error": "Node not found"}
        
        node = self.nodes[node_id]
        
        # Connexions entrantes/sortantes
        in_degree = self.graph.in_degree(node_id)
        out_degree = self.graph.out_degree(node_id)
        
        # Nœuds fortement connectés
        neighbors = list(self.graph.neighbors(node_id))
        
        return {
            "node": {
                "id": node.id,
                "type": node.node_type.value,
                "label": node.label,
                "activation_count": node.activation_count,
                "last_activated": node.last_activated
            },
            "connections": {
                "in_degree": in_degree,
                "out_degree": out_degree,
                "total_neighbors": len(neighbors),
                "neighbors": neighbors[:10]  # Limiter à 10
            },
            "importance": in_degree + out_degree
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Retourne l'état de santé du système cognitif."""
        if not self.nodes:
            return {"status": "empty", "message": "No cognitive data yet"}
        
        # Distribution des activations
        total_activations = sum(n.activation_count for n in self.nodes.values())
        avg_activations = total_activations / len(self.nodes) if self.nodes else 0
        
        # Densité du graphe
        density = nx.density(self.graph)
        
        # Composantes connectées
        components = nx.number_weakly_connected_components(self.graph)
        
        return {
            "status": "healthy" if density > 0.1 else "developing",
            "total_activations": total_activations,
            "average_activations": avg_activations,
            "graph_density": density,
            "connected_components": components,
            "cognitive_complexity": len(self.nodes) * len(self.edges)
        }
