"""
Parameter Form Component

Reusable parameter configuration form.

Author: Baovi Nguyen
"""

import streamlit as st
from typing import Optional, Dict


def parameter_form_component() -> Optional[Dict]:
    """
    Display parameter configuration form.
    
    Returns:
        Dictionary of parameters if form is submitted, None otherwise
    """
    with st.form("parameters"):
        st.subheader("Analysis Parameters")
        
        # Basic parameters
        col1, col2 = st.columns(2)
        
        with col1:
            sample_name = st.text_input(
                "Sample Name",
                value="sample_01",
                help="Identifier for this analysis"
            )
            
            genome = st.selectbox(
                "Genome",
                options=["hg20", "mm10"],
                format_func=lambda x: "Human (hg20)" if x == "hg20" else "Mouse (mm10)"
            )
        
        with col2:
            n_cores = st.slider(
                "CPU Cores",
                min_value=1,
                max_value=8,
                value=4
            )
            
            cell_line = st.radio(
                "Sample Type",
                options=["no", "yes"],
                format_func=lambda x: "Tumor" if x == "no" else "Cell Line",
                horizontal=True
            )
        
        # Advanced parameters
        with st.expander("Advanced Parameters"):
            ngene_chr = st.slider("Min Genes per Chr", 1, 20, 5)
            win_size = st.slider("Window Size", 10, 150, 25)
            low_dr = st.slider("LOW.DR", 0.01, 0.30, 0.05, 0.01)
            up_dr = st.slider("UP.DR", 0.01, 0.30, 0.10, 0.01)
            
            if up_dr < low_dr:
                st.error("UP.DR must be >= LOW.DR")
        
        # Submit button
        submit = st.form_submit_button("Run Analysis", type="primary")
        
        if submit:
            # Validate
            if not sample_name.replace('_', '').isalnum():
                st.error("Invalid sample name")
                return None
            
            if up_dr < low_dr:
                st.error("Invalid parameters: UP.DR < LOW.DR")
                return None
            
            # Return parameters
            return {
                'sample_name': sample_name,
                'genome': genome,
                'n_cores': n_cores,
                'cell_line': cell_line,
                'ngene_chr': ngene_chr,
                'win_size': win_size,
                'low_dr': low_dr,
                'up_dr': up_dr
            }
    
    return None

