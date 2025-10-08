# Streamlit Dashboard Design Guide for CopyKAT

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Layout Design](#layout-design)
4. [Widget Selection Guide](#widget-selection-guide)
5. [User Experience Features](#user-experience-features)
6. [Complete Code Examples](#complete-code-examples)
7. [Best Practices](#best-practices)
8. [Performance Optimization](#performance-optimization)

---

## Introduction

This guide provides comprehensive instructions for building a beginner-friendly Streamlit dashboard for Copy

KAT analysis, based on the PRD requirements and Streamlit best practices.

### Dashboard Goals

1. **Simplicity**: One-click CNV analysis
2. **Guidance**: Help text and validation at every step
3. **Feedback**: Real-time progress and status updates
4. **Accessibility**: No command-line knowledge required
5. **Completeness**: Upload → Analyze → Visualize → Download

---

## Architecture Overview

### Data Flow

```
User Upload
    ↓
[Streamlit Frontend]
    ↓
File Validation
    ↓
Parameter Configuration
    ↓
[Python Backend]
    ↓
subprocess → R Script → CopyKAT
    ↓
Results Generated
    ↓
[Streamlit Frontend]
    ↓
Visualization & Download
```

### File Structure

```
app/
├── streamlit_app.py          # Main dashboard
├── utils/
│   ├── data_loader.py        # File upload handling
│   ├── r_integration.py      # Python-R bridge
│   ├── validators.py         # Input validation
│   └── visualizations.py     # Plot generation
├── r_scripts/
│   └── run_copykat.R         # R wrapper for CopyKAT
└── requirements.txt          # Python dependencies
```

---

## Layout Design

### Page Configuration

```python
import streamlit as st

# Must be first Streamlit command
st.set_page_config(
    page_title="CopyKAT CNV Analysis",
    page_icon="🧬",
    layout="wide",  # Use full width
    initial_sidebar_state="expanded"
)
```

### Recommended Layout

```
+------------------+------------------------+
| Sidebar          | Main Panel             |
+------------------+------------------------+
| [Logo/Title]     | [Page Title]           |
|                  |                        |
| Upload Section   | [Instructions]         |
| - File upload    |                        |
| - Preview        | [Content Area]         |
|                  | (changes by tab)       |
| Parameters       |                        |
| - Basic          | Tab 1: Upload          |
| - Advanced       | Tab 2: Configure       |
|                  | Tab 3: Results         |
| Run Button       | Tab 4: Download        |
|                  |                        |
| Status Panel     | [Progress/Errors]      |
+------------------+------------------------+
```

### Implementation

```python
# Sidebar for inputs
with st.sidebar:
    st.image("logo.png", width=200)
    st.title("CopyKAT Analysis")

    # Upload section
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader(...)

    # Parameters
    st.header("2. Configure")
    # ... parameter widgets ...

    # Run button
    st.header("3. Run Analysis")
    run_button = st.button("🚀 Run CopyKAT", type="primary")

# Main panel with tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📁 Upload",
    "⚙️ Parameters",
    "📊 Results",
    "💾 Download"
])

with tab1:
    # Upload instructions and preview
    ...

with tab2:
    # Parameter explanations
    ...

with tab3:
    # Visualizations
    ...

with tab4:
    # Download options
    ...
```

---

## Widget Selection Guide

### Complete Parameter Widget Mapping

#### File Upload

```python
uploaded_file = st.file_uploader(
    "Upload Expression Matrix",
    type=["txt", "csv", "tsv", "gz"],
    help="""
    Upload your gene expression matrix:
    - Format: genes in rows, cells in columns
    - Supported: .txt, .csv, .tsv, .gz
    - Max size: 200MB
    """
)

# Preview
if uploaded_file:
    df = pd.read_csv(uploaded_file, index_col=0, nrows=5)
    st.success(f"Loaded: {df.shape[0]} genes × {df.shape[1]} cells (preview)")
    with st.expander("Preview first 5 genes"):
        st.dataframe(df)
```

#### Sample Name

```python
sam_name = st.text_input(
    "Sample Name",
    value="sample_01",
    max_chars=50,
    help="Name for output files (no spaces or special characters)"
)

# Validation
if ' ' in sam_name or not sam_name.isalnum():
    st.error("Sample name must be alphanumeric (no spaces)")
```

#### Genome Selection with Auto-Detection

```python
# Auto-detect from gene names
def detect_genome(gene_names):
    """Detect if genes are human or mouse"""
    human_markers = ["EGFR", "TP53", "MYC"]
    mouse_markers = ["Egfr", "Trp53", "Myc"]

    if any(g in gene_names for g in human_markers):
        return "hg20"
    elif any(g in gene_names for g in mouse_markers):
        return "mm10"
    return None

# Widget
genome = st.selectbox(
    "Reference Genome",
    options=["hg20", "mm10"],
    index=0,
    format_func=lambda x: {
        "hg20": "🧑 Human (hg20)",
        "mm10": "🐭 Mouse (mm10)"
    }[x],
    help="Select the organism for your sample"
)

# Show auto-detection
if data_loaded:
    detected = detect_genome(gene_names)
    if detected and detected != genome:
        st.warning(f"Auto-detected {detected} based on gene names. "
                   f"Consider changing selection.")
```

#### Cell Line Type

```python
cell_line = st.radio(
    "Sample Type",
    options=["no", "yes"],
    format_func=lambda x: {
        "no": "🔬 Tumor Sample (mixed tumor + normal cells)",
        "yes": "🧫 Pure Cell Line (100% cancer cells)"
    }[x],
    help="""
    - Choose 'Tumor Sample' for patient biopsies, organoids, PDX models
    - Choose 'Pure Cell Line' ONLY for established cell lines like HeLa, MCF7
    """,
    horizontal=True
)
```

#### Quality Filtering Parameters

```python
st.subheader("Quality Filtering")

ngene_chr = st.slider(
    "Minimum Genes Per Chromosome",
    min_value=1,
    max_value=20,
    value=5,
    step=1,
    help="""
    Cells must have at least this many genes detected on each chromosome.
    - Lower (1-3): Keep more cells, tolerate lower quality
    - Higher (10-20): Stricter quality filter
    - **Recommended**: 5 for most datasets
    """
)

# Show estimated filtering impact
if data_loaded:
    estimated_retained = estimate_cell_retention(data, ngene_chr)
    st.caption(f"📊 Estimated: ~{estimated_retained}/{total_cells} "
               f"cells will pass filter ({estimated_retained/total_cells*100:.1f}%)")
```

#### Detection Rate Parameters with Validation

```python
st.subheader("Gene Detection Rates")

col1, col2 = st.columns(2)

with col1:
    low_dr = st.slider(
        "LOW.DR (Smoothing)",
        min_value=0.01,
        max_value=0.30,
        value=0.05,
        step=0.01,
        format="%.2f",
        help="""
        Minimum fraction of cells expressing a gene (for smoothing).
        - Lower (0.01-0.03): Keep more genes, sparse data
        - Higher (0.1-0.2): Stricter filtering, dense data
        - **Default**: 0.05 (5% of cells)
        """
    )

with col2:
    up_dr = st.slider(
        "UP.DR (Segmentation)",
        min_value=low_dr,  # Must be >= LOW.DR
        max_value=0.30,
        value=max(0.10, low_dr),
        step=0.01,
        format="%.2f",
        help="""
        Minimum fraction of cells for segmentation (must be ≥ LOW.DR).
        - Usually set higher than LOW.DR
        - **Default**: 0.10 (10% of cells)
        """
    )

# Validation message
if up_dr < low_dr:
    st.error("⚠️ UP.DR must be greater than or equal to LOW.DR")
```

#### Window Size with Visual Guide

```python
win_size = st.slider(
    "Window Size (genes per segment)",
    min_value=10,
    max_value=150,
    value=25,
    step=5,
    help="""
    Number of genes per window for segmentation.
    - Smaller (10-15): High resolution, detects focal CNVs
    - Larger (50-100): Smooth results, misses focal events
    - **Default**: 25 (~5Mb genomic resolution)
    """
)

# Visual resolution indicator
resolution_mb = (win_size / 20000) * 3000  # Rough estimate
st.caption(f"📏 Genomic resolution: ~{resolution_mb:.1f} Mb per segment")

# Visual guide
st.progress(min(win_size / 150, 1.0))
if win_size < 20:
    st.caption("🔬 High resolution - good for focal CNVs")
elif win_size > 50:
    st.caption("🔭 Low resolution - chromosome-level events")
else:
    st.caption("⚖️ Balanced resolution - recommended")
```

#### KS Cut with Semantic Labels

```python
ks_cut = st.select_slider(
    "Segmentation Sensitivity (KS.cut)",
    options=[0.05, 0.1, 0.15, 0.2, 0.3, 0.4],
    value=0.1,
    format_func=lambda x: {
        0.05: "Very Strict (many breakpoints)",
        0.1: "Moderate (recommended)",
        0.15: "Relaxed",
        0.2: "Loose",
        0.3: "Very Loose",
        0.4: "Minimal segmentation"
    }.get(x, f"{x}"),
    help="""
    Controls how many CNV breakpoints are detected.
    - Lower (0.05-0.1): More sensitive, more breakpoints
    - Higher (0.2-0.4): Less sensitive, smoother profiles
    - **Default**: 0.1
    """
)
```

#### Distance Metric

```python
distance = st.selectbox(
    "Distance Metric",
    options=["euclidean", "pearson", "spearman"],
    index=0,
    format_func=lambda x: {
        "euclidean": "Euclidean (standard, recommended)",
        "pearson": "Pearson correlation (for batch effects)",
        "spearman": "Spearman correlation (robust to outliers)"
    }[x],
    help="Method for measuring cell similarity"
)
```

#### CPU Cores

```python
import os

max_cores = os.cpu_count()

n_cores = st.slider(
    "CPU Cores",
    min_value=1,
    max_value=max_cores,
    value=min(4, max_cores),
    step=1,
    help=f"Number of CPU cores to use (max: {max_cores}). "
         f"More cores = faster analysis."
)

# Time estimate
if data_loaded:
    estimated_time = estimate_runtime(n_cells, n_cores)
    st.caption(f"⏱️ Estimated runtime: ~{estimated_time} minutes")
```

#### Output Options

```python
st.subheader("Output Options")

col1, col2 = st.columns(2)

with col1:
    output_seg = st.checkbox(
        "Generate IGV .seg file",
        value=False,
        help="Create file for viewing in IGV genome browser"
    )

with col2:
    plot_genes = st.checkbox(
        "Show gene labels in heatmap",
        value=True,
        help="May slow down rendering for large datasets"
    )

    if plot_genes and n_cells > 500:
        st.warning("⚠️ Gene labels may be slow with >500 cells")
```

---

## User Experience Features

### Progress Tracking

```python
def run_copykat_with_progress():
    """Run CopyKAT with live progress updates"""

    # Create progress elements
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Step 1: Data preparation
    status_text.text("Step 1/5: Preparing data...")
    progress_bar.progress(0.1)
    # ... data prep code ...

    # Step 2: Writing R script
    status_text.text("Step 2/5: Configuring CopyKAT...")
    progress_bar.progress(0.2)
    # ... write R script ...

    # Step 3: Running CopyKAT
    status_text.text("Step 3/5: Running CNV analysis (this may take 5-15 min)...")
    progress_bar.progress(0.3)

    # Monitor R process
    process = subprocess.Popen(...)
    while process.poll() is None:
        # Parse R output for progress
        time.sleep(2)
        # Update progress based on log

    progress_bar.progress(0.7)

    # Step 4: Reading results
    status_text.text("Step 4/5: Loading results...")
    progress_bar.progress(0.8)
    # ... load results ...

    # Step 5: Generating visualizations
    status_text.text("Step 5/5: Creating visualizations...")
    progress_bar.progress(0.9)
    # ... create plots ...

    progress_bar.progress(1.0)
    status_text.text("✅ Analysis complete!")

    return results
```

### Real-Time Validation

```python
def validate_expression_matrix(df):
    """Validate uploaded data with helpful messages"""

    errors = []
    warnings = []

    # Check dimensions
    n_genes, n_cells = df.shape

    if n_cells < 50:
        errors.append(f"Too few cells ({n_cells}). Minimum: 50 cells.")

    if n_genes < 1000:
        warnings.append(f"Low gene count ({n_genes}). CopyKAT works best with >5000 genes.")

    # Check for negative values
    if (df < 0).any().any():
        errors.append("Negative values detected. Use raw counts or normalized positive values.")

    # Check gene names
    gene_names = df.index.tolist()
    if not all(isinstance(g, str) for g in gene_names[:10]):
        errors.append("Gene names must be strings (not numbers).")

    # Check for duplicates
    if len(gene_names) != len(set(gene_names)):
        warnings.append("Duplicate gene names detected. Will be removed.")

    # Display validation results
    if errors:
        for err in errors:
            st.error(f"❌ {err}")
        return False

    if warnings:
        for warn in warnings:
            st.warning(f"⚠️ {warn}")

    st.success(f"✅ Data validated: {n_genes} genes × {n_cells} cells")
    return True
```

### Error Handling UI

```python
try:
    results = run_copykat(...)

except FileNotFoundError as e:
    st.error(f"""
    ❌ **File Not Found**

    CopyKAT could not find required files.

    **Error details**: {str(e)}

    **Possible causes**:
    - R script not in expected location
    - Output directory not created
    - Missing dependencies

    **Solution**: Check file paths in settings
    """)

except subprocess.CalledProcessError as e:
    st.error(f"""
    ❌ **CopyKAT Analysis Failed**

    The R script encountered an error.

    **Error code**: {e.returncode}
    **Error output**:
    ```
    {e.stderr}
    ```

    **Common causes**:
    - Data quality issues → Try lowering LOW.DR and UP.DR
    - Memory issues → Reduce dataset size or increase RAM
    - Invalid parameters → Check parameter values

    See [Troubleshooting Guide](docs/07_TROUBLESHOOTING.md) for solutions.
    """)

except Exception as e:
    st.error(f"""
    ❌ **Unexpected Error**

    {str(e)}

    Please report this issue with the error message above.
    """)
```

### Help System

```python
# Contextual help button
with st.sidebar:
    if st.button("❓ Help", key="help_main"):
        st.info("""
        **Quick Start:**
        1. Upload your expression matrix
        2. Adjust parameters if needed (defaults work well)
        3. Click 'Run CopyKAT'
        4. View results and download

        **Need more help?**
        - [Beginner Tutorial](docs/08_BEGINNER_TUTORIAL.md)
        - [Parameter Guide](docs/03_PARAMETERS_REFERENCE.md)
        - [Troubleshooting](docs/07_TROUBLESHOOTING.md)
        """)

# Inline tooltips
st.markdown("""
<style>
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
}
</style>
""", unsafe_allow_html=True)
```

---

## Complete Code Examples

### Minimal Working Dashboard

```python
import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="CopyKAT Analysis", layout="wide")

# Title
st.title("🧬 CopyKAT CNV Analysis Dashboard")

# Sidebar
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Expression Matrix", type=["txt", "csv", "gz"])

    st.header("Parameters")
    sam_name = st.text_input("Sample Name", "sample")
    ngene_chr = st.slider("Min genes/chr", 1, 20, 5)

    run_button = st.button("🚀 Run Analysis", type="primary")

# Main panel
if uploaded_file:
    # Preview
    df = pd.read_csv(uploaded_file, index_col=0, nrows=5)
    st.write(f"Preview: {df.shape[0]} genes × {df.shape[1]} cells")
    st.dataframe(df)

    if run_button:
        with st.spinner("Running CopyKAT..."):
            # Save uploaded file
            df_full = pd.read_csv(uploaded_file, index_col=0)
            df_full.to_csv("temp_data.txt", sep="\t")

            # Run R script
            result = subprocess.run(
                ["Rscript", "run_copykat.R", "temp_data.txt", sam_name, str(ngene_chr)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                st.success("✅ Analysis complete!")

                # Load and display results
                predictions = pd.read_csv(f"{sam_name}_copykat_prediction.txt", sep="\t")
                st.subheader("Cell Classifications")
                st.dataframe(predictions)

                # Show classification summary
                summary = predictions['copykat.pred'].value_counts()
                st.bar_chart(summary)
            else:
                st.error(f"Error: {result.stderr}")
else:
    st.info("👆 Upload an expression matrix to begin")
```

---

## Best Practices Summary

1. **Use `st.cache_data`** for expensive operations
2. **Validate all inputs** before running analysis
3. **Provide real-time feedback** during long operations
4. **Group related parameters** in expandable sections
5. **Use semantic labels** (not just parameter names)
6. **Show estimated impacts** (cells retained, runtime, etc.)
7. **Handle errors gracefully** with actionable messages
8. **Enable downloads** for all outputs
9. **Add tooltips** to every widget
10. **Test with real data** at various scales

---

**Next Steps**:
- [06_PYTHON_R_INTEGRATION.md](06_PYTHON_R_INTEGRATION.md) - Connecting Python and R
- [08_BEGINNER_TUTORIAL.md](08_BEGINNER_TUTORIAL.md) - Complete walkthrough

**See Also**:
- [PRD Document](../Product%20Requirements%20Document%20(PRD)_%20CNV-Cancer-RNAseq-analysis.md) - Requirements
- [10_PARAMETER_QUICK_REFERENCE.md](10_PARAMETER_QUICK_REFERENCE.md) - Parameter guide
