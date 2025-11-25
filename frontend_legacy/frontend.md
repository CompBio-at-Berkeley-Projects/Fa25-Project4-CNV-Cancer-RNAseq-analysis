# Frontend Development Guide

Welcome, Baovi! This guide contains everything you need to develop the Streamlit frontend for the CNV-Cancer-RNAseq-analysis project.

## Table of Contents

1. [Your Role and Responsibilities](#your-role-and-responsibilities)
2. [Frontend Architecture](#frontend-architecture)
3. [Getting Started](#getting-started)
4. [Streamlit Application Structure](#streamlit-application-structure)
5. [Backend Integration](#backend-integration)
6. [Component Development](#component-development)
7. [UI/UX Requirements](#uiux-requirements)
8. [Testing Your Code](#testing-your-code)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

## Your Role and Responsibilities

As the Frontend Lead, you are responsible for:

- Building the entire Streamlit user interface
- Creating reusable UI components
- Implementing file upload functionality
- Developing parameter configuration forms
- Displaying analysis results and visualizations
- Integrating with the backend API layer
- Ensuring good user experience

You will NOT be writing R code or directly calling R scripts. The backend team handles all R-related work.

## Frontend Architecture

### Directory Structure

```
frontend/
├── streamlit_app.py          # Main application entry point
├── pages/                    # Multi-page app structure
│   ├── 1_Upload.py          # File upload page
│   ├── 2_Configure.py       # Parameter configuration page
│   ├── 3_Results.py         # Results display page
│   └── 4_Download.py        # Download results page
├── components/               # Reusable UI components
│   ├── __init__.py
│   ├── file_uploader.py     # File upload widget
│   ├── parameter_form.py    # Parameter configuration form
│   └── visualization.py     # Result visualization components
├── utils/                    # Frontend utilities
│   ├── __init__.py
│   ├── validators.py        # Input validation functions
│   └── formatters.py        # Data formatting utilities
└── requirements.txt          # Python dependencies
```

### How Streamlit Works

Streamlit is a Python framework for building interactive web applications. Key concepts:

1. **Script Reruns**: Every user interaction reruns the entire script from top to bottom
2. **Session State**: Use `st.session_state` to persist data between reruns
3. **Caching**: Use `@st.cache_data` to cache expensive computations
4. **Widgets**: Interactive elements (buttons, sliders, file uploaders) that trigger reruns

### Data Flow

```
User uploads file in Streamlit
    ↓
File saved to temporary location
    ↓
User configures parameters in Streamlit form
    ↓
User clicks "Run Analysis" button
    ↓
Frontend calls backend/api/r_executor.py
    ↓
Python API executes R script (backend team's code)
    ↓
Backend writes results to backend/results/
    ↓
Frontend calls backend/api/result_parser.py
    ↓
Frontend displays visualizations
    ↓
User downloads results
```

## Getting Started

### 1. Environment Setup

```bash
# Navigate to project root
cd /Users/hansonwen/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Install frontend dependencies
pip install -r frontend/requirements.txt

# Verify Streamlit installation
streamlit hello
```

### 2. Run the Application

```bash
# From project root
streamlit run frontend/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Development Mode

When developing:
- Edit any .py file in frontend/
- Save the file
- Streamlit will detect changes and offer to rerun
- Click "Always rerun" for automatic updates

## Streamlit Application Structure

### Main Application (streamlit_app.py)

This is the entry point. It should:
- Set page configuration
- Display title and description
- Load the home page
- Handle navigation if needed

Example structure:
```python
import streamlit as st

st.set_page_config(
    page_title="CopyKAT CNV Analysis",
    page_icon="DNA",
    layout="wide"
)

st.title("CopyKAT CNV Analysis Dashboard")
st.markdown("Analyze copy number variations from single-cell RNA-seq data")

# Main content
# ... your code here ...
```

### Multi-Page Structure

Streamlit automatically creates a sidebar navigation from files in `pages/`:

- `1_Upload.py` -> "Upload" page
- `2_Configure.py` -> "Configure" page  
- `3_Results.py` -> "Results" page
- `4_Download.py` -> "Download" page

Each page is a standalone Python script that runs when selected.

### Session State Management

Use session state to share data between pages:

```python
# Store uploaded file
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Store analysis results
if 'results' not in st.session_state:
    st.session_state.results = None

# Store configuration
if 'config' not in st.session_state:
    st.session_state.config = {}
```

## Backend Integration

### Calling the Backend API

You will interact with the backend through Python API files in `backend/api/`:

#### 1. Running Analysis

```python
from backend.api.r_executor import run_copykat_analysis

# Prepare parameters
params = {
    'input_file': '/path/to/data.txt.gz',
    'sample_name': 'my_sample',
    'genome': 'hg20',
    'n_cores': 4,
    # ... other parameters
}

# Run analysis (this calls R script)
result = run_copykat_analysis(params)

if result['success']:
    st.success("Analysis complete!")
    st.session_state.results = result['output_dir']
else:
    st.error(f"Analysis failed: {result['error']}")
```

#### 2. Monitoring Progress

```python
from backend.api.status_monitor import monitor_analysis_progress

# Show progress while R script runs
progress_bar = st.progress(0)
status_text = st.empty()

for status in monitor_analysis_progress(process_id):
    progress_bar.progress(status['progress'])
    status_text.text(status['message'])
```

#### 3. Parsing Results

```python
from backend.api.result_parser import parse_copykat_results

# Load and parse results
output_dir = st.session_state.results
results = parse_copykat_results(output_dir)

# Results dict contains:
# - predictions: DataFrame of cell classifications
# - heatmap_path: Path to CNV heatmap image
# - summary: Dict of statistics
```

### API Contract

The backend API expects and returns specific data formats defined in `shared/schemas/`:

**Input Schema** (what you send to backend):
```json
{
    "input_file": "/path/to/file.txt.gz",
    "sample_name": "sample_001",
    "genome": "hg20",
    "ngene_chr": 5,
    "n_cores": 4,
    "output_dir": "/path/to/output"
}
```

**Output Schema** (what backend returns):
```json
{
    "success": true,
    "output_dir": "/path/to/results",
    "predictions_file": "sample_001_copykat_prediction.txt",
    "heatmap_file": "sample_001_copykat_heatmap.jpeg",
    "summary": {
        "n_cells": 500,
        "n_aneuploid": 300,
        "n_diploid": 200
    }
}
```

## Component Development

### File Uploader Component

See `components/file_uploader.py` for the template. Key features:

- Accept .txt, .csv, .tsv, .gz files
- Validate file format
- Preview data (first few rows)
- Store in session state

```python
import streamlit as st
import pandas as pd

def file_uploader_component():
    uploaded_file = st.file_uploader(
        "Upload Expression Matrix",
        type=['txt', 'csv', 'tsv', 'gz'],
        help="Upload your gene expression matrix (genes x cells)"
    )
    
    if uploaded_file:
        # Save to session state
        st.session_state.uploaded_file = uploaded_file
        
        # Preview
        df = pd.read_csv(uploaded_file, sep='\t', index_col=0, nrows=5)
        st.success(f"Loaded: {df.shape[0]} genes x {df.shape[1]} cells (preview)")
        
        with st.expander("Preview Data"):
            st.dataframe(df)
    
    return uploaded_file
```

### Parameter Form Component

See `components/parameter_form.py`. Create form with all CopyKAT parameters:

```python
def parameter_form_component():
    with st.form("parameters"):
        st.subheader("Analysis Parameters")
        
        # Basic parameters
        sample_name = st.text_input("Sample Name", value="sample_01")
        genome = st.selectbox("Genome", options=["hg20", "mm10"])
        
        # Advanced parameters
        with st.expander("Advanced Parameters"):
            ngene_chr = st.slider("Min Genes per Chromosome", 1, 20, 5)
            win_size = st.slider("Window Size", 10, 150, 25)
            n_cores = st.slider("CPU Cores", 1, 8, 4)
        
        submit = st.form_submit_button("Run Analysis")
        
        if submit:
            params = {
                'sample_name': sample_name,
                'genome': genome,
                'ngene_chr': ngene_chr,
                'win_size': win_size,
                'n_cores': n_cores
            }
            return params
    
    return None
```

### Visualization Component

See `components/visualization.py`. Display results:

```python
def display_results(results):
    st.header("Analysis Results")
    
    # Display summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cells", results['summary']['n_cells'])
    with col2:
        st.metric("Aneuploid", results['summary']['n_aneuploid'])
    with col3:
        st.metric("Diploid", results['summary']['n_diploid'])
    
    # Display heatmap
    st.subheader("CNV Heatmap")
    st.image(results['heatmap_path'])
    
    # Display predictions table
    st.subheader("Cell Classifications")
    predictions_df = pd.read_csv(results['predictions_file'], sep='\t')
    st.dataframe(predictions_df)
```

## UI/UX Requirements

Reference the detailed design specifications in `docs/05_STREAMLIT_DASHBOARD_DESIGN.md`.

### Key Requirements

1. **Simple and Intuitive**
   - Clear navigation
   - Helpful tooltips on every widget
   - Progress indicators for long operations

2. **Informative Feedback**
   - Success/error messages
   - Validation warnings
   - Estimated runtime

3. **Professional Appearance**
   - Consistent styling
   - Proper spacing
   - Clean layout

4. **Responsive Design**
   - Works on different screen sizes
   - Use st.columns() for layout
   - Sidebar for parameters

### Widget Selection Guide

- **File Upload**: `st.file_uploader()`
- **Text Input**: `st.text_input()` for sample names
- **Dropdowns**: `st.selectbox()` for genome, distance metric
- **Sliders**: `st.slider()` for numeric parameters
- **Checkboxes**: `st.checkbox()` for boolean options
- **Buttons**: `st.button()` for actions
- **Forms**: `st.form()` to group inputs

### Validation and Error Handling

Always validate user inputs:

```python
from utils.validators import validate_expression_matrix

def validate_file(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, sep='\t', index_col=0)
        
        validation = validate_expression_matrix(df)
        
        if validation['errors']:
            for error in validation['errors']:
                st.error(error)
            return False
        
        if validation['warnings']:
            for warning in validation['warnings']:
                st.warning(warning)
        
        st.success("File validation passed!")
        return True
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return False
```

## Testing Your Code

### Manual Testing

1. **Test file upload**
   - Try different file formats (.txt, .gz, .csv)
   - Try invalid files
   - Check preview displays correctly

2. **Test parameter form**
   - Verify all widgets work
   - Check validation
   - Ensure defaults are reasonable

3. **Test analysis flow**
   - Upload file -> Configure -> Run -> View Results
   - Test error cases
   - Verify progress indicators

4. **Test on different data**
   - Use glioblastoma dataset
   - Use melanoma dataset
   - Test with small subset

### Using Test Data

```python
# Test with glioblastoma data
test_file = "backend/data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"
```

## Common Tasks

### Task 1: Add a New Parameter Widget

1. Open `components/parameter_form.py`
2. Add widget to the form
3. Add to returned params dictionary
4. Update schema in `shared/schemas/input_schema.json`

### Task 2: Display a New Visualization

1. Check if backend generates the plot
2. Get file path from result parser
3. Add display code to `components/visualization.py`
4. Use `st.image()` or `st.pyplot()`

### Task 3: Add Input Validation

1. Open `utils/validators.py`
2. Add validation function
3. Call from component
4. Display error with `st.error()`

### Task 4: Handle Errors Gracefully

```python
try:
    result = run_analysis(params)
except Exception as e:
    st.error(f"Analysis failed: {str(e)}")
    st.info("Please check your input file and parameters")
    st.stop()
```

## Troubleshooting

### Streamlit Not Starting

```bash
# Check if installed
pip list | grep streamlit

# Reinstall if needed
pip install --upgrade streamlit
```

### Import Errors

```bash
# Make sure you're in project root
cd /Users/hansonwen/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Run from root
streamlit run frontend/streamlit_app.py
```

### Backend API Not Found

Make sure backend API files exist:
- `backend/api/r_executor.py`
- `backend/api/result_parser.py`
- `backend/api/status_monitor.py`

If they don't exist, ask the backend team.

### Session State Issues

```python
# Always initialize session state at top
if 'my_variable' not in st.session_state:
    st.session_state.my_variable = default_value
```

### Page Not Updating

- Check for errors in terminal where Streamlit is running
- Click "Always rerun" in browser
- Hard refresh browser (Cmd+Shift+R on Mac)

## Getting Help

### Resources

1. **Streamlit Documentation**: https://docs.streamlit.io/
2. **Project Design Doc**: `docs/05_STREAMLIT_DASHBOARD_DESIGN.md`
3. **Python-R Integration**: `docs/06_PYTHON_R_INTEGRATION.md`
4. **Troubleshooting Guide**: `docs/07_TROUBLESHOOTING.md`

### Ask for Help

- Check documentation first
- Search Streamlit docs
- Ask in team channel
- Tag backend team if API questions
- Create GitHub issue if you find a bug

## Next Steps

1. Review `docs/05_STREAMLIT_DASHBOARD_DESIGN.md` for detailed design specs
2. Look at skeleton code in `frontend/` directory
3. Start with `streamlit_app.py` - create the home page
4. Then work on `pages/1_Upload.py` - file upload functionality
5. Test frequently and commit working code

Good luck! You've got this!

