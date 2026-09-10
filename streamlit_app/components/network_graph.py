"""Interactive Network Graph Component using PyVis."""
import streamlit.components.v1 as components
from typing import Dict, Any, List
from pyvis.network import Network
try:
    from utils.formatting import score_to_risk_level
    from utils.constants import RISK_COLORS
except (ImportError, ModuleNotFoundError):
    from aml_app.utils.formatting import score_to_risk_level
    from aml_app.utils.constants import RISK_COLORS


def render_pyvis_network(graph_data: Dict[str, Any], height: int = 580):
    """Render an interactive directed graph with physics using PyVis."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    if not nodes:
        components.html(
            '<div style="text-align: center; padding: 40px; color: #68707A; font-family: Inter, sans-serif;">'
            'No network graph connections discovered for this account at current depth.</div>',
            height=120
        )
        return

    net = Network(
        height=f"{height}px", 
        width="100%", 
        bgcolor="#E8ECF1", 
        font_color="#20242A", 
        directed=True
    )

    # Physics configuration for clean layout
    net.set_options("""
    {
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 4,
        "font": {
          "size": 13,
          "face": "Inter, sans-serif",
          "color": "#20242A"
        }
      },
      "edges": {
        "color": {
          "color": "#94A3B8",
          "highlight": "#1E3A8A"
        },
        "smooth": {
          "type": "continuous"
        },
        "arrows": {
          "to": { "enabled": true, "scaleFactor": 0.8 }
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": { "iterations": 150 }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    # Add Nodes
    for n in nodes:
        acc_id = n["id"]
        is_root = n.get("is_root", False)
        is_fraud = n.get("is_fraud", False)
        tot_deg = n.get("total_degree", 0)
        in_deg = n.get("in_degree", 0)
        out_deg = n.get("out_degree", 0)

        if is_root:
            color = "#1E3A8A"  # Deep Indigo (Selected Focus Account)
            border_color = "#0F172A"
            size = 28
        elif is_fraud:
            color = "#DC2626"  # Red (Confirmed Fraud Tag in Silver)
            border_color = "#991B1B"
            size = 22
        else:
            color = "#7C3AED"  # Purple (Precomputed GraphFrames Cycle Vertex)
            border_color = "#5B21B6"
            size = 18

        tooltip = (
            f"Account: ACC_{acc_id}\n"
            f"Role: {'Focus Account' if is_root else ('Confirmed Fraud Participant' if is_fraud else 'Cycle Participant')}\n"
            f"Total Degree: {tot_deg} (In: {in_deg}, Out: {out_deg})\n"
            f"Country: {n.get('country', 'US')}\n"
            f"Type: {n.get('type', 'I')}"
        )

        net.add_node(
            acc_id,
            label=f"ACC_{acc_id}" + (" (Focus)" if is_root else ""),
            title=tooltip,
            color={"background": color, "border": border_color},
            size=size,
            shape="dot"
        )

    # Add Edges
    for e in edges:
        src = e["source"]
        dst = e["target"]
        cid = e.get("cycle_id", "")
        rule = e.get("rule", "CYCLE_DETECTION")
        score = e.get("score", 0.0)

        edge_color = "#7C3AED" if cid else "#94A3B8"
        edge_width = 3 if cid else 1

        tooltip = f"Rule: {rule}\nCycle ID: {cid}\nGraph Score: {score}" if cid else f"Directed Edge: ACC_{src} -> ACC_{dst}"

        net.add_edge(
            src, 
            dst, 
            title=tooltip, 
            color=edge_color, 
            width=edge_width
        )

    try:
        html_str = net.generate_html()
        components.html(html_str, height=height + 20)
    except Exception as exc:
        components.html(f"<div style='color: red;'>Failed to render network graph: {str(exc)}</div>", height=100)
