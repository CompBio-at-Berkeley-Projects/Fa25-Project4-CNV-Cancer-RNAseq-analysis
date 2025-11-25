"""
Download Page

Handles result downloads for current and historical analyses.

Author: Baovi Nguyen / Hanson Wen
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import zipfile
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.result_parser import parse_copykat_results

st.title("💾 Download Results")

# Get all result directories
results_dir = project_root / "backend" / "results"
if results_dir.exists():
    result_folders = sorted([d for d in results_dir.iterdir() if d.is_dir()],
                          key=lambda x: x.stat().st_mtime, reverse=True)
else:
    result_folders = []

# Check if there are any results
if not result_folders and not st.session_state.get('results'):
    st.warning("⚠️ No results available to download")
    st.info("Complete an analysis on the **Configure** page first")
    st.stop()

# Sidebar for selecting result to download
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

# Display results info
if not results:
    st.error("No results data available")
    st.stop()

st.success(f"✅ Download results: **{result_source}**")

# Summary info
summary = results.get('summary', {})
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cells", summary.get('n_cells', 0))
with col2:
    st.metric("Aneuploid", summary.get('n_aneuploid', 0))
with col3:
    st.metric("Diploid", summary.get('n_diploid', 0))

st.markdown("---")

# File downloads section
st.subheader("📁 Individual Files")

file_paths = results.get('file_paths', {})

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Primary Outputs**")

    # Predictions
    if 'predictions' in file_paths and Path(file_paths['predictions']).exists():
        with open(file_paths['predictions'], 'rb') as f:
            st.download_button(
                label="📄 Cell Classifications",
                data=f.read(),
                file_name=f"{result_source}_predictions.txt",
                mime="text/plain",
                help="Cell-level classification results",
                width='stretch'
            )

    # CNV results
    if 'cna_results' in file_paths and Path(file_paths['cna_results']).exists():
        with open(file_paths['cna_results'], 'rb') as f:
            st.download_button(
                label="📄 CNV Segments",
                data=f.read(),
                file_name=f"{result_source}_CNA_results.txt",
                mime="text/plain",
                help="Segment-level CNV calls",
                width='stretch'
            )

    # Heatmap
    if 'heatmap' in file_paths and Path(file_paths['heatmap']).exists():
        with open(file_paths['heatmap'], 'rb') as f:
            st.download_button(
                label="🖼️ CNV Heatmap (JPEG)",
                data=f.read(),
                file_name=f"{result_source}_heatmap.jpeg",
                mime="image/jpeg",
                help="CNV heatmap visualization",
                width='stretch'
            )

with col2:
    st.markdown("**Additional Outputs**")

    # Check for additional files
    output_dir = Path(results.get('output_dir', '')) if 'output_dir' in results else None

    if output_dir and output_dir.exists():
        # Raw CNV matrix
        raw_files = list(output_dir.glob("*_CNA_raw_results_gene_by_cell.txt"))
        if raw_files:
            with open(raw_files[0], 'rb') as f:
                st.download_button(
                    label="📄 Gene-level CNV Matrix",
                    data=f.read(),
                    file_name=f"{result_source}_gene_by_cell.txt",
                    mime="text/plain",
                    help="Gene-by-cell CNV matrix",
                    width='stretch'
                )

        # PDF heatmap with genes
        pdf_files = list(output_dir.glob("*_with_genes_heatmap.pdf"))
        if pdf_files:
            with open(pdf_files[0], 'rb') as f:
                st.download_button(
                    label="📊 Detailed Heatmap (PDF)",
                    data=f.read(),
                    file_name=f"{result_source}_detailed_heatmap.pdf",
                    mime="application/pdf",
                    help="High-resolution heatmap with gene labels",
                    width='stretch'
                )

        # RDS file (R data)
        rds_files = list(output_dir.glob("*_clustering_results.rds"))
        if rds_files:
            with open(rds_files[0], 'rb') as f:
                st.download_button(
                    label="🔬 Clustering Data (RDS)",
                    data=f.read(),
                    file_name=f"{result_source}_clustering.rds",
                    mime="application/octet-stream",
                    help="R data object for further analysis",
                    width='stretch'
                )

st.markdown("---")

# Batch download as ZIP
st.subheader("📦 Batch Download")

if output_dir and output_dir.exists():
    st.markdown("Download all result files in a single archive:")

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_type, file_path in file_paths.items():
            if Path(file_path).exists():
                zip_file.write(file_path, Path(file_path).name)

        # Add any additional files in output directory
        if output_dir.exists():
            for file in output_dir.glob("*"):
                if file.is_file() and str(file) not in file_paths.values():
                    zip_file.write(file, file.name)

    zip_buffer.seek(0)
    st.download_button(
        label="⬇️ Download All (ZIP)",
        data=zip_buffer.read(),
        file_name=f"{result_source}_complete_results.zip",
        mime="application/zip",
        help="All analysis outputs in one compressed file",
        use_container_width=True,
        type="primary"
    )
else:
    st.warning("Output directory not available for batch download")

st.markdown("---")

# Export predictions to CSV
st.subheader("🔄 Export Options")

predictions = results.get('predictions')
if predictions is not None and not predictions.empty:
    col_a, col_b = st.columns(2)

    with col_a:
        # CSV export
        csv_data = predictions.to_csv(index=False)
        st.download_button(
            label="📈 Export Predictions as CSV",
            data=csv_data,
            file_name=f"{result_source}_predictions.csv",
            mime="text/csv",
            help="Comma-separated format for Excel/spreadsheets",
            use_container_width=True
        )

    with col_b:
        # Excel export
        try:
            from io import BytesIO
            excel_buffer = BytesIO()
            predictions.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            st.download_button(
                label="📊 Export Predictions as Excel",
                data=excel_buffer.read(),
                file_name=f"{result_source}_predictions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Excel format with formatting",
                width='stretch'
            )
        except ImportError:
            st.info("Install openpyxl for Excel export")
else:
    st.info("No predictions available for export")

st.markdown("---")

# File information
with st.expander("📋 File Descriptions"):
    st.markdown("""
    **Cell Classifications (_prediction.txt)**:
    - Cell ID, prediction (aneuploid/diploid), confidence score

    **CNV Segments (_CNA_results.txt)**:
    - Chromosome, start, end, copy number for each segment

    **CNV Heatmap (_heatmap.jpeg)**:
    - Visual representation of CNV across genome

    **Gene-level CNV (_gene_by_cell.txt)**:
    - Full gene-by-cell copy number matrix

    **Detailed Heatmap (_with_genes_heatmap.pdf)**:
    - High-resolution heatmap with gene labels

    **Clustering Data (_clustering.rds)**:
    - R data object for advanced analysis in R
    """)

# File sizes summary
st.markdown("### 📊 Storage Summary")
total_size = 0
file_count = 0
for file_type, file_path in file_paths.items():
    if Path(file_path).exists():
        size = Path(file_path).stat().st_size
        total_size += size
        file_count += 1

if file_count > 0:
    col_x, col_y = st.columns(2)
    with col_x:
        st.metric("Total Files", file_count)
    with col_y:
        st.metric("Total Size", f"{total_size / 1024 / 1024:.2f} MB")
