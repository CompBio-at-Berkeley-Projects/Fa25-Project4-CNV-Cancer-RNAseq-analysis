# Shared Utilities Documentation

This directory contains utilities, configurations, and data contracts shared between frontend and backend components.

## Table of Contents

1. [Purpose](#purpose)
2. [Directory Structure](#directory-structure)
3. [Configuration Management](#configuration-management)
4. [Data Schemas](#data-schemas)
5. [Constants](#constants)
6. [Shared Utilities](#shared-utilities)
7. [Usage Guidelines](#usage-guidelines)

## Purpose

The `shared/` directory provides:

- **Configuration Management**: Centralized config loading and validation
- **Data Schemas**: Contract definitions for frontend-backend communication
- **Constants**: Project-wide constants (file paths, defaults, enums)
- **Utilities**: Cross-cutting helper functions

This ensures consistency and reduces code duplication between frontend and backend.

## Directory Structure

```
shared/
├── shared.md              # This file
├── config.py              # Configuration management
├── constants.py           # Shared constants
├── utils.py               # Common utility functions
└── schemas/               # Data contract definitions
    ├── input_schema.json  # Analysis input format
    └── output_schema.json # Analysis output format
```

## Configuration Management

### config.py

Provides unified configuration loading for the entire application.

**Features**:
- Load YAML configuration files
- Validate configuration parameters
- Merge CLI arguments with config files
- Provide default values

**Usage**:

```python
from shared.config import load_config, validate_config

# Load configuration
config = load_config('config/analysis_config.yaml')

# Validate
is_valid, errors = validate_config(config)

# Access values
input_file = config['input']['file']
genome = config['copykat']['genome']
```

**Configuration Structure**:

```yaml
input:
  file: "backend/data/raw/sample.txt.gz"
  separator: "tab"
  header: true
  row_names: true

output:
  directory: "backend/results"
  sample_name: "sample_001"
  timestamp: true

copykat:
  genome: "hg20"
  cell_line: "no"
  ngene_chr: 5
  LOW_DR: 0.05
  UP_DR: 0.10
  win_size: 25
  KS_cut: 0.1
  n_cores: 4
```

## Data Schemas

### Purpose

Schemas define the data contracts between frontend and backend. They ensure:
- Frontend sends data in the format backend expects
- Backend returns data in the format frontend expects
- Changes to data format are explicitly documented
- Validation catches errors early

### input_schema.json

Defines the format for analysis requests from frontend to backend.

**Fields**:

```json
{
  "input_file": "string (required) - Path to expression matrix",
  "sample_name": "string (required) - Sample identifier",
  "output_dir": "string (required) - Output directory path",
  "genome": "string (required) - 'hg20' or 'mm10'",
  "ngene_chr": "integer (optional, default: 5) - Min genes per chromosome",
  "LOW_DR": "float (optional, default: 0.05) - Detection rate for smoothing",
  "UP_DR": "float (optional, default: 0.10) - Detection rate for segmentation",
  "win_size": "integer (optional, default: 25) - Window size in genes",
  "KS_cut": "float (optional, default: 0.1) - Segmentation sensitivity",
  "distance": "string (optional, default: 'euclidean') - Distance metric",
  "n_cores": "integer (optional, default: 4) - CPU cores",
  "cell_line": "string (optional, default: 'no') - 'yes' or 'no'",
  "plot_genes": "boolean (optional, default: true) - Show genes in heatmap"
}
```

**Example**:

```json
{
  "input_file": "/path/to/data.txt.gz",
  "sample_name": "glio_sample_001",
  "output_dir": "backend/results",
  "genome": "hg20",
  "ngene_chr": 5,
  "n_cores": 4
}
```

### output_schema.json

Defines the format for analysis results from backend to frontend.

**Fields**:

```json
{
  "success": "boolean - Whether analysis succeeded",
  "output_dir": "string - Path to results directory",
  "sample_name": "string - Sample identifier",
  "timestamp": "string - ISO format timestamp",
  "files": {
    "predictions": "string - Path to predictions file",
    "heatmap": "string - Path to heatmap image",
    "cna_results": "string - Path to CNV results",
    "report": "string - Path to HTML report",
    "log": "string - Path to log file"
  },
  "summary": {
    "n_cells": "integer - Total cells analyzed",
    "n_aneuploid": "integer - Aneuploid cells",
    "n_diploid": "integer - Diploid cells",
    "n_not_defined": "integer - Undefined cells",
    "aneuploid_fraction": "float - Fraction of aneuploid cells"
  },
  "runtime_minutes": "float - Analysis runtime",
  "error": "string (nullable) - Error message if failed"
}
```

**Example**:

```json
{
  "success": true,
  "output_dir": "backend/results/glio_001_20241029_120000",
  "sample_name": "glio_001",
  "timestamp": "2024-10-29T12:00:00",
  "files": {
    "predictions": "backend/results/glio_001_20241029_120000/glio_001_copykat_prediction.txt",
    "heatmap": "backend/results/glio_001_20241029_120000/glio_001_copykat_heatmap.jpeg",
    "cna_results": "backend/results/glio_001_20241029_120000/glio_001_copykat_CNA_results.txt",
    "report": "backend/results/glio_001_20241029_120000/glio_001_report.html",
    "log": "backend/results/glio_001_20241029_120000/logs/analysis.log"
  },
  "summary": {
    "n_cells": 500,
    "n_aneuploid": 350,
    "n_diploid": 145,
    "n_not_defined": 5,
    "aneuploid_fraction": 0.70
  },
  "runtime_minutes": 12.5,
  "error": null
}
```

## Constants

### constants.py

Project-wide constants to ensure consistency.

**Categories**:

1. **File Paths**
   ```python
   PROJECT_ROOT = "/Users/hansonwen/Fa25-Project4-CNV-Cancer-RNAseq-analysis"
   DATA_DIR = "backend/data"
   RESULTS_DIR = "backend/results"
   CONFIG_DIR = "config"
   ```

2. **Analysis Defaults**
   ```python
   DEFAULT_GENOME = "hg20"
   DEFAULT_NGENE_CHR = 5
   DEFAULT_WIN_SIZE = 25
   DEFAULT_N_CORES = 4
   MIN_CELLS = 50
   MIN_GENES = 1000
   ```

3. **Genome Options**
   ```python
   SUPPORTED_GENOMES = ["hg20", "mm10"]
   GENOME_DISPLAY_NAMES = {
       "hg20": "Human (hg20)",
       "mm10": "Mouse (mm10)"
   }
   ```

4. **File Extensions**
   ```python
   SUPPORTED_INPUT_FORMATS = [".txt", ".csv", ".tsv", ".gz", ".rds"]
   OUTPUT_FILE_PATTERNS = {
       "predictions": "{sample}_copykat_prediction.txt",
       "heatmap": "{sample}_copykat_heatmap.jpeg",
       "cna_results": "{sample}_copykat_CNA_results.txt"
   }
   ```

5. **Status Messages**
   ```python
   STATUS_LOADING = "Loading data..."
   STATUS_VALIDATING = "Validating input..."
   STATUS_PREPROCESSING = "Preprocessing data..."
   STATUS_ANALYZING = "Running CopyKAT analysis..."
   STATUS_COMPLETE = "Analysis complete!"
   ```

**Usage**:

```python
from shared.constants import DEFAULT_GENOME, MIN_CELLS, SUPPORTED_GENOMES

if genome not in SUPPORTED_GENOMES:
    raise ValueError(f"Unsupported genome: {genome}")

if n_cells < MIN_CELLS:
    print(f"Warning: Only {n_cells} cells (recommended: {MIN_CELLS}+)")
```

## Shared Utilities

### utils.py

Common utility functions used by both frontend and backend.

**Functions**:

1. **Path Utilities**
   ```python
   def get_absolute_path(relative_path: str) -> str:
       """Convert relative path to absolute path from project root"""
   
   def ensure_dir_exists(dir_path: str) -> None:
       """Create directory if it doesn't exist"""
   
   def get_project_root() -> str:
       """Get project root directory"""
   ```

2. **File Operations**
   ```python
   def get_file_size_mb(file_path: str) -> float:
       """Get file size in megabytes"""
   
   def is_compressed(file_path: str) -> bool:
       """Check if file is gzip compressed"""
   
   def list_result_directories() -> List[str]:
       """List all analysis result directories"""
   ```

3. **Validation**
   ```python
   def validate_file_path(file_path: str) -> Tuple[bool, str]:
       """Validate file exists and is readable"""
   
   def validate_genome(genome: str) -> bool:
       """Validate genome parameter"""
   
   def validate_sample_name(name: str) -> Tuple[bool, str]:
       """Validate sample name format"""
   ```

4. **Data Conversion**
   ```python
   def timestamp_to_readable(timestamp: str) -> str:
       """Convert timestamp to human-readable format"""
   
   def bytes_to_human_readable(size_bytes: int) -> str:
       """Convert bytes to human-readable size"""
   ```

**Usage**:

```python
from shared.utils import get_absolute_path, validate_file_path

# Get absolute path
abs_path = get_absolute_path("backend/data/sample.txt")

# Validate before processing
is_valid, error_msg = validate_file_path(abs_path)
if not is_valid:
    print(f"Error: {error_msg}")
```

## Usage Guidelines

### For Frontend Developers

1. **Use schemas for validation**
   ```python
   from shared.schemas import validate_input, validate_output
   
   # Before sending to backend
   params = get_user_parameters()
   if not validate_input(params):
       show_error("Invalid parameters")
   ```

2. **Use constants for display**
   ```python
   from shared.constants import GENOME_DISPLAY_NAMES
   
   genome_options = st.selectbox(
       "Genome",
       options=list(GENOME_DISPLAY_NAMES.keys()),
       format_func=lambda x: GENOME_DISPLAY_NAMES[x]
   )
   ```

3. **Use utilities for file operations**
   ```python
   from shared.utils import get_file_size_mb, ensure_dir_exists
   
   file_size = get_file_size_mb(uploaded_file)
   if file_size > 200:
       st.warning("Large file - may take longer to process")
   ```

### For Backend Developers

1. **Use config management**
   ```r
   # Load shared configuration
   config <- yaml::read_yaml("config/analysis_config.yaml")
   
   # Override with command line args
   if ("--cores" %in% args) {
       config$copykat$n_cores <- as.integer(args[which(args == "--cores") + 1])
   }
   ```

2. **Follow output schema**
   ```r
   # Ensure outputs match schema
   output <- list(
       success = TRUE,
       output_dir = output_directory,
       sample_name = sample_name,
       files = list(
           predictions = prediction_file,
           heatmap = heatmap_file
       ),
       summary = list(
           n_cells = ncol(data),
           n_aneuploid = sum(predictions$copykat.pred == "aneuploid")
       )
   )
   
   # Write output manifest
   jsonlite::write_json(output, file.path(output_dir, "manifest.json"))
   ```

### Updating Schemas

When you need to change data formats:

1. Update the schema JSON file
2. Update documentation in this file
3. Notify both frontend and backend teams
4. Update all code that uses the schema
5. Test thoroughly

### Adding New Constants

When adding new constants:

1. Add to appropriate category in `constants.py`
2. Document the constant
3. Use descriptive ALL_CAPS names
4. Ensure type consistency

## Best Practices

1. **Never hardcode values** - Use constants instead
2. **Always validate against schemas** - Catch errors early
3. **Use shared utilities** - Don't duplicate code
4. **Document changes** - Update this file when modifying shared code
5. **Test both sides** - Changes affect frontend and backend

## When to Add to Shared

Add code to `shared/` when:

- Used by both frontend and backend
- Defines a data contract between components
- Represents a project-wide constant
- Implements cross-cutting functionality

Don't add to `shared/` when:

- Only used by frontend (put in `frontend/utils/`)
- Only used by backend (put in `backend/api/`)
- Component-specific logic
- UI-specific formatting

## Questions?

Refer to:
- Frontend guide: `frontend/frontend.md`
- Backend guide: `backend/backend.md`
- Main instructions: `instructions.md`

