import json

def build_execution_graph(actions: list) -> dict:
    """Return a simple graph representation.
    For demo purposes we just return a dict with a list of actions and a placeholder for dependencies.
    Each action dict is expected to have 'type' and 'details' keys.
    """
    # In a real implementation we would compute DAG edges based on action prerequisites.
    # Here we simply package the actions in order.
    graph = {
        "nodes": [],
        "edges": [],
        "actions": actions,
    }
    for idx, action in enumerate(actions):
        node = {
            "id": idx,
            "type": action.get("type"),
            "details": action.get("details", {}),
            "status": "pending"
        }
        graph["nodes"].append(node)
        # No explicit edges in this simple version.
    return json.dumps(graph)
