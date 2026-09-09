"""Unit tests for GraphFrames network graph extraction."""
import pytest
from aml_app.services.data_service import data_service

def test_get_network_graph():
    account_id = 6976
    graph = data_service.get_network_graph(account_id, depth=1)
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) > 0
    # Root node exists
    root_nodes = [n for n in graph["nodes"] if n["id"] == account_id]
    assert len(root_nodes) == 1
    assert root_nodes[0]["is_root"] is True
