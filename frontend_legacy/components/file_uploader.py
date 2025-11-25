"""
File Uploader Component

Reusable file upload widget with preview and validation.

Author: Baovi Nguyen
"""

import streamlit as st
import pandas as pd
from typing import Optional, Tuple


def file_uploader_component() -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
    """
    Display file uploader widget with preview functionality.
    
    Returns:
        UploadedFile object if file is uploaded, None otherwise
    """
    uploaded_file = st.file_uploader(
        "Upload Expression Matrix",
        type=['txt', 'csv', 'tsv', 'gz'],
        help="""
        Upload your gene expression matrix:
        - Format: genes in rows, cells in columns
        - Supported: .txt, .csv, .tsv, .gz
        - Max size: 200MB
        """
    )
    
    if uploaded_file:
        # Save to session state
        st.session_state.uploaded_file = uploaded_file
        
        # Preview data
        preview_data(uploaded_file)
    
    return uploaded_file


def preview_data(uploaded_file) -> None:
    """
    Display preview of uploaded data.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    """
    try:
        # Detect separator
        if uploaded_file.name.endswith('.csv'):
            sep = ','
        else:
            sep = '\t'
        
        # Read first few rows
        df = pd.read_csv(uploaded_file, sep=sep, index_col=0, nrows=5)
        
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Display success message
        st.success(f"Loaded: {df.shape[0]} genes × {df.shape[1]} cells (preview)")
        
        # Show preview
        with st.expander("Preview Data"):
            st.dataframe(df)
        
        # Show summary
        with st.expander("Data Summary"):
            st.write("**First few gene names:**")
            st.write(", ".join(df.index[:5].tolist()))
            
            st.write("**First few cell names:**")
            st.write(", ".join(df.columns[:5].tolist()))
            
            st.write("**Value range (preview):**")
            st.write(f"Min: {df.min().min():.2f}, Max: {df.max().max():.2f}")
    
    except Exception as e:
        st.error(f"Error previewing file: {str(e)}")
        st.info("Please ensure your file is properly formatted")


# TODO: Implement when validators are ready
def validate_file(uploaded_file) -> Tuple[bool, list, list]:
    """
    Validate uploaded expression matrix.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Placeholder validation
    # TODO: Implement actual validation
    # from frontend.utils.validators import validate_expression_matrix
    # is_valid, errors, warnings = validate_expression_matrix(df)
    
    return True, errors, warnings

