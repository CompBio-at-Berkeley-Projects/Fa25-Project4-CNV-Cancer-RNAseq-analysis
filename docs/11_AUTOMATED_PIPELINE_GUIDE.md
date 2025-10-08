# Automated CopyKAT Pipeline Guide

Complete guide for using the production-grade automated CopyKAT analysis pipeline with comprehensive error handling, validation, and reporting.

---

## Overview

The automated pipeline provides:

- **Automatic data validation** and quality assessment
- **Smart preprocessing** (log-transform detection, filtering)
- **Robust error handling** with detailed logging
- **Comprehensive HTML reports** with visualizations
- **Production-ready** for batch processing and HPC

**Created Files:**
1. `r_scripts/automated_copykat_analysis.R` - Main pipeline script
2. `r_scripts/copykat_utils.R` - Utility functions
3. `r_scripts/copykat_report.Rmd` - HTML report template
4. `config/analysis_config.yaml` - Configuration file

---

## Quick Start

### Basic Usage

```bash
# Navigate to project directory
cd ~/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Activate conda environment
conda activate Project4-CNV-Cancer-RNAseq

# Run with default configuration
Rscript r_scripts/automated_copykat_analysis.R

# Run with custom configuration
Rscript r_scripts/automated_copykat_analysis.R config/my_config.yaml

# Run with command-line arguments
Rscript r_scripts/automated_copykat_analysis.R \
  --input data/sample.txt.gz \
  --name sample_001 \
  --output results \
  --genome hg20 \
  --cores 8
```

### First Time Setup

**1. Install required R packages:**

```r
# In R console
install.packages(c("yaml", "logger", "rmarkdown", "knitr",
                   "ggplot2", "pheatmap", "RColorBrewer", "gridExtra"))
```

**2. Edit configuration file:**

```bash
# Copy template
cp config/analysis_config.yaml config/my_analysis.yaml

# Edit with your parameters
nano config/my_analysis.yaml
```

**3. Run analysis:**

```bash
Rscript r_scripts/automated_copykat_analysis.R config/my_analysis.yaml
```

---

## Configuration File

### Structure

The YAML configuration file has 8 main sections:

1. **input** - Data file and format settings
2. **output** - Output directory and naming
3. **quality_control** - QC thresholds
4. **preprocessing** - Data preprocessing options
5. **copykat** - CopyKAT algorithm parameters
6. **advanced** - Additional analysis options
7. **logging** - Logging configuration
8. **visualization** - Plot settings

### Key Parameters

```yaml
input:
  file: "data/raw/sample.txt.gz"
  separator: "tab"           # tab, comma, or space
  header: true
  row_names: true

output:
  directory: "results"
  sample_name: "sample_001"
  timestamp: true            # Add timestamp to output dir
  save_intermediate: true    # Save intermediate results

quality_control:
  min_genes_per_cell: 200
  min_umi_per_cell: 500
  max_mt_percent: 20
  auto_filter: true          # Automatically filter low-quality cells

preprocessing:
  detect_log_transform: true # Auto-detect log-transformed data
  convert_to_counts: true    # Convert back to counts if needed
  log_base: 2

copykat:
  genome: "hg20"             # hg20, hg19, mm10, mm9
  id_type: "S"               # S (Symbol) or E (Ensembl)
  cell_line: "no"            # "yes" for pure cell lines
  n_cores: 4                 # CPU cores to use

advanced:
  extra_plots: true          # Generate additional visualizations
  chr_summary: true          # Create chromosome-level summary
  export_csv: true           # Export results to CSV
  generate_report: true      # Generate HTML report
```

### Scenario Presets

The config file includes presets for common scenarios:

**High Resolution Analysis:**
```yaml
copykat:
  win_size: 15      # Smaller windows
  KS_cut: 0.05      # More sensitive
  n_cores: 8
```

**Low Quality Data:**
```yaml
copykat:
  LOW_DR: 0.02      # Lower thresholds
  UP_DR: 0.02
  win_size: 50      # Larger windows for smoothing
```

**Pure Cell Line:**
```yaml
copykat:
  cell_line: "yes"
  LOW_DR: 0.02
  UP_DR: 0.05
```

