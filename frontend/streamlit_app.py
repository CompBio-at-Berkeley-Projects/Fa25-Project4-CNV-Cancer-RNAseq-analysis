"""
CopyKAT CNV Analysis Dashboard

Main entry point for the Streamlit web application.
This application provides an intuitive interface for analyzing copy number
variations (CNVs) from single-cell RNA-seq data using CopyKAT.

Author: Baovi Nguyen (Frontend Lead)
Date: October 2024
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="CopyKAT CNV Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/navinlabcode/copykat',
        'Report a bug': None,
        'About': """
        # CopyKAT CNV Analysis Dashboard
        
        A user-friendly interface for analyzing copy number variations 
        from single-cell RNA-seq data.
        
        Powered by CopyKAT and Streamlit.
        """
    }
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    
    if 'analysis_params' not in st.session_state:
        st.session_state.analysis_params = {}
    
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'

init_session_state()

# Main application
def main():
    """Main application logic"""
    
    # Title and description
    st.markdown('<h1 class="main-header">🧬 CopyKAT CNV Analysis</h1>', 
                unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Identify malignant cells through copy number variation analysis</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80?text=CNV+Analysis", 
                 use_column_width=True)
        st.markdown("---")
        
        st.header("Navigation")
        st.markdown("""
        Use the pages menu above to navigate:
        - **Upload**: Upload your data
        - **Configure**: Set analysis parameters  
        - **Results**: View analysis results
        - **Download**: Download outputs
        """)
        
        st.markdown("---")
        
        # Quick stats if analysis is complete
        if st.session_state.results:
            st.success("✅ Analysis Complete")
            st.metric("Total Cells", st.session_state.results.get('n_cells', 'N/A'))
            st.metric("Aneuploid", st.session_state.results.get('n_aneuploid', 'N/A'))
        
        st.markdown("---")
        
        # Help section
        with st.expander("ℹ️ Quick Help"):
            st.markdown("""
            **Getting Started:**
            1. Upload your expression matrix
            2. Configure parameters (or use defaults)
            3. Run analysis
            4. View and download results
            
            **Need more help?**
            - Check the documentation pages
            - Review parameter tooltips
            - Contact your team lead
            """)
    
    # Main content
    st.markdown("## Welcome!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>📤 Step 1: Upload</h3>
        <p>Upload your single-cell RNA-seq expression matrix 
        (genes x cells format)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h3>⚙️ Step 2: Configure</h3>
        <p>Set analysis parameters or use recommended defaults</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
        <h3>📊 Step 3: Analyze</h3>
        <p>Run CopyKAT and view results with interactive visualizations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("---")
    st.markdown("## Getting Started")
    
    if not st.session_state.uploaded_file:
        st.info("👈 Go to the **Upload** page to begin")
    elif not st.session_state.analysis_params:
        st.info("👈 Go to the **Configure** page to set parameters")
    elif not st.session_state.results:
        st.info("⚙️ Ready to run analysis! Go to **Configure** page and click 'Run Analysis'")
    else:
        st.success("✅ Analysis complete! Check the **Results** and **Download** pages")
    
    # About section
    st.markdown("---")
    st.markdown("## About CopyKAT")
    
    with st.expander("What is CopyKAT?"):
        st.markdown("""
        CopyKAT (Copynumber Karyotyping of Aneuploid Tumors) is a computational tool 
        that uses single-cell RNA-seq data to identify aneuploid cells by detecting 
        copy number variations (CNVs) across the genome.
        
        **Key Features:**
        - Distinguishes malignant from non-malignant cells
        - Requires no prior knowledge of normal cells
        - Generates genome-wide CNV heatmaps
        - Provides cell-level classifications with confidence scores
        
        **Reference:**
        Gao et al. (2021) Nature Biotechnology
        """)
    
    with st.expander("How does it work?"):
        st.markdown("""
        1. **Data Input**: Single-cell RNA-seq expression matrix (genes x cells)
        2. **Preprocessing**: Normalize and smooth expression data
        3. **Segmentation**: Identify genomic segments with consistent copy number
        4. **Classification**: Cluster cells and identify aneuploid populations
        5. **Output**: Cell classifications, CNV heatmaps, and detailed results
        """)
    
    with st.expander("What data do I need?"):
        st.markdown("""
        **Required:**
        - Gene expression matrix (genes as rows, cells as columns)
        - Gene names (symbols like "TP53" or "EGFR")
        - At least 50-100 cells (more is better)
        - At least 1000-5000 genes
        
        **Supported Formats:**
        - Tab-separated (.txt, .tsv)
        - Comma-separated (.csv)
        - Compressed (.gz)
        
        **Example datasets** are provided in the Upload page for testing.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
        Built with Streamlit | Powered by CopyKAT | 
        <a href='https://github.com/navinlabcode/copykat'>CopyKAT GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

