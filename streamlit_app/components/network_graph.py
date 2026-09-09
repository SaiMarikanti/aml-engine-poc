"""Interactive Network Graph Component using PyVis."""
import streamlit.components.v1 as components
from typing import Dict, Any, List
from pyvis.network import Network
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
        risk_score = n.get("risk_score", 0.1)
        risk_lvl = score_to_risk_level(risk_score)
        color = RISK_COLORS[risk_lvl]
        is_root = n.get("is_root", False)
        
        size = 28 if is_root else 18
        border_color = "#1E3A8A" if is_root else "#64748B"
        
        tooltip = (
            f"Account: ACC_{acc_id}\n"
            f"Risk Score: {risk_score:.2f} ({risk_lvl.value})\n"
            f"Country: {n.get('country', 'Unknown')}\n"
            f"Type: {n.get('type', 'Individual')}\n"
            f"Open Alerts: {n.get('open_alerts', 0)}"
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
        count = e.get("count", 1)
        vol = e.get("volume", 0.0)
        has_alert = e.get("has_alert", False) or count >= 5
        
        edge_color = "#DC2626" if has_alert else "#94A3B8"
        edge_width = min(1 + count, 6)
        
        tooltip = f"Transfers: {count}\nTotal Volume: ₹{vol:,.2f}"
        
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
