# Automated CopyKAT Analysis Pipeline

**Production-grade automated pipeline for CNV detection from single-cell RNA-seq data**

---

## What This Is

A fully automated, production-ready R pipeline that:

- **Validates** your input data automatically
- **Preprocesses** data intelligently (detects log-transform, filters poor quality)
- **Analyzes** with CopyKAT to detect copy number variations
- **Handles errors** gracefully with comprehensive logging
- **Generates reports** with publication-quality visualizations and statistics
- **Documents everything** - every step is logged and explained

Perfect for:
- Beginners who want a "just works" solution
- Production environments requiring robust error handling
- Batch processing multiple samples
- Reproducible research with detailed documentation

---

## Quick Start (3 Steps)

### 1. Install Dependencies

```r
# In R console
install.packages(c("yaml", "logger", "rmarkdown", "knitr",
                   "ggplot2", "pheatmap", "RColorBrewer", "gridExtra"))
```

### 2. Run Example

```bash
# In terminal
conda activate Project4-CNV-Cancer-RNAseq
./run_automated_example.sh
```

### 3. View Results

Open the HTML report in your browser:
```bash
# Output will be in results/glioblastoma_example_TIMESTAMP/
open results/glioblastoma_example_*/glioblastoma_example_report.html
```

**That's it!** The pipeline handles everything else automatically.

---

## What Gets Created

### Files Created

```
r_scripts/
├── automated_copykat_analysis.R  # Main pipeline (~450 lines)
├── copykat_utils.R               # Utility functions (~400 lines)
└── copykat_report.Rmd            # HTML report template (~450 lines)

config/
└── analysis_config.yaml          # Configuration template (~150 lines)

docs/
└── 11_AUTOMATED_PIPELINE_GUIDE.md  # Complete guide (~600 lines)

run_automated_example.sh          # Example run script
```

### Output Structure

When you run the pipeline, it creates:

```
results/sample_TIMESTAMP/
├── logs/
│   └── analysis.log              # Detailed execution log
├── plots/
│   ├── qc_metrics.pdf            # Data quality plots
│   └── copykat_summary.pdf       # Results summary
├── sample_copykat_prediction.txt # Cell classifications
├── sample_copykat_CNA_results.txt  # CNV matrix
├── sample_copykat_heatmap.pdf    # CNV heatmap
├── sample_predictions.csv        # Predictions (CSV)
├── sample_cnv_matrix.csv         # CNV matrix (CSV)
├── chromosome_summary.csv        # Chromosome alterations
└── sample_report.html            # Comprehensive HTML report ⭐
```

---

## Features

### Automatic Data Handling

**Smart Preprocessing:**
- Detects if data is log-transformed (checks for negative values, value ranges)
- Automatically converts back to counts if needed
- Filters low-quality cells and genes
- Handles compressed files (.gz) automatically

**Validation:**
- Checks matrix structure before analysis
- Validates gene/cell names
- Detects NA/Inf values
- Reports data quality metrics

### Robust Error Handling

- **Try-Catch blocks** around every critical step
- **Detailed logging** to file (INFO, WARN, ERROR levels)
- **Graceful degradation** - optional steps can fail without stopping pipeline
- **Clear error messages** with solutions

### Comprehensive Reporting

The HTML report includes:
- **Executive Summary** - Key findings at a glance
- **Quality Control** - QC plots and metrics
- **Cell Classifications** - Bar charts, pie charts, confidence scores
- **CNV Heatmap** - Visual representation of alterations
- **Chromosome Summary** - Table and bar chart of CNVs by chromosome
- **Biological Interpretation** - Tumor purity, clinical relevance
- **Methods** - Parameters used, algorithm description
- **QC Checklist** - PASS/WARNING status for all metrics

---

## Usage Examples

### Basic Usage

```bash
# Default configuration
Rscript r_scripts/automated_copykat_analysis.R

# Custom configuration file
Rscript r_scripts/automated_copykat_analysis.R config/my_analysis.yaml

# Command-line arguments
Rscript r_scripts/automated_copykat_analysis.R \
  --input data/sample.txt.gz \
  --name sample_001 \
  --output results \
  --genome hg20 \
  --cores 8
```

### Batch Processing