**Large Dataset (>5000 cells):**
```yaml
copykat:
  n_cores: 16
  plot_genes: "FALSE"  # Faster plotting
performance:
  max_memory_gb: 64
```

---

## Pipeline Workflow

The automated pipeline executes 7 main steps:

### Step 1: Data Loading

- Reads expression matrix from file
- Supports `.txt`, `.txt.gz`, `.csv`, `.tsv`, `.rds` formats
- Handles compressed files automatically

### Step 2: Data Validation

- Checks matrix structure (genes × cells)
- Validates row/column names
- Detects NA/Inf values
- Reports dimensions and sparsity

### Step 3: Quality Control

- Calculates QC metrics (genes/cell, UMI/cell, MT%)
- Generates QC plots: `plots/qc_metrics.pdf`
- Logs all quality metrics

### Step 4: Preprocessing

- **Auto-detects** log-transformed data
- Converts to counts if needed
- Filters low-quality cells and genes
- Reports filtering statistics

### Step 5: CopyKAT Analysis

- Changes to output directory
- Runs CopyKAT with specified parameters
- Logs progress and warnings
- Handles errors gracefully

### Step 6: Results Processing

- Summarizes cell classifications
- Calculates confidence scores
- Generates summary plots: `plots/copykat_summary.pdf`
- Creates chromosome-level summary: `chromosome_summary.csv`
- Exports CSV files: `*_predictions.csv`, `*_cnv_matrix.csv`

### Step 7: Report Generation

- Renders HTML report using R Markdown
- Includes all visualizations and statistics
- Comprehensive interpretation and QC checks
- Output: `<sample_name>_report.html`

---

## Output Structure

```
results/sample_001_20250107_123456/
├── logs/
│   └── analysis.log                          # Detailed log file
├── plots/
│   ├── qc_metrics.pdf                        # Quality control plots
│   └── copykat_summary.pdf                   # Results summary plots
├── sample_001_copykat_prediction.txt         # Cell classifications
├── sample_001_copykat_CNA_results.txt        # CNV matrix (segmented)
├── sample_001_copykat_CNA_raw_results.txt    # Raw CNV values
├── sample_001_copykat_heatmap.pdf            # CNV heatmap
├── sample_001_predictions.csv                # Predictions (CSV export)
├── sample_001_cnv_matrix.csv                 # CNV matrix (CSV export)
├── chromosome_summary.csv                    # Chromosome-level summary
└── sample_001_report.html                    # Comprehensive HTML report
```

---

## Understanding the Log File

The log file (`logs/analysis.log`) contains detailed execution information:

```
[INFO] 2025-01-07 12:34:56 ================================================================================
[INFO] 2025-01-07 12:34:56 CopyKAT Automated Analysis Pipeline
[INFO] 2025-01-07 12:34:56 ================================================================================
[INFO] 2025-01-07 12:34:56 Start time: 2025-01-07 12:34:56
[INFO] 2025-01-07 12:34:56 Output directory: results/sample_001_20250107_123456
[INFO] 2025-01-07 12:34:56
[INFO] 2025-01-07 12:34:57 STEP 1: Loading Data
[INFO] 2025-01-07 12:34:57 --------------------------------------------------------------------------------
[INFO] 2025-01-07 12:34:57 Input file: data/raw/sample.txt.gz
[INFO] 2025-01-07 12:35:02 Data loaded successfully
[INFO] 2025-01-07 12:35:02 Dimensions: 5948 genes x 543 cells
...
```

**Log Levels:**
- `[INFO]` - Normal execution progress
- `[WARN]` - Warnings (analysis continues)
- `[ERROR]` - Errors (analysis stops)
- `[DEBUG]` - Detailed debugging info (if enabled)

---

## HTML Report

The automated HTML report includes:

### Executive Summary
- Key findings at a glance
- Overall quality assessment
- Cell classification counts and percentages

### Data Quality Control
- Input data summary
- QC metric plots (genes/cell, UMI/cell, MT%)
- Quality statistics table

### CopyKAT Results
- Cell classification distribution (bar chart, pie chart)
- Confidence score analysis (histogram, boxplot)
- CNV heatmap display
- Chromosome-level alterations (table, bar chart)

### Biological Interpretation
- Tumor purity estimation
- Detected chromosomal alterations
- Clinical relevance notes

