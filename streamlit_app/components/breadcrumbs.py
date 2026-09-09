"""Breadcrumbs navigation component."""
import streamlit as st
from typing import List, Tuple

def render_breadcrumbs(crumbs: List[Tuple[str, str]]):
    """Render interactive breadcrumb trace.
    Args:
        crumbs: List of (label, target_page_or_empty)
    """
    items = []
    for i, (label, target) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            items.append(f'<span style="font-weight: 700; color: #1E3A8A;">{label}</span>')
        else:
            items.append(f'<span style="color: #68707A;">{label}</span>')
    
    html = f"""
    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.84rem; margin-bottom: 16px; padding: 4px 0;">
        {' <span style="color: #9AA0A6;">/</span> '.join(items)}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
