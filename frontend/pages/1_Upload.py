"""
Data Upload Page

Handles file upload and preview of expression matrices.

Author: Baovi Nguyen
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import constants for example datasets
from shared.constants import EXAMPLE_DATASETS

# TODO: Import validators when implemented
# from frontend.utils.validators import validate_expression_matrix

st.title("📤 Data Upload")

st.markdown("""
Upload your single-cell RNA-seq expression matrix. The file should contain:
- **Rows**: Genes (with gene symbols as row names)
- **Columns**: Cells (with cell IDs as column names)
- **Values**: Expression counts (raw or normalized)
""")

# Show status if example dataset is loaded
if 'example_dataset' in st.session_state and st.session_state.example_dataset:
    st.success(f"✅ Example dataset loaded: **{st.session_state.example_dataset.capitalize()}**")
    st.info(f"📁 File path: `{st.session_state.example_file_path}`")
    if st.button("Clear Example Dataset"):
        st.session_state.example_dataset = None
        st.session_state.example_file_path = None
        st.rerun()

# File uploader
st.subheader("Upload Expression Matrix")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=['txt', 'csv', 'tsv', 'gz'],
    help="""
    Supported formats: .txt, .csv, .tsv, .gz
    Maximum file size: 200MB
    """
)

if uploaded_file is not None:
    try:
        # Save to session state
        st.session_state.uploaded_file = uploaded_file
        
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024 / 1024:.2f} MB",
            "File type": uploaded_file.type
        }
        
        with st.expander("📁 File Information"):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        # Preview data
        st.subheader("Data Preview")
        
        with st.spinner("Loading data preview..."):
            # Detect separator
            if uploaded_file.name.endswith('.csv'):
                sep = ','
            else:
                sep = '\t'
            
            # Read first few rows
            try:
                df_preview = pd.read_csv(
                    uploaded_file, 
                    sep=sep, 
                    index_col=0, 
                    nrows=10
                )
                
                # Reset file pointer
                uploaded_file.seek(0)
                
                # Display dimensions
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Preview Genes", df_preview.shape[0])
                with col2:
                    st.metric("Preview Cells", df_preview.shape[1])
                with col3:
                    # Estimate total (rough approximation)
                    st.metric("Estimated Total Genes", "> 1000")
                
                # Show preview
                st.dataframe(df_preview.head(10), width='stretch')
                
                # Data summary
                with st.expander("📊 Data Summary"):
                    st.write("**First few gene names:**")
                    st.write(", ".join(df_preview.index[:5].tolist()))
                    
                    st.write("**First few cell names:**")
                    st.write(", ".join(df_preview.columns[:5].tolist()))
                    
                    st.write("**Value range (preview):**")
                    st.write(f"Min: {df_preview.min().min():.2f}, Max: {df_preview.max().max():.2f}")
                
                # TODO: Add validation when validator is implemented
                # is_valid, errors, warnings = validate_expression_matrix(df_preview)
                # Display validation results
                
                st.success("✅ File uploaded successfully!")
                st.info("👉 Go to the **Configure** page to set analysis parameters")
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please ensure your file is properly formatted")
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    # Show example datasets
    st.info("No file uploaded yet. Upload a file above or try an example dataset.")
    
    st.subheader("📚 Example Datasets")
    
    st.markdown("""
    Test the application with pre-loaded datasets:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Glioblastoma Dataset**")
        st.write("- Source: GSE57872")
        st.write(f"- Cells: {EXAMPLE_DATASETS['glioblastoma']['n_cells']}")
        st.write(f"- Genes: {EXAMPLE_DATASETS['glioblastoma']['n_genes']}")

        if st.button("Load Glioblastoma Example"):
            # Store example dataset path in session state
            dataset_path = project_root / EXAMPLE_DATASETS['glioblastoma']['path']
            st.session_state.example_dataset = 'glioblastoma'
            st.session_state.example_file_path = str(dataset_path)
            st.session_state.uploaded_file = None  # Clear any uploaded file
            st.success("✅ Glioblastoma example loaded! Go to Configure page to run analysis.")
            st.rerun()

    with col2:
        st.markdown("**Melanoma Dataset**")
        st.write("- Source: GSE72056")
        st.write(f"- Cells: {EXAMPLE_DATASETS['melanoma']['n_cells']}")
        st.write(f"- Genes: {EXAMPLE_DATASETS['melanoma']['n_genes']}")

        if st.button("Load Melanoma Example"):
            # Store example dataset path in session state
            dataset_path = project_root / EXAMPLE_DATASETS['melanoma']['path']
            st.session_state.example_dataset = 'melanoma'
            st.session_state.example_file_path = str(dataset_path)
            st.session_state.uploaded_file = None  # Clear any uploaded file
            st.success("✅ Melanoma example loaded! Go to Configure page to run analysis.")
            st.rerun()

# Data requirements
with st.expander("ℹ️ Data Requirements"):
    st.markdown("""
    **File Format:**
    - First column: Gene names/symbols
    - First row: Cell IDs
    - Values: Expression counts (integer or float)
    
    **Minimum Requirements:**
    - At least 50 cells (100+ recommended)
    - At least 1,000 genes (5,000+ recommended)
    - Gene names must be present
    - Cell IDs must be unique
    
    **Example Format:**
    ```
    Gene    Cell1    Cell2    Cell3    ...
    TP53    123      45       67       ...
    EGFR    89       234      156      ...
    MYC     45       78       123      ...
    ...
    ```
    """)

