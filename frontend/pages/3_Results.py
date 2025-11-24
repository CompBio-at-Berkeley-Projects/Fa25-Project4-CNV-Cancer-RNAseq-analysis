"""
Results Display Page

Visualizes current and historical analysis results.

Author: Baovi Nguyen / Hanson Wen
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.result_parser import parse_copykat_results

st.title("📊 Analysis Results")

# Get all result directories
results_dir = project_root / "backend" / "results"
if results_dir.exists():
    result_folders = sorted([d for d in results_dir.iterdir() if d.is_dir()],
                          key=lambda x: x.stat().st_mtime, reverse=True)
else:
    result_folders = []

# Check if there are any results
if not result_folders and not st.session_state.get('results'):
    st.warning("⚠️ No results available yet")
    st.info("Run an analysis on the **Configure** page first")
    st.stop()

# Sidebar for selecting result to view
with st.sidebar:
    st.header("Select Analysis Run")

    if result_folders:
        # Add current session result if it exists
        options = []
        if st.session_state.get('results'):
            options.append("Current Session")

        # Add historical results
        for folder in result_folders:
            folder_name = folder.name
            mtime = datetime.fromtimestamp(folder.stat().st_mtime)
            options.append(f"{folder_name} ({mtime.strftime('%Y-%m-%d %H:%M')})")

        selected_option = st.selectbox("Analysis Run", options, index=0)

        # Parse selected result
        if selected_option == "Current Session":
            results = st.session_state.results
            result_source = "Current Session"
        else:
            # Extract folder name from option
            folder_name = selected_option.split(" (")[0]
            selected_folder = results_dir / folder_name
            try:
                results = parse_copykat_results(str(selected_folder))
                result_source = folder_name
            except Exception as e:
                st.error(f"Error loading results: {str(e)}")
                st.stop()
    else:
        # Only current session available
        results = st.session_state.results
        result_source = "Current Session"
        st.info("📍 Viewing current session results")

# Display results
if not results:
    st.error("No results data available")
    st.stop()

st.success(f"✅ Displaying results: **{result_source}**")

# Summary Statistics
st.subheader("Summary Statistics")

summary = results.get('summary', {})
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Cells", summary.get('n_cells', 0))
with col2:
    st.metric("Aneuploid", summary.get('n_aneuploid', 0))
with col3:
    st.metric("Diploid", summary.get('n_diploid', 0))
with col4:
    aneuploid_pct = summary.get('aneuploid_fraction', 0) * 100
    st.metric("Aneuploid %", f"{aneuploid_pct:.1f}%")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Heatmap", "📋 Predictions", "📊 Charts", "ℹ️ Info"])

with tab1:
    st.subheader("CNV Heatmap")

    file_paths = results.get('file_paths', {})
    if 'heatmap' in file_paths and Path(file_paths['heatmap']).exists():
        st.image(file_paths['heatmap'], width='stretch',
                caption="Copy Number Variation Heatmap - Red: amplification, Blue: deletion")
    else:
        st.warning("Heatmap not found")
        st.markdown("""
        The CNV heatmap shows:
        - **Rows**: Genomic positions (chromosomes)
        - **Columns**: Individual cells
        - **Colors**: Copy number state (red = gain, blue = loss)
        """)

with tab2:
    st.subheader("Cell Classifications")

    predictions = results.get('predictions')
    if predictions is not None and not predictions.empty:
        # Add filtering
        col_a, col_b = st.columns(2)
        with col_a:
            filter_class = st.multiselect(
                "Filter by classification",
                options=predictions['copykat.pred'].unique() if 'copykat.pred' in predictions.columns else [],
                default=predictions['copykat.pred'].unique() if 'copykat.pred' in predictions.columns else []
            )

        # Apply filter
        if filter_class:
            filtered_df = predictions[predictions['copykat.pred'].isin(filter_class)]
        else:
            filtered_df = predictions

        # Display table
        st.dataframe(
            filtered_df,
            width='stretch',
            height=400
        )

        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Predictions (CSV)",
            data=csv,
            file_name=f"predictions_{result_source}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Predictions data not available")

with tab3:
    st.subheader("Classification Distribution")

    predictions = results.get('predictions')
    if predictions is not None and not predictions.empty and 'copykat.pred' in predictions.columns:
        # Bar chart
        class_counts = predictions['copykat.pred'].value_counts()
        st.bar_chart(class_counts)

        # Pie chart data
        st.markdown("### Breakdown")
        for class_name, count in class_counts.items():
            pct = (count / len(predictions)) * 100
            st.write(f"**{class_name}**: {count} cells ({pct:.1f}%)")
    else:
        st.warning("No classification data available for visualization")

with tab4:
    st.subheader("Analysis Information")

    # Runtime info
    if 'runtime' in results:
        st.metric("Runtime", f"{results['runtime']:.1f} minutes")

    # Output directory
    if 'output_dir' in results:
        st.info(f"📁 Output directory: `{results['output_dir']}`")

    # Parameters used
    st.markdown("### Parameters Used")
    if st.session_state.get('analysis_params'):
        params_df = pd.DataFrame([
            {"Parameter": k, "Value": str(v)}
            for k, v in st.session_state.analysis_params.items()
        ])
        st.dataframe(params_df, width='stretch', hide_index=True)
    else:
        st.write("No parameter information available")

    # File paths
    st.markdown("### Output Files")
    file_paths = results.get('file_paths', {})
    for file_type, file_path in file_paths.items():
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size / 1024  # KB
            st.write(f"- **{file_type}**: `{Path(file_path).name}` ({file_size:.1f} KB)")

st.markdown("---")
st.info("👉 Go to the **Download** page to export all results")
