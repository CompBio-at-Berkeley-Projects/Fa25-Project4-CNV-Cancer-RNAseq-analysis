"""
Simple CopyKAT Analysis App

Minimal Streamlit app that runs CopyKAT analysis.
Single-page design for quick testing and development.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.api.r_executor import run_copykat_analysis
from backend.api.result_parser import parse_copykat_results
from shared.constants import SUPPORTED_GENOMES, EXAMPLE_DATASETS

# Page config
st.set_page_config(
    page_title="CopyKAT Analysis",
    page_icon="🧬",
    layout="wide"
)

# Title
st.title("🧬 CopyKAT CNV Analysis")
st.markdown("Analyze copy number variations from single-cell RNA-seq data")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")

    # File selection
    use_example = st.checkbox("Use example dataset", value=True)

    if use_example:
        dataset = st.selectbox(
            "Select dataset",
            options=list(EXAMPLE_DATASETS.keys()),
            format_func=lambda x: EXAMPLE_DATASETS[x]['name']
        )
        input_file = str(project_root / EXAMPLE_DATASETS[dataset]['path'])
        st.info(f"Cells: {EXAMPLE_DATASETS[dataset]['n_cells']}")
    else:
        uploaded_file = st.file_uploader(
            "Upload expression matrix",
            type=['txt', 'csv', 'tsv', 'gz'],
            help="Upload a gene x cell expression matrix"
        )
        if uploaded_file:
            # Save uploaded file
            temp_path = project_root / "backend" / "data" / "uploaded" / uploaded_file.name
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            input_file = str(temp_path)
            st.success(f"Uploaded: {uploaded_file.name}")
        else:
            input_file = None

    # Parameters
    st.divider()
    sample_name = st.text_input("Sample name", value="analysis")
    genome = st.selectbox("Genome", options=SUPPORTED_GENOMES)
    n_cores = st.slider("CPU cores", min_value=1, max_value=8, value=2)

    # Run button
    st.divider()
    run_analysis = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# Main content area
if run_analysis and input_file:
    with st.spinner("Running CopyKAT analysis... This may take 2-5 minutes"):
        # Prepare parameters
        params = {
            'input_file': input_file,
            'sample_name': sample_name,
            'output_dir': str(project_root / "backend" / "results"),
            'genome': genome,
            'n_cores': n_cores
        }

        # Run analysis
        result = run_copykat_analysis(params)

        if result['success']:
            st.success(f"✅ Analysis complete! Runtime: {result.get('runtime_minutes', 0):.1f} minutes")

            # Parse results
            try:
                parsed_results = parse_copykat_results(result['output_dir'])
                st.session_state.results = parsed_results
                st.session_state.analysis_complete = True
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing results: {str(e)}")
        else:
            st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            with st.expander("Error details"):
                st.code(result.get('stderr', 'No error details available'))

elif run_analysis and not input_file:
    st.warning("⚠️ Please select a dataset or upload a file first")

# Display results
if st.session_state.analysis_complete and st.session_state.results:
    results = st.session_state.results

    st.header("Analysis Results")

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cells", results['summary']['n_cells'])
    with col2:
        st.metric("Aneuploid", results['summary']['n_aneuploid'])
    with col3:
        st.metric("Diploid", results['summary']['n_diploid'])
    with col4:
        aneuploid_pct = results['summary']['aneuploid_fraction'] * 100
        st.metric("Aneuploid %", f"{aneuploid_pct:.1f}%")

    # Visualizations
    tab1, tab2, tab3 = st.tabs(["📊 Heatmap", "📋 Predictions", "📁 Files"])

    with tab1:
        st.subheader("CNV Heatmap")
        if 'heatmap' in results['file_paths']:
            st.image(results['file_paths']['heatmap'], use_column_width=True)
        else:
            st.warning("Heatmap not found")

    with tab2:
        st.subheader("Cell Classifications")
        if results['predictions'] is not None:
            # Display predictions table
            st.dataframe(
                results['predictions'],
                use_container_width=True,
                height=400
            )

            # Download button
            csv = results['predictions'].to_csv(index=False)
            st.download_button(
                label="📥 Download Predictions (CSV)",
                data=csv,
                file_name=f"{sample_name}_predictions.csv",
                mime="text/csv"
            )

            # Classification pie chart
            if 'copykat.pred' in results['predictions'].columns:
                st.subheader("Classification Distribution")
                class_counts = results['predictions']['copykat.pred'].value_counts()
                st.bar_chart(class_counts)
        else:
            st.warning("Predictions data not available")

    with tab3:
        st.subheader("Output Files")
        for file_type, file_path in results['file_paths'].items():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.text(f"{file_type}: {Path(file_path).name}")
            with col_b:
                if Path(file_path).exists():
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="Download",
                            data=f,
                            file_name=Path(file_path).name,
                            key=file_type
                        )

    # Clear results button
    if st.button("🔄 New Analysis"):
        st.session_state.results = None
        st.session_state.analysis_complete = False
        st.rerun()

else:
    # Welcome message
    st.info("""
    👋 Welcome to the CopyKAT CNV Analysis tool!

    **Get started:**
    1. Select an example dataset or upload your own file
    2. Configure analysis parameters in the sidebar
    3. Click "Run Analysis" to start

    **Example datasets include:**
    - Glioblastoma (~400 cells, ~1 minute runtime)
    - Melanoma (~4000 cells, ~15 minute runtime)
    """)

    # Show example data info
    with st.expander("ℹ️ About the example datasets"):
        for key, info in EXAMPLE_DATASETS.items():
            st.markdown(f"**{info['name']}**")
            st.markdown(f"- Cells: {info['n_cells']}")
            st.markdown(f"- Genes: {info['n_genes']}")
            st.markdown(f"- Genome: {info['genome']}")
            st.markdown("")
