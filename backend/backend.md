# Backend Development Guide

Welcome, Rajan and Jimmy! This guide contains everything you need to develop the R backend for the CNV-Cancer-RNAseq-analysis project.

## Table of Contents

1. [Your Role and Responsibilities](#your-role-and-responsibilities)
2. [Backend Architecture](#backend-architecture)
3. [Getting Started](#getting-started)
4. [R Script Structure](#r-script-structure)
5. [Frontend Integration](#frontend-integration)
6. [CopyKAT Integration](#copykat-integration)
7. [Data Flow](#data-flow)
8. [Development Guidelines](#development-guidelines)
9. [Testing Your Code](#testing-your-code)
10. [Common Tasks](#common-tasks)
11. [Troubleshooting](#troubleshooting)

## Your Role and Responsibilities

As the Backend Team, you are responsible for:

- Implementing R scripts for CopyKAT analysis
- Configuring CopyKAT parameters appropriately
- Preprocessing and validating input data
- Running CNV analysis pipeline
- Generating output files and visualizations
- Creating analysis reports
- Handling errors and logging
- Ensuring reproducibility

You will NOT be writing Streamlit UI code. The frontend team handles all Python web interface work.

## Backend Architecture

### Directory Structure

```
backend/
├── backend.md                          # This file
├── data/                               # Data files (moved from root)
│   ├── raw/
│   │   ├── glioblastomas_compressed/
│   │   └── melanoma_compressed/
│   └── DATA_GUIDE.md                   # Data documentation
├── results/                            # Analysis outputs (moved from root)
├── r_scripts/                          # Your R scripts
│   ├── example_complete_workflow.R     # COMPLETE WORKING EXAMPLE
│   ├── copykat_analysis.R             # Main analysis script (TO IMPLEMENT)
│   ├── copykat_utils.R                # Utility functions (TO IMPLEMENT)
│   ├── data_preprocessing.R           # Data preprocessing (TO IMPLEMENT)
│   └── copykat_report.Rmd             # Report template (TO IMPLEMENT)
└── api/                                # Python-R bridge (for reference)
    ├── r_executor.py                   # Calls your R scripts
    ├── result_parser.py                # Parses your outputs
    └── status_monitor.py               # Monitors execution
```

### How Python Calls Your R Code

```
User clicks "Run Analysis" in Streamlit
    ↓
Python receives parameters
    ↓
backend/api/r_executor.py is called
    ↓
Python builds command: Rscript backend/r_scripts/copykat_analysis.R [args]
    ↓
Your R script executes
    ↓
Your script writes outputs to backend/results/
    ↓
Your script exits with status code (0 = success, 1 = error)
    ↓
Python reads outputs from backend/results/
    ↓
Python returns results to frontend
```

## Getting Started

### 1. Environment Setup

```bash
# Activate conda environment
conda activate Project4-CNV-Cancer-RNAseq

# Verify R installation
which R

# Verify CopyKAT installation
R -e 'library(copykat)'
```

### 2. Review the Working Example

Before implementing new code, thoroughly review the complete working example:

```bash
# Open in RStudio or text editor
backend/r_scripts/example_complete_workflow.R
```

This file contains:
- Complete argument parsing
- Configuration management
- Data loading and validation
- Quality control
- Preprocessing
- CopyKAT execution
- Results processing
- Error handling
- Logging

### 3. Understand the Data

```bash
# Read the data guide
backend/data/DATA_GUIDE.md
```

Key points:
- Expression matrices are genes (rows) x cells (columns)
- Data may be raw counts or log-transformed
- Files are compressed (.gz format)
- Gene names are human (hg20) or mouse (mm10)

### 4. Test with Example Data

```bash
# Navigate to project root
cd /Users/hansonwen/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Run the working example
Rscript backend/r_scripts/example_complete_workflow.R \
  --input backend/data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  --name test_backend \
  --output backend/results \
  --genome hg20 \
  --cores 2
```

Results will be in `backend/results/test_backend_*/`

## R Script Structure

### Required Scripts

#### 1. copykat_analysis.R (Main Script)

This is the main entry point that Python will call.

**Purpose**: Run CopyKAT analysis from command line with arguments

**Input**: Command line arguments or config file
- `--input`: Path to expression matrix
- `--output`: Output directory
- `--name`: Sample name
- `--genome`: Genome version (hg20 or mm10)
- `--cores`: Number of CPU cores

**Output**: Results written to output directory
- `{sample}_copykat_prediction.txt`: Cell classifications
- `{sample}_copykat_CNA_results.txt`: CNV segments
- `{sample}_copykat_heatmap.jpeg`: Heatmap visualization
- `{sample}_report.html`: Analysis report

**Exit Code**: 0 on success, 1 on error

**Template Structure**:
```r
#!/usr/bin/env Rscript

# Load libraries
library(copykat)
source("backend/r_scripts/copykat_utils.R")

# Parse arguments
args <- parse_arguments()

# Load and validate data
data <- load_expression_matrix(args$input)
validation <- validate_data(data)

# Preprocess data
processed_data <- preprocess_data(data)

# Run CopyKAT
result <- run_copykat_analysis(processed_data, args)

# Save results
save_results(result, args$output, args$name)

# Exit with status
quit(save = "no", status = 0)
```

#### 2. copykat_utils.R (Utility Functions)

**Purpose**: Reusable functions for validation, preprocessing, analysis

**Functions to Implement**:

```r
# Data validation
validate_expression_matrix(data)
assess_data_quality(data)

# Preprocessing
detect_log_transform(data)
convert_log_to_counts(data, base = 2)
filter_cells(data, min_genes, min_umi, max_mt_percent)
filter_genes(data, min_cells)

# Analysis helpers
run_copykat_safe(data, params)

# Visualization
plot_qc_metrics(data, output_file)
plot_copykat_summary(result, output_file)

# Results processing
export_results_csv(result, output_dir, sample_name)
```

See `example_complete_workflow.R` for complete implementations.

#### 3. data_preprocessing.R (Preprocessing Pipeline)

**Purpose**: Prepare data for CopyKAT analysis

**Key Steps**:
1. Load raw expression matrix
2. Detect if log-transformed
3. Convert to counts if needed
4. Filter low-quality cells
5. Filter low-abundance genes
6. Generate QC plots

#### 4. copykat_report.Rmd (R Markdown Report)

**Purpose**: Generate HTML report with results

**Sections**:
- Analysis Overview
- Data Quality Metrics
- CopyKAT Parameters
- Cell Classification Results
- CNV Heatmap
- Chromosome-level Summary
- Conclusions

## Frontend Integration

### How Frontend Calls Your Code

The frontend team will call your R scripts through Python subprocess:

```python
# Python code (you don't write this)
import subprocess

command = [
    "Rscript",
    "backend/r_scripts/copykat_analysis.R",
    "--input", input_file,
    "--output", output_dir,
    "--name", sample_name,
    "--genome", genome,
    "--cores", str(n_cores)
]

result = subprocess.run(command, capture_output=True, text=True)

if result.returncode == 0:
    # Success - read outputs
else:
    # Error - result.stderr contains error message
```

### Your Responsibilities for Integration

1. **Accept Command Line Arguments**
   - Parse all required and optional parameters
   - Provide clear error messages for invalid arguments

2. **Write to Expected Output Location**
   - Use the output directory provided via `--output`
   - Use the sample name provided via `--name`
   - Follow naming convention: `{output_dir}/{sample_name}_copykat_*.txt`

3. **Return Proper Exit Codes**
   - Exit with 0 on success
   - Exit with 1 on error
   - Use `quit(save = "no", status = code)`

4. **Provide Logging and Progress**
   - Use `logger` package for logging
   - Write logs to `{output_dir}/logs/analysis.log`
   - Print progress to stdout

5. **Handle Errors Gracefully**
   - Catch errors with `tryCatch()`
   - Log error messages
   - Don't leave partial outputs

### Expected Input/Output Formats

Refer to `shared/schemas/input_schema.json` and `output_schema.json`.

**Input** (via command line arguments):
```bash
--input /path/to/data.txt.gz
--output backend/results
--name sample_001
--genome hg20
--ngene_chr 5
--win_size 25
--cores 4
```

**Output Files** (written by your script):
```
backend/results/sample_001_TIMESTAMP/
├── logs/
│   └── analysis.log
├── plots/
│   ├── qc_metrics.pdf
│   └── copykat_summary.pdf
├── sample_001_copykat_prediction.txt
├── sample_001_copykat_CNA_results.txt
├── sample_001_copykat_heatmap.jpeg
├── sample_001_copykat_with_genes_heatmap.pdf
└── sample_001_report.html
```

## CopyKAT Integration

### CopyKAT Function Call

```r
library(copykat)

result <- copykat(
  rawmat = expression_matrix,        # genes x cells matrix
  id.type = "S",                     # "S" for gene Symbol, "E" for Ensembl
  cell.line = "no",                  # "no" for tumor, "yes" for cell line
  ngene.chr = 5,                     # min genes per chromosome
  LOW.DR = 0.05,                     # detection rate for smoothing
  UP.DR = 0.10,                      # detection rate for segmentation
  win.size = 25,                     # window size (genes)
  KS.cut = 0.1,                      # segmentation sensitivity
  sam.name = "sample_001",           # sample name
  distance = "euclidean",            # distance metric
  norm.cell.names = "",              # known normal cell names (optional)
  output.seg = "FALSE",              # generate .seg file for IGV
  plot.genes = "TRUE",               # show gene names in heatmap
  genome = "hg20",                   # "hg20" for human, "mm10" for mouse
  n.cores = 4                        # parallel processing
)
```

### CopyKAT Parameters Explained

See `docs/03_PARAMETERS_REFERENCE.md` for complete details.

**Critical Parameters**:

- `ngene_chr`: Cells with fewer genes per chromosome are filtered. Default: 5
- `LOW.DR`: Minimum detection rate for gene smoothing. Default: 0.05
- `UP.DR`: Minimum detection rate for segmentation. Must be >= LOW.DR. Default: 0.10
- `win.size`: Genes per window for smoothing. Smaller = higher resolution. Default: 25
- `KS.cut`: Segmentation sensitivity. Lower = more breakpoints. Default: 0.1

**Common Pitfalls**:
- UP.DR must be >= LOW.DR (will error otherwise)
- Too small win.size causes noisy results
- Too large ngene_chr filters too many cells
- Wrong genome version produces incorrect results

### CopyKAT Output Structure

```r
result <- list(
  prediction = data.frame(
    cell.names = c("cell1", "cell2", ...),
    copykat.pred = c("aneuploid", "diploid", ...),
    copykat.confidence = c(0.95, 0.82, ...)
  ),
  CNV.matrix = matrix(...),        # Copy number matrix
  CNAmat = list(...)               # Segmentation results
)
```

**Output Files** (generated by CopyKAT):
- `{sample}_copykat_prediction.txt`: Cell classifications
- `{sample}_copykat_CNA_results.txt`: Segment-level CNV calls
- `{sample}_copykat_CNA_raw_results_gene_by_cell.txt`: Gene-level CNV
- `{sample}_copykat_heatmap.jpeg`: CNV heatmap
- `{sample}_copykat_clustering_results.rds`: Clustering object

## Data Flow

### Complete Analysis Workflow

```
1. DATA LOADING
   - Read expression matrix from .gz file
   - Check dimensions (genes x cells)
   - Verify row/column names exist

2. DATA VALIDATION
   - Check for NA/Inf values
   - Verify minimum cell count (>= 50)
   - Verify minimum gene count (>= 1000)
   - Check value ranges

3. QUALITY CONTROL
   - Calculate genes per cell
   - Calculate UMI per cell
   - Calculate mitochondrial percentage
   - Generate QC plots

4. PREPROCESSING
   - Detect if log-transformed
   - Convert to counts if needed
   - Filter low-quality cells
   - Filter low-abundance genes

5. COPYKAT ANALYSIS
   - Set working directory to output folder
   - Configure parameters
   - Run copykat() function
   - Handle warnings/errors

6. RESULTS PROCESSING
   - Summarize cell classifications
   - Calculate chromosome-level alterations
   - Generate summary plots
   - Export CSV files

7. REPORT GENERATION
   - Render R Markdown report
   - Include all visualizations
   - Summarize findings

8. CLEANUP
   - Verify all outputs created
   - Return to original directory
   - Exit with proper status code
```

## Development Guidelines

### Code Style

Follow R tidyverse style guide:

```r
# Good variable names
expression_matrix <- load_data(file_path)
n_cells <- ncol(expression_matrix)

# Use <- for assignment, not =
result <- run_analysis(data)

# Function names: snake_case
calculate_qc_metrics <- function(data) {
  # Function body
}

# Add documentation
#' Calculate quality control metrics
#'
#' @param data Expression matrix (genes x cells)
#' @return List of QC metrics
#' @export
calculate_qc_metrics <- function(data) {
  # ...
}
```

### Error Handling

Always use `tryCatch()`:

```r
result <- tryCatch(
  {
    # Main code
    copykat_result <- copykat(rawmat = data, ...)
    list(success = TRUE, result = copykat_result, error = NULL)
  },
  error = function(e) {
    log_error("Analysis failed: {conditionMessage(e)}")
    list(success = FALSE, result = NULL, error = conditionMessage(e))
  },
  warning = function(w) {
    log_warn("Warning: {conditionMessage(w)}")
    # Continue despite warning
    suppressWarnings(copykat(rawmat = data, ...))
  }
)

if (!result$success) {
  quit(save = "no", status = 1)
}
```

### Logging

Use the `logger` package:

```r
library(logger)

# Setup logging
log_file <- file.path(output_dir, "logs", "analysis.log")
log_appender(appender_tee(log_file))  # Log to file and console
log_threshold(INFO)

# Use throughout script
log_info("Starting analysis")
log_info("Loaded {n_genes} genes and {n_cells} cells")
log_warn("Low cell count detected")
log_error("Failed to load data: {error_message}")
```

### Configuration Management

Support both CLI arguments and config files:

```r
# Load from YAML config
if (file.exists(config_file)) {
  config <- yaml::read_yaml(config_file)
  input_file <- config$input$file
  genome <- config$copykat$genome
}

# Override with CLI arguments
args <- commandArgs(trailingOnly = TRUE)
if ("--input" %in% args) {
  input_file <- args[which(args == "--input") + 1]
}
```

## Testing Your Code

### Manual Testing

```bash
# Test with glioblastoma data
Rscript backend/r_scripts/copykat_analysis.R \
  --input backend/data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  --name glio_test \
  --output backend/results \
  --genome hg20 \
  --cores 2

# Check outputs
ls -la backend/results/glio_test_*/

# Verify prediction file
head backend/results/glio_test_*/glio_test_copykat_prediction.txt
```

### Test Cases

1. **Valid input, all parameters**
2. **Minimal parameters** (use defaults)
3. **Invalid input file** (should error gracefully)
4. **Wrong genome version** (should warn/error)
5. **Log-transformed data** (should auto-detect and convert)
6. **Small dataset** (<100 cells, should warn)

### Validation Checklist

- [ ] Script accepts all required arguments
- [ ] Script creates output directory
- [ ] Script writes all expected output files
- [ ] Log file contains progress messages
- [ ] Exit code is 0 on success, 1 on error
- [ ] Error messages are clear and helpful
- [ ] Works with both glioblastoma and melanoma data

## Common Tasks

### Task 1: Add a New Parameter

1. Add argument parsing in `copykat_analysis.R`
2. Pass to CopyKAT function
3. Document in help message
4. Update schema in `shared/schemas/input_schema.json`

### Task 2: Implement a Preprocessing Function

1. Open `copykat_utils.R`
2. Add function with documentation
3. Add unit tests if possible
4. Use in main pipeline

### Task 3: Generate a New Visualization

1. Create plot in `copykat_utils.R`
2. Save to `{output_dir}/plots/`
3. Include in report

### Task 4: Handle a New Data Format

1. Add loader function in `data_preprocessing.R`
2. Detect format based on file extension
3. Convert to standard matrix format
4. Test with example file

## Troubleshooting

### CopyKAT Errors

**Error: "UP.DR must be >= LOW.DR"**
- Check parameter values
- Ensure UP.DR >= LOW.DR

**Error: "Too few cells"**
- CopyKAT needs at least 50 cells
- Check cell filtering settings

**Error: "Cannot find reference"**
- Check genome parameter ("hg20" or "mm10")
- Ensure correct case

### Data Loading Issues

**Error: "File not found"**
- Check file path is correct
- Use absolute paths or paths relative to project root
- Verify file exists: `file.exists(path)`

**Error: "Cannot read compressed file"**
- Use `gzfile()` for .gz files
- Use `read.table(gzfile(path), ...)`

### Memory Issues

**Error: "Cannot allocate vector of size X"**
- Reduce number of cells (subset for testing)
- Reduce n.cores parameter
- Close other applications
- Use machine with more RAM

### Integration Issues

**Frontend can't find outputs**
- Check output directory is correct
- Verify file naming convention
- Ensure script completed successfully (exit code 0)

**Frontend can't parse results**
- Check output format matches schema
- Verify all expected files were created
- Check for partial outputs

## Getting Help

### Resources

1. **Data Guide**: `backend/data/DATA_GUIDE.md`
2. **CopyKAT Documentation**: 
   - `docs/01_COPYKAT_OVERVIEW.md`
   - `docs/02_ALGORITHM_EXPLAINED.md`
   - `docs/03_PARAMETERS_REFERENCE.md`
3. **Parameter Reference**: `docs/10_PARAMETER_QUICK_REFERENCE.md`
4. **Tutorials**: `docs/08_BEGINNER_TUTORIAL.md`
5. **Troubleshooting**: `docs/07_TROUBLESHOOTING.md`

### Ask for Help

- Check documentation first
- Review example_complete_workflow.R
- Search existing issues
- Ask in team channel
- Tag frontend team if integration questions
- Create GitHub issue for bugs

## Next Steps

1. Review `example_complete_workflow.R` thoroughly
2. Read `backend/data/DATA_GUIDE.md`
3. Test the example script with both datasets
4. Implement `copykat_analysis.R` skeleton
5. Implement key utility functions
6. Test with glioblastoma data
7. Test with melanoma data
8. Document your code

You've got the complete working example. Use it as your reference and template. Good luck!

