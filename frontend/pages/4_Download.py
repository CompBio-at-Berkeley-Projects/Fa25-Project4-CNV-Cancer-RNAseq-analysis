"""
Download Page

Handles result downloads.

Author: Baovi Nguyen
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

st.title("💾 Download Results")

# Check if results exist
if not st.session_state.get('results'):
    st.warning("⚠️ No results available to download")
    st.info("Complete an analysis on the **Configure** page first")
    st.stop()

st.success("✅ Results ready for download")

st.markdown("""
Download your analysis results in various formats below.
""")

# File downloads section
st.subheader("📁 Output Files")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Primary Outputs**")
    
    # TODO: Implement actual file downloads when backend is ready
    
    # Predictions
    st.download_button(
        label="📄 Cell Classifications (TXT)",
        data="Placeholder data",
        file_name="copykat_predictions.txt",
        mime="text/plain",
        help="Cell-level classification results",
        disabled=True  # Enable when backend is ready
    )
    
    # CNV results
    st.download_button(
        label="📄 CNV Segments (TXT)",
        data="Placeholder data",
        file_name="copykat_CNA_results.txt",
        mime="text/plain",
        help="Segment-level CNV calls",
        disabled=True
    )
    
    # Heatmap
    st.download_button(
        label="🖼️ CNV Heatmap (JPEG)",
        data=b"Placeholder",
        file_name="copykat_heatmap.jpeg",
        mime="image/jpeg",
        help="CNV heatmap visualization",
        disabled=True
    )

with col2:
    st.markdown("**Additional Outputs**")
    
    # Report
    st.download_button(
        label="📊 HTML Report",
        data="<html>Placeholder</html>",
        file_name="analysis_report.html",
        mime="text/html",
        help="Comprehensive analysis report",
        disabled=True
    )
    
    # Log file
    st.download_button(
        label="📝 Analysis Log",
        data="Placeholder log",
        file_name="analysis.log",
        mime="text/plain",
        help="Detailed execution log",
        disabled=True
    )
    
    # Raw CNV matrix
    st.download_button(
        label="📄 Gene-level CNV (TXT)",
        data="Placeholder data",
        file_name="copykat_CNA_raw_results.txt",
        mime="text/plain",
        help="Gene-by-cell CNV matrix",
        disabled=True
    )

st.markdown("---")

# Export formats
st.subheader("📦 Batch Download")

st.markdown("Download all results in a single archive:")

# TODO: Implement zip download
st.download_button(
    label="⬇️ Download All (ZIP)",
    data=b"Placeholder",
    file_name="copykat_results.zip",
    mime="application/zip",
    help="All analysis outputs in one file",
    disabled=True
)

st.markdown("---")

# Export to other formats
with st.expander("🔄 Export to Other Formats"):
    st.markdown("**Convert results to:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Excel Format", disabled=True):
            st.info("Will export predictions to Excel format")
    
    with col2:
        if st.button("📈 CSV Format", disabled=True):
            st.info("Will export predictions to CSV format")
    
    with col3:
        if st.button("🧬 Seurat Object", disabled=True):
            st.info("Will export to Seurat-compatible format")

st.markdown("---")

# File information
with st.expander("📋 File Descriptions"):
    st.markdown("""
    **Cell Classifications (copykat_prediction.txt)**:
    - Cell ID, prediction (aneuploid/diploid), confidence score
    
    **CNV Segments (copykat_CNA_results.txt)**:
    - Chromosome, start, end, copy number for each segment
    
    **CNV Heatmap (copykat_heatmap.jpeg)**:
    - Visual representation of CNV across genome
    
    **Gene-level CNV (copykat_CNA_raw_results.txt)**:
    - Full gene-by-cell copy number matrix
    
    **HTML Report**:
    - Complete analysis report with all visualizations
    
    **Analysis Log**:
    - Detailed execution log for troubleshooting
    """)

st.info("🔨 Download functionality will be enabled when analysis is complete")