```bash
# Create batch script
cat > batch_run.sh << 'EOF'
#!/bin/bash
for sample in sample_001 sample_002 sample_003; do
  Rscript r_scripts/automated_copykat_analysis.R \
    --input "data/${sample}.txt.gz" \
    --name "$sample" \
    --cores 4
done
EOF

chmod +x batch_run.sh
./batch_run.sh
```

### Custom Configuration

```yaml
# config/my_config.yaml
input:
  file: "data/my_sample.txt.gz"

output:
  sample_name: "my_sample"

copykat:
  genome: "hg20"
  n_cores: 8
  win_size: 15    # High resolution
  KS_cut: 0.05    # More sensitive

advanced:
  generate_report: true
  extra_plots: true
```

Run:
```bash
Rscript r_scripts/automated_copykat_analysis.R config/my_config.yaml
```

---

## Configuration Reference

### Essential Parameters

```yaml
input:
  file: "path/to/data.txt.gz"    # Your expression matrix

output:
  sample_name: "sample_001"       # Name for outputs
  timestamp: true                 # Add timestamp to directory

copykat:
  genome: "hg20"                  # hg20, hg19, mm10, mm9
  n_cores: 4                      # CPU cores
  cell_line: "no"                 # "yes" for pure cell lines
```

### Tuning Parameters

```yaml
copykat:
  # Resolution control
  win_size: 25      # 15=high res, 25=default, 50=smooth
  KS_cut: 0.1       # 0.05=sensitive, 0.1=default, 0.2=conservative

  # Data quality thresholds
  LOW_DR: 0.05      # Lower for sparse data (0.02)
  UP_DR: 0.1        # Adjust with LOW_DR
```

### Quality Control

```yaml
quality_control:
  min_genes_per_cell: 200   # Filter cells with <200 genes
  min_umi_per_cell: 500     # Filter cells with <500 UMI
  max_mt_percent: 20        # Filter cells with >20% MT
  auto_filter: true         # Enable automatic filtering
```

---

## Understanding the Output

### Log File

Track progress in real-time:
```bash
tail -f results/sample_*/logs/analysis.log
```

Example log:
```
[INFO] STEP 1: Loading Data
[INFO] Data loaded successfully
[INFO] Dimensions: 5948 genes x 543 cells
[INFO] STEP 2: Data Validation
[INFO] Data validation: PASSED
[INFO] STEP 3: Quality Control
[INFO] Median genes/cell: 3450
[INFO] STEP 4: Preprocessing
[INFO] Log-transform detection: negative_values
[INFO] Converting log-transformed data to counts...
[INFO] Filtering low-quality cells...
[INFO] STEP 5: CopyKAT Analysis
[INFO] Starting CopyKAT analysis...
[INFO] Runtime: 8.5 minutes
[INFO] STEP 6: Processing Results
[INFO] aneuploid: 450 cells (82.88%)
[INFO] diploid: 93 cells (17.12%)
[INFO] STEP 7: Generating HTML Report
[INFO] Report generated
[INFO] ANALYSIS COMPLETE
```

### HTML Report

The star of the show! Includes:

1. **Executive Summary** - Quick overview
2. **QC Plots** - Genes/cell, UMI/cell, MT%
3. **Classifications** - How many aneuploid vs diploid
4. **Confidence Scores** - How reliable are classifications
5. **CNV Heatmap** - Visual CNV patterns
6. **Chromosome Alterations** - Which chromosomes are altered
7. **Interpretation** - What it means biologically
8. **QC Checklist** - Quality assessment

### Key Files

- `*_report.html` - **Start here!** Complete analysis summary
- `*_predictions.csv` - Cell classifications (aneuploid/diploid)
- `chromosome_summary.csv` - CNVs by chromosome
- `logs/analysis.log` - Detailed execution log

---

## Troubleshooting

### Common Issues

**"conda: command not found"**
```bash
# Use full path
/Users/hansonwen/anaconda3/bin/conda activate Project4-CNV-Cancer-RNAseq
```

**"Package 'yaml' not found"**
```r
install.packages(c("yaml", "logger", "rmarkdown"))
```

**"All cells classified as diploid"**
```yaml
# In config, increase sensitivity:
copykat:
  KS_cut: 0.05
  win_size: 15
```

