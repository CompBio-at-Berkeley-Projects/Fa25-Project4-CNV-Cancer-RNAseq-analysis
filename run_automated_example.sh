#!/bin/bash

# =============================================================================
# Example: Run Automated CopyKAT Pipeline
# =============================================================================
# This script demonstrates how to run the automated pipeline with test data
#
# Usage:
#   ./run_automated_example.sh
# =============================================================================

echo "========================================="
echo "Automated CopyKAT Pipeline - Example Run"
echo "========================================="
echo ""

# Check if conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "Project4-CNV-Cancer-RNAseq" ]]; then
    echo "Error: Conda environment not activated"
    echo "Please run: conda activate Project4-CNV-Cancer-RNAseq"
    exit 1
fi

# Create a custom config for this example
CONFIG_FILE="config/example_config.yaml"

echo "Creating example configuration..."
cat > $CONFIG_FILE << 'EOF'
# Example Configuration for Automated CopyKAT Pipeline

input:
  file: "data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"
  separator: "tab"
  header: true
  row_names: true

output:
  directory: "results"
  sample_name: "glioblastoma_example"
  timestamp: true
  save_intermediate: true

quality_control:
  min_genes_per_cell: 200
  min_umi_per_cell: 500
  max_mt_percent: 20
  auto_filter: true
  plot_qc: true

preprocessing:
  detect_log_transform: true
  convert_to_counts: true
  log_base: 2

copykat:
  id_type: "S"
  cell_line: "no"
  ngene_chr: 5
  LOW_DR: 0.05
  UP_DR: 0.1
  win_size: 25
  KS_cut: 0.1
  distance: "euclidean"
  genome: "hg20"
  n_cores: 4
  norm_cell_names: ""
  plot_genes: "TRUE"
  output_dir: ""

advanced:
  extra_plots: true
  chr_summary: true
  export_csv: true
  generate_report: true
  report_template: "r_scripts/copykat_report.Rmd"

logging:
  verbose: true
  level: "INFO"
  save_log: true
  continue_on_error: false

performance:
  max_memory_gb: 32
  timeout_minutes: 240

visualization:
  width: 12
  height: 8
  dpi: 300
  color_scheme: "default"
EOF

echo "Configuration created: $CONFIG_FILE"
echo ""

# Display configuration
echo "Analysis Configuration:"
echo "  Input: data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"
echo "  Sample: glioblastoma_example"
echo "  Genome: hg20"
echo "  Cores: 4"
echo ""

# Ask for confirmation
read -p "Run analysis? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Analysis cancelled."
    exit 0
fi

echo ""
echo "Starting automated analysis..."
echo "This will take approximately 5-15 minutes."
echo ""

# Run the automated pipeline
Rscript r_scripts/automated_copykat_analysis.R $CONFIG_FILE

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "ANALYSIS COMPLETE!"
    echo "========================================="
    echo ""
    echo "Results are in: results/glioblastoma_example_*/"
    echo ""
    echo "Generated files:"
    echo "  - HTML Report: *_report.html"
    echo "  - Cell Classifications: *_predictions.csv"
    echo "  - CNV Heatmap: *_copykat_heatmap.pdf"
    echo "  - QC Plots: plots/qc_metrics.pdf"
    echo "  - Summary Plots: plots/copykat_summary.pdf"
    echo "  - Chromosome Summary: chromosome_summary.csv"
    echo "  - Log File: logs/analysis.log"
    echo ""
    echo "Open the HTML report in your browser to view all results."
    echo ""
else
    echo ""
    echo "========================================="
    echo "ANALYSIS FAILED"
    echo "========================================="
    echo ""
    echo "Check the log file for error details:"
    echo "  results/glioblastoma_example_*/logs/analysis.log"
    echo ""
    exit 1
fi
