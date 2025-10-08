# Python-R Integration Guide for CopyKAT

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Using subprocess Module](#using-subprocess-module)
3. [Complete R Wrapper Script](#complete-r-wrapper-script)
4. [Python Integration Code](#python-integration-code)
5. [Data Format Conversions](#data-format-conversions)
6. [Error Handling](#error-handling)
7. [Process Monitoring](#process-monitoring)
8. [Production-Ready Example](#production-ready-example)

---

## Architecture Overview

### The PRD Approach

According to the PRD Section 5.2, the data flow is:

```
Streamlit Frontend (Python)
         ↓
    subprocess.run()
         ↓
    R Script (run_copykat.R)
         ↓
    CopyKAT Analysis
         ↓
    Output Files (results/)
         ↓
    Python reads outputs
         ↓
    Streamlit displays results
```

### Why This Approach?

**Advantages**:
- Clean separation: Python for UI, R for analysis
- No complex bindings (rpy2) required
- Easy to debug each component
- Portable across systems

**Trade-offs**:
- File I/O overhead
- Process startup cost
- Temporary files needed

---

## Using subprocess Module

### Basic Pattern

```python
import subprocess

result = subprocess.run(
    ["Rscript", "script.R", "arg1", "arg2"],
    capture_output=True,
    text=True,
    timeout=3600  # 1 hour
)

if result.returncode == 0:
    print("Success!")
    print(result.stdout)
else:
    print("Error!")
    print(result.stderr)
```

### Key Parameters

| Parameter | Purpose | Value |
|-----------|---------|-------|
| `capture_output` | Capture stdout/stderr | `True` |
| `text` | Return strings (not bytes) | `True` |
| `timeout` | Kill if exceeds (seconds) | `3600` |
| `check` | Raise exception on error | `False` (handle manually) |
| `cwd` | Working directory | Path to project |

---

## Complete R Wrapper Script

### File: `r_scripts/run_copykat.R`

```r
#!/usr/bin/env Rscript

# CopyKAT Wrapper Script
# Called from Python with command-line arguments

# Load required libraries
suppressPackageStartupMessages({
  library(copykat)
})

# =======================
# Parse Command Line Args
# =======================

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  cat("Usage: Rscript run_copykat.R <input_file> <output_dir> [params...]\n")
  cat("\nRequired:\n")
  cat("  input_file: Path to expression matrix\n")
  cat("  output_dir: Directory for output files\n")
  cat("\nOptional (in order):\n")
  cat("  sam_name: Sample name (default: sample)\n")
  cat("  id_type: S or E (default: S)\n")
  cat("  cell_line: yes or no (default: no)\n")
  cat("  ngene_chr: integer (default: 5)\n")
  cat("  low_dr: float (default: 0.05)\n")
  cat("  up_dr: float (default: 0.1)\n")
  cat("  win_size: integer (default: 25)\n")
  cat("  ks_cut: float (default: 0.1)\n")
  cat("  distance: euclidean, pearson, or spearman (default: euclidean)\n")
  cat("  genome: hg20 or mm10 (default: hg20)\n")
  cat("  n_cores: integer (default: 1)\n")
  cat("  output_seg: TRUE or FALSE (default: FALSE)\n")
  cat("  plot_genes: TRUE or FALSE (default: TRUE)\n")
  quit(status = 1)
}

# Required arguments
input_file <- args[1]
output_dir <- args[2]

# Optional arguments with defaults
sam_name <- if (length(args) >= 3) args[3] else "sample"
id_type <- if (length(args) >= 4) args[4] else "S"
cell_line <- if (length(args) >= 5) args[5] else "no"
ngene_chr <- if (length(args) >= 6) as.integer(args[6]) else 5
low_dr <- if (length(args) >= 7) as.numeric(args[7]) else 0.05
up_dr <- if (length(args) >= 8) as.numeric(args[8]) else 0.1
win_size <- if (length(args) >= 9) as.integer(args[9]) else 25
ks_cut <- if (length(args) >= 10) as.numeric(args[10]) else 0.1
distance <- if (length(args) >= 11) args[11] else "euclidean"
genome <- if (length(args) >= 12) args[12] else "hg20"
n_cores <- if (length(args) >= 13) as.integer(args[13]) else 1
output_seg <- if (length(args) >= 14) args[14] else "FALSE"
plot_genes <- if (length(args) >= 15) args[15] else "TRUE"

# =======================
# Validation
# =======================

cat("======================================\n")
cat("CopyKAT Wrapper Script\n")
cat("======================================\n\n")

# Check input file exists
if (!file.exists(input_file)) {
  cat("ERROR: Input file not found:", input_file, "\n")
  quit(status = 1)
}

# Create output directory
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
  cat("Created output directory:", output_dir, "\n")
}

# Print parameters
cat("Parameters:\n")
cat(sprintf("  Input file:    %s\n", input_file))
cat(sprintf("  Output dir:    %s\n", output_dir))
cat(sprintf("  Sample name:   %s\n", sam_name))
cat(sprintf("  ID type:       %s\n", id_type))
cat(sprintf("  Cell line:     %s\n", cell_line))
cat(sprintf("  ngene.chr:     %d\n", ngene_chr))
cat(sprintf("  LOW.DR:        %.3f\n", low_dr))
cat(sprintf("  UP.DR:         %.3f\n", up_dr))
cat(sprintf("  win.size:      %d\n", win_size))
cat(sprintf("  KS.cut:        %.3f\n", ks_cut))
cat(sprintf("  distance:      %s\n", distance))
cat(sprintf("  genome:        %s\n", genome))
cat(sprintf("  n.cores:       %d\n", n_cores))
cat(sprintf("  output.seg:    %s\n", output_seg))
cat(sprintf("  plot.genes:    %s\n", plot_genes))
cat("\n")

# =======================
# Load Data
# =======================

cat("Loading expression matrix...\n")

tryCatch({
  # Detect file format
  if (grepl("\\.gz$", input_file)) {
    raw_data <- read.table(gzfile(input_file),
                           header = TRUE,
                           row.names = 1,
                           sep = "\t",
                           check.names = FALSE)
  } else if (grepl("\\.csv$", input_file)) {
    raw_data <- read.csv(input_file,
                         row.names = 1,
                         check.names = FALSE)
  } else {
    raw_data <- read.table(input_file,
                           header = TRUE,
                           row.names = 1,
                           sep = "\t",
                           check.names = FALSE)
  }

  cat(sprintf("  Loaded: %d genes × %d cells\n", nrow(raw_data), ncol(raw_data)))

  # Basic validation
  if (nrow(raw_data) < 1000) {
    cat("WARNING: Less than 1000 genes. Results may be unreliable.\n")
  }

  if (ncol(raw_data) < 50) {
    cat("WARNING: Less than 50 cells. CopyKAT needs at least 50 cells.\n")
  }

}, error = function(e) {
  cat("ERROR loading data:", conditionMessage(e), "\n")
  quit(status = 1)
})

# =======================
# Run CopyKAT
# =======================

cat("\nRunning CopyKAT analysis...\n")
cat("This may take 5-30 minutes depending on dataset size.\n\n")

# Change to output directory so files are created there
original_wd <- getwd()
setwd(output_dir)

tryCatch({
  result <- copykat(
    rawmat = raw_data,
    id.type = id_type,
    cell.line = cell_line,
    ngene.chr = ngene_chr,
    LOW.DR = low_dr,
    UP.DR = up_dr,
    win.size = win_size,
    KS.cut = ks_cut,
    sam.name = sam_name,
    distance = distance,
    output.seg = output_seg,
    plot.genes = plot_genes,
    genome = genome,
    n.cores = n_cores
  )

  cat("\n======================================\n")
  cat("CopyKAT analysis completed successfully!\n")
  cat("======================================\n\n")

  # Print summary
  if (!is.null(result$prediction)) {
    cat("Cell Classifications:\n")
    print(table(result$prediction$copykat.pred))
    cat("\n")
  }

  # List output files
  cat("Output files created:\n")
  output_files <- list.files(pattern = sprintf("^%s_copykat", sam_name))
  for (f in output_files) {
    cat(sprintf("  - %s\n", f))
  }

  cat("\nAnalysis complete!\n")

}, error = function(e) {
  cat("\n======================================\n")
  cat("ERROR during CopyKAT analysis:\n")
  cat("======================================\n")
  cat(conditionMessage(e), "\n\n")

  cat("Troubleshooting tips:\n")
  cat("  - Check data quality (LOW.DR/UP.DR may need adjustment)\n")
  cat("  - Ensure sufficient memory (large datasets need 8-16GB)\n")
  cat("  - Verify genome matches data (hg20 for human, mm10 for mouse)\n")
  cat("  - See troubleshooting guide for solutions\n\n")

  quit(status = 1)
}, finally = {
  # Restore original working directory
  setwd(original_wd)
})

# Exit successfully
quit(status = 0)
```

---

## Python Integration Code

### Basic Integration Function

```python
import subprocess
import os
from pathlib import Path

def run_copykat(
    input_file: str,
    output_dir: str,
    sam_name: str = "sample",
    params: dict = None
) -> dict:
    """
    Run CopyKAT analysis via R subprocess.

    Args:
        input_file: Path to expression matrix
        output_dir: Directory for output files
        sam_name: Sample name for outputs
        params: Dictionary of CopyKAT parameters

    Returns:
        dict with 'success', 'stdout', 'stderr', 'output_files'
    """

    # Default parameters
    default_params = {
        'id_type': 'S',
        'cell_line': 'no',
        'ngene_chr': 5,
        'low_dr': 0.05,
        'up_dr': 0.1,
        'win_size': 25,
        'ks_cut': 0.1,
        'distance': 'euclidean',
        'genome': 'hg20',
        'n_cores': 4,
        'output_seg': 'FALSE',
        'plot_genes': 'TRUE'
    }

    # Merge with provided params
    if params:
        default_params.update(params)

    # Build command
    cmd = [
        "Rscript",
        "r_scripts/run_copykat.R",
        input_file,
        output_dir,
        sam_name,
        default_params['id_type'],
        default_params['cell_line'],
        str(default_params['ngene_chr']),
        str(default_params['low_dr']),
        str(default_params['up_dr']),
        str(default_params['win_size']),
        str(default_params['ks_cut']),
        default_params['distance'],
        default_params['genome'],
        str(default_params['n_cores']),
        default_params['output_seg'],
        default_params['plot_genes']
    ]

    # Run subprocess
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour
            check=False  # Don't raise exception, handle manually
        )

        # Check success
        success = (result.returncode == 0)

        # Find output files
        output_files = []
        if success:
            pattern = f"{sam_name}_copykat*"
            output_files = list(Path(output_dir).glob(pattern))

        return {
            'success': success,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'output_files': [str(f) for f in output_files]
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Analysis timed out after 1 hour',
            'output_files': []
        }

    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'output_files': []
        }
```

### Usage Example

```python
# Run CopyKAT
result = run_copykat(
    input_file="data/tumor_data.txt",
    output_dir="results",
    sam_name="patient_001",
    params={
        'ngene_chr': 5,
        'low_dr': 0.05,
        'up_dr': 0.1,
        'n_cores': 8
    }
)

# Check result
if result['success']:
    print("Analysis completed!")
    print(f"Output files: {result['output_files']}")
else:
    print("Analysis failed!")
    print(f"Error: {result['stderr']}")
```

---

## Data Format Conversions

### Python → R (Saving for R)

```python
import pandas as pd

# Python DataFrame
df = pd.read_csv("input.csv", index_col=0)

# Save for R (tab-delimited)
df.to_csv("temp_for_r.txt", sep="\t")

# Or compressed
df.to_csv("temp_for_r.txt.gz", sep="\t", compression="gzip")
```

### R → Python (Reading R outputs)

```python
import pandas as pd

# Read CopyKAT prediction table
predictions = pd.read_csv(
    "results/sample_copykat_prediction.txt",
    sep="\t",
    index_col=0
)

# Read CNV matrix
cnv_matrix = pd.read_csv(
    "results/sample_copykat_CNA_results.txt",
    sep="\t",
    index_col=0
)

# Process results
aneuploid_cells = predictions[predictions['copykat.pred'] == 'aneuploid']
print(f"Found {len(aneuploid_cells)} aneuploid cells")
```

---

## Error Handling

### Comprehensive Error Handling

```python
def run_copykat_safe(input_file, output_dir, sam_name, params=None):
    """
    Run CopyKAT with comprehensive error handling.
    """

    # Validate inputs
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Check R availability
    try:
        subprocess.run(
            ["Rscript", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("Rscript not found. Please install R.")

    # Check CopyKAT package
    check_cmd = [
        "Rscript",
        "-e",
        "if (!require('copykat', quietly=TRUE)) quit(status=1)"
    ]

    try:
        subprocess.run(check_cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("CopyKAT R package not installed. "
                         "Run: R -e 'remotes::install_github(\"navinlabcode/copykat\")'")

    # Run analysis
    result = run_copykat(input_file, output_dir, sam_name, params)

    # Parse errors
    if not result['success']:
        error_msg = result['stderr']

        if "low data quality" in error_msg:
            raise ValueError("Data quality too low. Try lowering LOW.DR and UP.DR parameters.")
        elif "memory" in error_msg.lower():
            raise MemoryError("Insufficient memory. Reduce dataset size or increase RAM.")
        elif "not found" in error_msg:
            raise FileNotFoundError(f"R script or data file issue: {error_msg}")
        else:
            raise RuntimeError(f"CopyKAT failed: {error_msg}")

    return result
```

---

## Process Monitoring

### Real-Time Output Streaming

```python
import subprocess
import threading

def run_copykat_streaming(input_file, output_dir, sam_name, params=None, callback=None):
    """
    Run CopyKAT with real-time output streaming.

    Args:
        callback: Function called with each output line
    """

    # Build command
    cmd = build_copykat_command(input_file, output_dir, sam_name, params)

    # Start process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )

    # Stream stdout
    def stream_output(pipe, prefix):
        for line in pipe:
            line = line.strip()
            if callback:
                callback(f"{prefix}: {line}")
            print(f"{prefix}: {line}")

    # Start threads for stdout and stderr
    stdout_thread = threading.Thread(
        target=stream_output,
        args=(process.stdout, "OUT")
    )
    stderr_thread = threading.Thread(
        target=stream_output,
        args=(process.stderr, "ERR")
    )

    stdout_thread.start()
    stderr_thread.start()

    # Wait for completion
    process.wait()

    stdout_thread.join()
    stderr_thread.join()

    return process.returncode == 0
```

### Progress Estimation

```python
def estimate_progress(output_line):
    """
    Estimate progress from R output.
    """
    progress_map = {
        "step1": 0.1,
        "step 2": 0.2,
        "step 3": 0.3,
        "step 4": 0.5,
        "step 5": 0.6,
        "step 6": 0.7,
        "step 7": 0.8,
        "step 8": 0.9,
        "step 9": 0.95,
        "step 10": 1.0
    }

    for key, value in progress_map.items():
        if key in output_line.lower():
            return value

    return None

# Usage with Streamlit
import streamlit as st

progress_bar = st.progress(0)

def update_progress(line):
    progress = estimate_progress(line)
    if progress:
        progress_bar.progress(progress)

run_copykat_streaming(..., callback=update_progress)
```

---

## Production-Ready Example

### Complete Streamlit Integration

```python
import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path
import os

def main():
    st.title("CopyKAT CNV Analysis")

    # Upload
    uploaded_file = st.file_uploader("Upload Expression Matrix", type=["txt", "csv", "gz"])

    if uploaded_file:
        # Save uploaded file
        temp_input = "temp/input_data.txt"
        os.makedirs("temp", exist_ok=True)

        with open(temp_input, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Parameters
        with st.sidebar:
            st.header("Parameters")
            sam_name = st.text_input("Sample Name", "sample")
            ngene_chr = st.slider("Min genes/chr", 1, 20, 5)
            n_cores = st.slider("CPU Cores", 1, os.cpu_count(), 4)

        # Run button
        if st.button("Run CopyKAT"):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Build command
            cmd = [
                "Rscript",
                "r_scripts/run_copykat.R",
                temp_input,
                "results",
                sam_name,
                "S",          # id_type
                "no",         # cell_line
                str(ngene_chr),
                "0.05",       # low_dr
                "0.1",        # up_dr
                "25",         # win_size
                "0.1",        # ks_cut
                "euclidean",  # distance
                "hg20",       # genome
                str(n_cores),
                "FALSE",      # output_seg
                "TRUE"        # plot_genes
            ]

            # Run with monitoring
            status_text.text("Running CopyKAT...")
            progress_bar.progress(0.3)

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                progress_bar.progress(1.0)
                status_text.text("✅ Analysis complete!")

                # Load results
                pred_file = f"results/{sam_name}_copykat_prediction.txt"
                if os.path.exists(pred_file):
                    predictions = pd.read_csv(pred_file, sep="\t")

                    st.subheader("Results")
                    st.dataframe(predictions)

                    # Summary
                    summary = predictions['copykat.pred'].value_counts()
                    st.bar_chart(summary)

                    # Download
                    st.download_button(
                        "Download Predictions",
                        predictions.to_csv(index=False),
                        file_name=f"{sam_name}_predictions.csv"
                    )
            else:
                st.error(f"Analysis failed:\n{result.stderr}")

if __name__ == "__main__":
    main()
```

---

**See Also**:
- [05_STREAMLIT_DASHBOARD_DESIGN.md](05_STREAMLIT_DASHBOARD_DESIGN.md) - UI design patterns
- [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) - Error solutions
- [PRD Section 5](../Product%20Requirements%20Document%20(PRD)_%20CNV-Cancer-RNAseq-analysis.md) - Architecture specification