**"Low data quality warning"**
```yaml
# Adjust thresholds:
copykat:
  LOW_DR: 0.02
  UP_DR: 0.02
```

**"Report generation failed"**
```r
# Install missing packages:
install.packages(c("rmarkdown", "knitr", "ggplot2", "gridExtra"))
# Analysis results still available without report
```

### Check the Log

Always check `logs/analysis.log` for detailed error information.

---

## Performance Guide

### Memory Requirements

| Cells | Genes | RAM Needed |
|-------|-------|------------|
| 500   | 10k   | 8-12 GB    |
| 2,000 | 15k   | 16-24 GB   |
| 5,000 | 20k   | 32-48 GB   |
| 10,000+ | 20k | 64+ GB     |

### Runtime Estimates

| Cells | Cores | Time |
|-------|-------|------|
| 500   | 4     | 5-10 min |
| 2,000 | 4     | 20-40 min |
| 2,000 | 8     | 10-20 min |
| 5,000 | 16    | 45-90 min |

### Speed Optimization

```yaml
copykat:
  n_cores: 8              # More cores = faster
  plot_genes: "FALSE"     # Faster plotting
  win_size: 50            # Larger windows = faster

advanced:
  extra_plots: false      # Skip optional plots
```

---

## Integration with Streamlit

The pipeline is designed to integrate with the Streamlit dashboard:

```python
# In Streamlit app
import subprocess
import yaml

def run_automated_pipeline(input_file, sample_name, params):
    # Update config
    config = {
        'input': {'file': input_file},
        'output': {'sample_name': sample_name},
        'copykat': params
    }

    # Save config
    config_file = f'config/temp_{sample_name}.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    # Run pipeline
    result = subprocess.run(
        ['Rscript', 'r_scripts/automated_copykat_analysis.R', config_file],
        capture_output=True,
        text=True
    )

    return result.returncode == 0
```

See [06_PYTHON_R_INTEGRATION.md](docs/06_PYTHON_R_INTEGRATION.md) for complete integration guide.

---

## Advanced Features

### Using Utility Functions

The `copykat_utils.R` module provides reusable functions:

```r
source("r_scripts/copykat_utils.R")

# Validate data
validation <- validate_expression_matrix(data)

# Assess quality
quality <- assess_data_quality(data)

# Detect log transformation
log_status <- detect_log_transform(data)

# Filter cells
filtered <- filter_cells(data, min_genes = 200, min_umi = 500)

# Plot QC metrics
plot_qc_metrics(data, "qc_plots.pdf")
```

### Custom Report Templates

Modify `r_scripts/copykat_report.Rmd` to customize the HTML report:

```r
# Add custom sections
# Change color schemes
# Add additional visualizations
# Customize interpretation
```

---

## Documentation

Comprehensive documentation available:

1. **[11_AUTOMATED_PIPELINE_GUIDE.md](docs/11_AUTOMATED_PIPELINE_GUIDE.md)** - Complete guide (this document)
2. **[08_BEGINNER_TUTORIAL.md](docs/08_BEGINNER_TUTORIAL.md)** - Step-by-step tutorial
3. **[04_CLI_USAGE_GUIDE.md](docs/04_CLI_USAGE_GUIDE.md)** - CLI reference
4. **[07_TROUBLESHOOTING.md](docs/07_TROUBLESHOOTING.md)** - Common issues
5. **[03_PARAMETERS_REFERENCE.md](docs/03_PARAMETERS_REFERENCE.md)** - Parameter details

---

## Credits

**Pipeline Components:**
- CopyKAT: Gao et al. (2021) Nature Biotechnology
- R packages: yaml, logger, rmarkdown, ggplot2, pheatmap

**Documentation:**
- Based on best practices from bioinformatics community 2025
- Error handling patterns from production R workflows

---

## License

This pipeline is part of the Fa25-Project4-CNV-Cancer-RNAseq-analysis project.

---

## Support

For issues or questions:
1. Check [07_TROUBLESHOOTING.md](docs/07_TROUBLESHOOTING.md)
2. Review log file: `results/*/logs/analysis.log`
3. Consult [11_AUTOMATED_PIPELINE_GUIDE.md](docs/11_AUTOMATED_PIPELINE_GUIDE.md)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-07
**Status:** Production Ready ✓
