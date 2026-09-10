"""Network Analysis View - GraphFrames Visualization via PyVis."""
import streamlit as st
try:
    from services.data_service import data_service
    from components.network_graph import render_pyvis_network
    from utils.formatting import render_risk_badge
except (ImportError, ModuleNotFoundError):
    from aml_app.services.data_service import data_service
    from aml_app.components.network_graph import render_pyvis_network
    from aml_app.utils.formatting import render_risk_badge


def render_network():
    pages_map = st.session_state.get("_pages_map", {})
    
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #1E3A8A;">GRAPH NETWORK INVESTIGATION</h2>
            <p style="margin: 4px 0 0 0; color: #68707A; font-size: 0.9rem;">
                Visual graph intelligence rendering precomputed Databricks GraphFrames topologies, circular cycles, and counterparty clusters via interactive PyVis.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Search, Depth, and Risk Filter Controls Card
    st.markdown('<div class="neo-card" style="padding: 18px 22px; margin-bottom: 20px;">', unsafe_allow_html=True)
    c_acc, c_depth, c_risk, c_btn = st.columns([2, 1.2, 1.2, 1.2])
    
    with c_acc:
        current_focus = st.session_state.get("selected_network_account", 6976)
        acc_str = st.text_input("Root Account Vertex (ID)", value=str(current_focus), placeholder="e.g. 6976, 9739, 5776")
        
    with c_depth:
        depth = st.radio("Traversal Depth", [1, 2, 3], index=0, horizontal=True)

    with c_risk:
        min_risk_filter = st.selectbox("Risk Filter", ["All Nodes", "Medium+ (≥0.4)", "High+ (≥0.65)"], index=0)
        
    with c_btn:
        st.write("")
        st.write("")
        load_btn = st.button("RENDER GRAPH", type="primary", use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    if not acc_str.strip().isdigit():
        st.warning("Please enter a valid numeric account ID.")
        return

    root_id = int(acc_str.strip())
    st.session_state.selected_network_account = root_id

    # Fetch precomputed GraphFrames subgraph from SQL Warehouse
    with st.spinner(f"Querying Databricks GraphFrames topology for ACC_{root_id} (depth {depth})..."):
        try:
            graph_data = data_service.get_network_graph(root_id, depth=depth)
        except Exception as e:
            st.error(f"Failed to fetch network graph: {e}")
            graph_data = {"nodes": [], "edges": []}

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # Filter nodes by risk if requested
    if min_risk_filter == "High+ (≥0.65)":
        valid_ids = {n["id"] for n in nodes if n.get("risk_score", 0) >= 0.65 or n["id"] == root_id}
        nodes = [n for n in nodes if n["id"] in valid_ids]
        edges = [e for e in edges if e["source"] in valid_ids and e["target"] in valid_ids]
    elif min_risk_filter == "Medium+ (≥0.4)":
        valid_ids = {n["id"] for n in nodes if n.get("risk_score", 0) >= 0.40 or n["id"] == root_id}
        nodes = [n for n in nodes if n["id"] in valid_ids]
        edges = [e for e in edges if e["source"] in valid_ids and e["target"] in valid_ids]

    # Top summary bar
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown(f'<div class="neo-card-sm"><b>Discovered Vertices:</b> {len(nodes)}</div>', unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f'<div class="neo-card-sm"><b>Transfer Edges:</b> {len(edges)}</div>', unsafe_allow_html=True)
    with col_stat3:
        high_risk_nodes = sum(1 for n in nodes if n.get('risk_score', 0) >= 0.65)
        st.markdown(f'<div class="neo-card-sm"><b>High-Risk Vertices:</b> <span style="color: #DC2626; font-weight:700;">{high_risk_nodes}</span></div>', unsafe_allow_html=True)
    with col_stat4:
        total_vol = sum(e.get('volume', 0) for e in edges)
        st.markdown(f'<div class="neo-card-sm"><b>Connected Volume:</b> ₹{total_vol:,.0f}</div>', unsafe_allow_html=True)

    # Graph Canvas Card & Node Inspector
    col_graph, col_inspect = st.columns([3, 1])

    with col_graph:
        st.markdown('<div class="neo-card" style="padding: 14px;">', unsafe_allow_html=True)
        st.markdown("""
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #68707A; margin-bottom: 8px;">
                <span><b>Interactive Physics Canvas</b> (Drag nodes, scroll to zoom)</span>
                <span>Legend: <span style="color: #059669;">● Low</span> <span style="color: #D97706;">● Med</span> <span style="color: #DC2626;">● High</span> <span style="color: #991B1B;">● Critical</span></span>
            </div>
        """, unsafe_allow_html=True)
        render_pyvis_network({"nodes": nodes, "edges": edges}, height=540)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_inspect:
        st.markdown('<div class="neo-card" style="padding: 18px 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 12px;">VERTEX INSPECTOR</div>', unsafe_allow_html=True)
        
        node_ids = [n["id"] for n in nodes]
        if node_ids:
            selected_node_id = st.selectbox("Inspect Connected Vertex", node_ids, index=0)
            target_node = next((n for n in nodes if n["id"] == selected_node_id), None)
            
            if target_node:
                r_score = target_node.get("risk_score", 0.1)
                r_tier = "CRITICAL" if r_score >= 0.85 else ("HIGH" if r_score >= 0.65 else ("MEDIUM" if r_score >= 0.40 else "LOW"))
                
                st.markdown(f"""
                    <div style="margin-top: 10px; font-size: 0.88rem;">
                        <div style="font-weight: 800; font-size: 1.1rem; color: #20242A;">ACC_{selected_node_id}</div>
                        <div style="margin: 6px 0;">{render_risk_badge(r_tier)}</div>
                        <p style="color: #4B5563; margin: 4px 0;">Risk Score: <b>{r_score:.2f}</b></p>
                        <p style="color: #4B5563; margin: 4px 0;">Country: <b>{target_node.get('country', 'US')}</b></p>
                        <p style="color: #4B5563; margin: 4px 0;">Account Type: <b>{target_node.get('type', 'I')}</b></p>
                        <p style="color: #4B5563; margin: 4px 0;">Active Alerts: <b>{target_node.get('open_alerts', 0)}</b></p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button(f"Open Profile ACC_{selected_node_id}", use_container_width=True, type="primary"):
                    st.session_state.selected_account = selected_node_id
                    if "Accounts" in pages_map:
                        st.switch_page(pages_map["Accounts"])
                    
                if st.button("Set as Root Graph Focus", use_container_width=True):
                    st.session_state.selected_network_account = selected_node_id
                    st.rerun()
        else:
            st.caption("No vertices to inspect.")
            
        st.markdown('</div>', unsafe_allow_html=True)
