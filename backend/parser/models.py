"""Pydantic models for n8n workflow structure"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class N8nConnection(BaseModel):
    """Represents a connection between nodes"""
    node: str
    type: str = "main"
    index: int = 0


class N8nConnectionMap(BaseModel):
    """Maps output connections for a node"""
    main: Optional[List[List[N8nConnection]]] = None


class N8nNodeParameters(BaseModel):
    """Base class for node parameters - flexible to accept any parameters"""
    class Config:
        extra = "allow"  # Allow any additional fields


class N8nNode(BaseModel):
    """Represents an n8n node"""
    id: Optional[str] = None
    name: str
    type: str
    typeVersion: Optional[float] = None
    position: Optional[List[float]] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    credentials: Optional[Dict[str, Any]] = None
    disabled: Optional[bool] = False
    notes: Optional[str] = None
    notesInFlow: Optional[bool] = False

    class Config:
        extra = "allow"


class N8nSettings(BaseModel):
    """Workflow settings"""
    executionOrder: Optional[str] = "v1"
    saveManualExecutions: Optional[bool] = False
    saveDataErrorExecution: Optional[str] = "all"
    saveDataSuccessExecution: Optional[str] = "all"

    class Config:
        extra = "allow"


class N8nStaticData(BaseModel):
    """Static data stored in workflow"""
    class Config:
        extra = "allow"


class N8nWorkflow(BaseModel):
    """Represents a complete n8n workflow"""
    name: str
    nodes: List[N8nNode]
    connections: Dict[str, N8nConnectionMap] = Field(default_factory=dict)
    settings: Optional[N8nSettings] = None
    staticData: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    pinData: Optional[Dict[str, Any]] = None
    active: Optional[bool] = False

    class Config:
        extra = "allow"

    def get_node_by_name(self, name: str) -> Optional[N8nNode]:
        """Get a node by its name"""
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_node_inputs(self, node_name: str) -> List[str]:
        """Get all nodes that connect to this node"""
        inputs = []
        for source_name, connection_map in self.connections.items():
            if connection_map.main:
                for connection_list in connection_map.main:
                    for conn in connection_list:
                        if conn.node == node_name:
                            inputs.append(source_name)
        return inputs

    def get_node_outputs(self, node_name: str) -> List[str]:
        """Get all nodes this node connects to"""
        outputs = []
        if node_name in self.connections:
            connection_map = self.connections[node_name]
            if connection_map.main:
                for connection_list in connection_map.main:
                    for conn in connection_list:
                        outputs.append(conn.node)
        return outputs

    def get_execution_order(self) -> List[str]:
        """
        Get nodes in execution order using topological sort.
        Returns list of node names in order they should execute.
        """
        # Build adjacency list
        graph = {node.name: [] for node in self.nodes}
        in_degree = {node.name: 0 for node in self.nodes}

        for source_name, connection_map in self.connections.items():
            if connection_map.main:
                for connection_list in connection_map.main:
                    for conn in connection_list:
                        graph[source_name].append(conn.node)
                        in_degree[conn.node] += 1

        # Find all nodes with no incoming edges (starting nodes)
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_name = queue.pop(0)
            result.append(node_name)

            # Reduce in-degree for connected nodes
            for neighbor in graph[node_name]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self.nodes):
            # If we can't process all nodes, there might be a cycle
            # Add remaining nodes (best effort)
            remaining = [node.name for node in self.nodes if node.name not in result]
            result.extend(remaining)

        return result
