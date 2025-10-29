"""
Shared Constants

Project-wide constants to ensure consistency.

All constants are organized by category for easy reference.
"""

from pathlib import Path

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "backend" / "data"
RESULTS_DIR = PROJECT_ROOT / "backend" / "results"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"

# Analysis Defaults
DEFAULT_GENOME = "hg20"
DEFAULT_NGENE_CHR = 5
DEFAULT_WIN_SIZE = 25
DEFAULT_LOW_DR = 0.05
DEFAULT_UP_DR = 0.10
DEFAULT_KS_CUT = 0.1
DEFAULT_N_CORES = 4
DEFAULT_DISTANCE = "euclidean"
DEFAULT_CELL_LINE = "no"

# Validation Thresholds
MIN_CELLS = 50
MIN_CELLS_RECOMMENDED = 100
MIN_GENES = 1000
MIN_GENES_RECOMMENDED = 5000
MAX_MT_PERCENT = 20

# Genome Options
SUPPORTED_GENOMES = ["hg20", "mm10"]
GENOME_DISPLAY_NAMES = {
    "hg20": "Human (hg20)",
    "mm10": "Mouse (mm10)"
}

# Distance Metrics
DISTANCE_METRICS = ["euclidean", "pearson", "spearman"]
DISTANCE_DISPLAY_NAMES = {
    "euclidean": "Euclidean (standard)",
    "pearson": "Pearson correlation",
    "spearman": "Spearman correlation"
}

# Cell Type Classifications
CELL_TYPES = ["aneuploid", "diploid", "not.defined"]
CELL_TYPE_COLORS = {
    "aneuploid": "#FF6B6B",  # Red
    "diploid": "#4ECDC4",     # Teal
    "not.defined": "#95A5A6"  # Gray
}

# File Extensions
SUPPORTED_INPUT_FORMATS = [".txt", ".csv", ".tsv", ".gz", ".rds"]
SUPPORTED_COMPRESSED_FORMATS = [".gz"]

# Output File Patterns
OUTPUT_FILE_PATTERNS = {
    "predictions": "{sample}_copykat_prediction.txt",
    "cna_results": "{sample}_copykat_CNA_results.txt",
    "cna_raw": "{sample}_copykat_CNA_raw_results_gene_by_cell.txt",
    "heatmap": "{sample}_copykat_heatmap.jpeg",
    "heatmap_genes": "{sample}_copykat_with_genes_heatmap.pdf",
    "clustering": "{sample}_copykat_clustering_results.rds",
    "report": "{sample}_report.html",
    "log": "logs/analysis.log"
}

# Status Messages
STATUS_IDLE = "Ready"
STATUS_LOADING = "Loading data..."
STATUS_VALIDATING = "Validating input..."
STATUS_PREPROCESSING = "Preprocessing data..."
STATUS_QC = "Quality control..."
STATUS_ANALYZING = "Running CopyKAT analysis..."
STATUS_PROCESSING = "Processing results..."
STATUS_COMPLETE = "Analysis complete!"
STATUS_ERROR = "Error occurred"

# Error Messages
ERROR_FILE_NOT_FOUND = "File not found: {path}"
ERROR_INVALID_FORMAT = "Invalid file format: {format}"
ERROR_INSUFFICIENT_CELLS = "Insufficient cells: {n_cells} (minimum: {min_cells})"
ERROR_INVALID_GENOME = "Invalid genome: {genome} (must be one of {options})"
ERROR_PARAMETER_RANGE = "Parameter {param} out of range: {value}"
ERROR_UP_DR_LOW_DR = "UP.DR must be >= LOW.DR"

# Success Messages
SUCCESS_FILE_LOADED = "File loaded successfully: {n_genes} genes × {n_cells} cells"
SUCCESS_ANALYSIS_COMPLETE = "Analysis completed in {runtime:.1f} minutes"
SUCCESS_RESULTS_SAVED = "Results saved to: {output_dir}"

# Warning Messages
WARNING_LOW_CELLS = "Low cell count: {n_cells} (recommended: {recommended}+)"
WARNING_LOW_GENES = "Low gene count: {n_genes} (recommended: {recommended}+)"
WARNING_HIGH_MT = "High mitochondrial percentage: {mt_percent:.1f}%"
WARNING_LOG_TRANSFORMED = "Data appears log-transformed. Will convert to counts."

# UI Display
UI_PAGE_TITLES = {
    "home": "🧬 CopyKAT CNV Analysis",
    "upload": "📤 Data Upload",
    "configure": "⚙️ Configure Analysis",
    "results": "📊 Analysis Results",
    "download": "💾 Download Results"
}

# Parameter Ranges
PARAM_RANGES = {
    "ngene_chr": (1, 20),
    "win_size": (10, 150),
    "LOW_DR": (0.01, 0.30),
    "UP_DR": (0.01, 0.30),
    "KS_cut": (0.05, 0.40),
    "n_cores": (1, 64)
}

# Analysis Stages
ANALYSIS_STAGES = [
    "Data Loading",
    "Data Validation",
    "Quality Control",
    "Preprocessing",
    "CopyKAT Analysis",
    "Results Processing",
    "Report Generation"
]

# Dataset Information
EXAMPLE_DATASETS = {
    "glioblastoma": {
        "name": "Glioblastoma (GSE57872)",
        "path": "backend/data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz",
        "n_cells": "~400",
        "n_genes": "~20,000",
        "genome": "hg20"
    },
    "melanoma": {
        "name": "Melanoma (GSE72056)",
        "path": "backend/data/raw/melanoma_compressed/GSE72056_melanoma_single_cell_revised_v2.txt.gz",
        "n_cells": "~4,000",
        "n_genes": "~23,000",
        "genome": "hg20"
    }
}

# Version Information
VERSION = "1.0.0"
APP_NAME = "CopyKAT CNV Analysis Dashboard"
AUTHOR = "Fa25-Project4 Team"