### Methods
- Analysis parameters used
- Algorithm summary
- Reference citations

### Quality Control Checks
- PASS/WARNING checklist
- Recommendations

### Session Information
- R version and package versions
- Reproducibility information

---

## Advanced Usage

### Batch Processing

**Create batch script:**

```bash
#!/bin/bash
# batch_analysis.sh

SAMPLES=(
  "sample_001:data/raw/sample1.txt.gz"
  "sample_002:data/raw/sample2.txt.gz"
  "sample_003:data/raw/sample3.txt.gz"
)

for sample_info in "${SAMPLES[@]}"; do
  IFS=':' read -r name file <<< "$sample_info"

  echo "Processing $name..."

  Rscript r_scripts/automated_copykat_analysis.R \
    --input "$file" \
    --name "$name" \
    --output results \
    --cores 4

  if [ $? -eq 0 ]; then
    echo "  ✓ SUCCESS: $name"
  else
    echo "  ✗ FAILED: $name"
  fi
done
```

**Run batch:**
```bash
chmod +x batch_analysis.sh
./batch_analysis.sh
```

### HPC/Cluster Usage

**SLURM job script:**

```bash
#!/bin/bash
#SBATCH --job-name=copykat_auto
#SBATCH --output=logs/copykat_%j.out
#SBATCH --error=logs/copykat_%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G

module load R/4.5.1

Rscript r_scripts/automated_copykat_analysis.R \
  --input $INPUT_FILE \
  --name $SAMPLE_NAME \
  --cores $SLURM_CPUS_PER_TASK
```

**Submit:**
```bash
export INPUT_FILE="data/sample.txt.gz"
export SAMPLE_NAME="sample_001"
sbatch slurm_copykat.sh
```

### Custom Configuration Per Sample

```bash
# Create sample-specific config
cat > config/sample_001.yaml << EOF
input:
  file: "data/sample_001.txt.gz"
output:
  sample_name: "sample_001"
copykat:
  genome: "hg20"
  n_cores: 8
EOF

# Run with sample config
Rscript r_scripts/automated_copykat_analysis.R config/sample_001.yaml
```

---

## Error Handling

### Automatic Recovery

The pipeline handles common errors:

1. **Log-transformed data detected** → Auto-converts to counts
2. **Low data quality** → Adjusts thresholds automatically
3. **Optional steps fail** → Continues with warnings
4. **Missing files** → Clear error message with instructions

### Error Messages

**"Input file not found"**
```
Solution: Check file path in config or --input argument
```

**"Data validation failed"**
```
Solution: Check for NA values, proper gene/cell names
See validation section in log file for details
```

**"CopyKAT analysis failed"**
```
Solution: Check parameters, data quality
Review full error in log file
Consider adjusting LOW.DR, UP.DR, or win.size
```

**"Report generation failed"**
```
Solution: Ensure rmarkdown package installed
install.packages("rmarkdown")
Analysis results still available in output directory
```

---

## Utility Functions Reference

The `copykat_utils.R` module provides reusable functions:

### Validation Functions

```r
# Validate expression matrix
validation <- validate_expression_matrix(data)
# Returns: list(valid, errors, warnings, metrics)

# Assess data quality
quality <- assess_data_quality(data)
# Returns: genes_per_cell, umi_per_cell, mt_percent, sparsity
```

### Preprocessing Functions

```r
# Detect log transformation
log_result <- detect_log_transform(data)
# Returns: is_log_transformed, method, confidence

# Convert log to counts
counts <- convert_log_to_counts(data, base = 2)

# Filter cells
filtered <- filter_cells(data, min_genes = 200, min_umi = 500, max_mt_percent = 20)

# Filter genes
filtered <- filter_genes(data, min_cells = 3)
```

### Visualization Functions

```r
# Plot QC metrics
plot_qc_metrics(data, output_file = "qc.pdf")

# Plot CNV profile
plot_cnv_profile(cnv_matrix, cell_name = "Cell_001", chr_data)

# Plot CopyKAT summary
plot_copykat_summary(result, output_file = "summary.pdf")
```

---

## Troubleshooting

### Common Issues

**Issue: Pipeline runs slowly**
```
Solution:
1. Increase n_cores in config
2. Use plot_genes: "FALSE" for large datasets
3. Run on HPC with more resources
```

