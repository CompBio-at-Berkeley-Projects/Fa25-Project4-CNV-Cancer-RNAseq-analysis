"""
Visualization Component

Display analysis results and plots.

Author: Baovi Nguyen
"""

import streamlit as st
import pandas as pd
from typing import Dict


def display_results(results: Dict) -> None:
    """
    Display CopyKAT analysis results.
    
    Args:
        results: Dictionary containing analysis results
    """
    # Summary statistics
    display_summary_statistics(results)
    
    st.markdown("---")
    
    # CNV Heatmap
    display_cnv_heatmap(results)
    
    st.markdown("---")
    
    # Predictions table
    display_predictions_table(results)


def display_summary_statistics(results: Dict) -> None:
    """
    Display summary statistics as metrics.
    
    Args:
        results: Dictionary containing summary data
    """
    st.subheader("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    summary = results.get('summary', {})
    
    with col1:
        st.metric("Total Cells", summary.get('n_cells', 'N/A'))
    
    with col2:
        n_aneu = summary.get('n_aneuploid', 0)
        st.metric("Aneuploid", n_aneu)
    
    with col3:
        n_dip = summary.get('n_diploid', 0)
        st.metric("Diploid", n_dip)
    
    with col4:
        n_undef = summary.get('n_not_defined', 0)
        st.metric("Not Defined", n_undef)


def display_cnv_heatmap(results: Dict) -> None:
    """
    Display CNV heatmap image.
    
    Args:
        results: Dictionary containing file paths
    """
    st.subheader("CNV Heatmap")
    
    heatmap_path = results.get('files', {}).get('heatmap')
    
    if heatmap_path:
        try:
            st.image(heatmap_path, use_column_width=True)
        except Exception as e:
            st.error(f"Error loading heatmap: {str(e)}")
    else:
        st.warning("Heatmap not available")


def display_predictions_table(results: Dict) -> None:
    """
    Display cell classification predictions table.
    
    Args:
        results: Dictionary containing file paths
    """
    st.subheader("Cell Classifications")
    
    predictions_path = results.get('files', {}).get('predictions')
    
    if predictions_path:
        try:
            df = pd.read_csv(predictions_path, sep='\t')
            
            # Display dataframe
            st.dataframe(df, use_container_width=True)
            
            # Display distribution
            with st.expander("Classification Distribution"):
                dist = df['copykat.pred'].value_counts()
                st.bar_chart(dist)
        
        except Exception as e:
            st.error(f"Error loading predictions: {str(e)}")
    else:
        st.warning("Predictions not available")


def display_confidence_distribution(predictions_df: pd.DataFrame) -> None:
    """
    Display confidence score distribution.
    
    Args:
        predictions_df: DataFrame with predictions
    """
    st.subheader("Confidence Distribution")
    
    if 'copykat.confidence' in predictions_df.columns:
        st.hist_chart(predictions_df['copykat.confidence'])
    else:
        st.warning("Confidence scores not available")

