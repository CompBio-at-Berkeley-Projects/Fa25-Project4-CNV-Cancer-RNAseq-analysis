"""
Configuration Page

Parameter configuration and analysis execution.

Author: Baovi Nguyen
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# TODO: Import backend API when implemented
# from backend.api.r_executor import run_copykat_analysis

st.title("⚙️ Configure Analysis")

# Check if file is uploaded
if not st.session_state.get('uploaded_file'):
    st.warning("⚠️ Please upload a file first on the **Upload** page")
    st.stop()

st.success("✅ File uploaded and ready for analysis")

st.markdown("""
Configure the CopyKAT analysis parameters below. Default values work well for most datasets.
""")

# Parameter form
with st.form("analysis_parameters"):
    st.subheader("Basic Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sample_name = st.text_input(
            "Sample Name",
            value="sample_001",
            help="Identifier for this analysis (alphanumeric only)"
        )
        
        genome = st.selectbox(
            "Reference Genome",
            options=["hg20", "mm10"],
            index=0,
            format_func=lambda x: "Human (hg20)" if x == "hg20" else "Mouse (mm10)",
            help="Select the organism for your sample"
        )
        
        cell_line = st.radio(
            "Sample Type",
            options=["no", "yes"],
            format_func=lambda x: "Tumor Sample" if x == "no" else "Pure Cell Line",
            help="Choose 'Tumor Sample' for patient biopsies, 'Pure Cell Line' for established cell lines",
            horizontal=True
        )
    
    with col2:
        n_cores = st.slider(
            "CPU Cores",
            min_value=1,
            max_value=8,
            value=4,
            help="Number of CPU cores to use (more = faster)"
        )
        
        distance = st.selectbox(
            "Distance Metric",
            options=["euclidean", "pearson", "spearman"],
            index=0,
            help="Method for measuring cell similarity"
        )
    
    # Advanced parameters
    with st.expander("🔧 Advanced Parameters"):
        st.markdown("*Adjust these only if you understand their impact*")
        
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            ngene_chr = st.slider(
                "Min Genes per Chromosome",
                min_value=1,
                max_value=20,
                value=5,
                help="Cells must have this many genes detected on each chromosome"
            )
            
            win_size = st.slider(
                "Window Size",
                min_value=10,
                max_value=150,
                value=25,
                step=5,
                help="Number of genes per window for segmentation"
            )
            
            ks_cut = st.select_slider(
                "Segmentation Sensitivity (KS.cut)",
                options=[0.05, 0.1, 0.15, 0.2, 0.3, 0.4],
                value=0.1,
                help="Lower = more sensitive (more breakpoints)"
            )
        
        with adv_col2:
            low_dr = st.slider(
                "LOW.DR (Smoothing)",
                min_value=0.01,
                max_value=0.30,
                value=0.05,
                step=0.01,
                format="%.2f",
                help="Minimum fraction of cells expressing a gene (for smoothing)"
            )
            
            up_dr = st.slider(
                "UP.DR (Segmentation)",
                min_value=0.01,
                max_value=0.30,
                value=0.10,
                step=0.01,
                format="%.2f",
                help="Minimum fraction for segmentation (must be >= LOW.DR)"
            )
            
            # Validate UP.DR >= LOW.DR
            if up_dr < low_dr:
                st.error("⚠️ UP.DR must be greater than or equal to LOW.DR")
            
            plot_genes = st.checkbox(
                "Show gene labels in heatmap",
                value=True,
                help="May slow down rendering for large datasets"
            )
    
    # Submit button
    st.markdown("---")
    submit = st.form_submit_button(
        "🚀 Run Analysis",
        type="primary",
        use_container_width=True
    )
    
    if submit:
        # Validate parameters
        if not sample_name or not sample_name.replace('_', '').isalnum():
            st.error("Sample name must be alphanumeric (underscores allowed)")
            st.stop()
        
        if up_dr < low_dr:
            st.error("UP.DR must be >= LOW.DR. Please adjust parameters.")
            st.stop()
        
        # Save parameters to session state
        st.session_state.analysis_params = {
            'sample_name': sample_name,
            'genome': genome,
            'cell_line': cell_line,
            'n_cores': n_cores,
            'distance': distance,
            'ngene_chr': ngene_chr,
            'win_size': win_size,
            'ks_cut': ks_cut,
            'low_dr': low_dr,
            'up_dr': up_dr,
            'plot_genes': plot_genes
        }
        
        # Run analysis
        st.session_state.analysis_running = True
        
        with st.spinner("Running CopyKAT analysis... This may take 5-15 minutes."):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Step 1/5: Preparing data...")
            progress_bar.progress(0.1)
            
            # TODO: Implement backend call when API is ready
            # try:
            #     result = run_copykat_analysis(st.session_state.analysis_params)
            #     
            #     if result['success']:
            #         st.session_state.results = result
            #         st.success("✅ Analysis complete!")
            #         st.info("👉 Go to the **Results** page to view outputs")
            #     else:
            #         st.error(f"Analysis failed: {result['error']}")
            # except Exception as e:
            #     st.error(f"Error running analysis: {str(e)}")
            
            # Placeholder for now
            status_text.text("Step 5/5: Complete!")
            progress_bar.progress(1.0)
            st.warning("⚠️ Backend integration pending. This is a placeholder.")
            st.info("When implemented, results will appear in the Results page.")
        
        st.session_state.analysis_running = False

# Parameter reference
with st.expander("📖 Parameter Guide"):
    st.markdown("""
    **Sample Name**: Unique identifier for your analysis
    
    **Reference Genome**: 
    - hg20 for human samples
    - mm10 for mouse samples
    
    **Sample Type**:
    - Tumor Sample: Mixed population (tumor + normal cells)
    - Pure Cell Line: 100% cancer cells
    
    **CPU Cores**: More cores = faster analysis (use 4-8 for best performance)
    
    **Distance Metric**:
    - Euclidean: Standard (recommended)
    - Pearson: Good for batch effects
    - Spearman: Robust to outliers
    
    **Advanced Parameters**: See [Parameter Reference](../docs/03_PARAMETERS_REFERENCE.md) for details
    """)