**Issue: All cells classified as diploid**
```
Solution:
1. Check if sample actually contains tumor cells
2. Decrease KS_cut (e.g., 0.05) for higher sensitivity
3. Use cell_line: "yes" if pure cancer cell line
```

**Issue: Poor quality warnings**
```
Solution:
1. Review QC plots in results/plots/
2. Adjust filtering thresholds in config
3. Consider using LOW.DR: 0.02, UP.DR: 0.02
```

**Issue: HTML report not generated**
```
Solution:
1. Install rmarkdown: install.packages("rmarkdown")
2. Install ggplot2 and dependencies
3. Check report template exists: r_scripts/copykat_report.Rmd
4. Analysis results still available without report
```

### Debug Mode

Enable detailed logging:

```yaml
logging:
  verbose: true
  level: "DEBUG"
```

Check log file for detailed execution trace.

---

## Best Practices

### Before Running

1. **Inspect your data first**
   ```r
   data <- read.table(gzfile("data/sample.txt.gz"), header=TRUE, row.names=1)
   dim(data)
   summary(colSums(data > 0))  # Genes per cell
   ```

2. **Start with default parameters**
   - Only adjust if you get warnings
   - Document parameter changes

3. **Use descriptive sample names**
   ```yaml
   sample_name: "GBM_patient01_tumor"  # Good
   sample_name: "sample"               # Bad
   ```

### During Analysis

1. **Monitor log file** for warnings
   ```bash
   tail -f results/sample_001_*/logs/analysis.log
   ```

2. **Check QC plots** before accepting results

3. **Validate with known biology**
   - Do detected CNVs match expectations?
   - Are confidence scores high (>0.8)?

### After Analysis

1. **Review HTML report** thoroughly

2. **Check chromosome summary** for expected alterations

3. **Compare multiple runs** if batch processing

4. **Archive results**
   ```bash
   tar -czf sample_001_results.tar.gz results/sample_001_*/
   ```

---

## Integration with Streamlit

The automated pipeline can be integrated with the Streamlit dashboard:

```python
import subprocess
import yaml

def run_automated_analysis(input_file, sample_name, config_updates=None):
    # Load base config
    with open('config/analysis_config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Update config
    config['input']['file'] = input_file
    config['output']['sample_name'] = sample_name

    if config_updates:
        config.update(config_updates)

    # Save temporary config
    temp_config = f'config/temp_{sample_name}.yaml'
    with open(temp_config, 'w') as f:
        yaml.dump(config, f)

    # Run analysis
    result = subprocess.run(
        ['Rscript', 'r_scripts/automated_copykat_analysis.R', temp_config],
        capture_output=True,
        text=True
    )

    return result.returncode == 0
```

---

## Performance Optimization

### Memory Usage

**Estimated RAM requirements:**
- 500 cells: 8-12 GB
- 2,000 cells: 16-24 GB
- 5,000 cells: 32-48 GB
- 10,000+ cells: 64+ GB

**Reduce memory:**
```yaml
copykat:
  plot_genes: "FALSE"
visualization:
  dpi: 150  # Lower resolution
```

### Runtime Optimization

**Expected runtimes:**
| Cells | Genes | Cores | Time |
|-------|-------|-------|------|
| 500 | 10k | 4 | 5-10 min |
| 2000 | 15k | 8 | 15-30 min |
| 5000 | 20k | 16 | 45-90 min |

**Speed up:**
1. Increase `n_cores`
2. Use `win_size: 50` (larger windows)
3. Disable `extra_plots`

---

## See Also

- [08_BEGINNER_TUTORIAL.md](08_BEGINNER_TUTORIAL.md) - Basic CopyKAT usage
- [04_CLI_USAGE_GUIDE.md](04_CLI_USAGE_GUIDE.md) - CLI reference
- [06_PYTHON_R_INTEGRATION.md](06_PYTHON_R_INTEGRATION.md) - Python integration
- [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) - Common issues
- [09_RESULTS_INTERPRETATION.md](09_RESULTS_INTERPRETATION.md) - Understanding results

---

**Pipeline Version:** 1.0.0
**Last Updated:** 2025-01-07
**Author:** Automated CopyKAT Pipeline Team
