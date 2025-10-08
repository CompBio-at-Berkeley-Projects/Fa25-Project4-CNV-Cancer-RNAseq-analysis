# CopyKAT Command-Line Usage Guide

Practical guide for running CopyKAT from the command line, including automation, batch processing, and cluster computing scenarios.

---

## Table of Contents
1. [Basic CLI Workflow](#basic-cli-workflow)
2. [Command-Line Arguments](#command-line-arguments)
3. [Batch Processing](#batch-processing)
4. [HPC and Cluster Usage](#hpc-and-cluster-usage)
5. [Automation Scripts](#automation-scripts)
6. [Output Management](#output-management)
7. [Performance Optimization](#performance-optimization)

---

## Basic CLI Workflow

### Single Sample Analysis

**Step 1: Activate environment**
```bash
# Navigate to project
cd ~/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Activate conda environment
conda activate Project4-CNV-Cancer-RNAseq
```

**Step 2: Launch R**
```bash
R --no-save --quiet
```

**Step 3: Run CopyKAT**
```r
library(copykat)

# Load data
data <- read.table(gzfile("data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"),
                   header = TRUE, row.names = 1, sep = "\t", check.names = FALSE)

# Run analysis
result <- copykat(rawmat = data,
                  id.type = "S",
                  cell.line = "no",
                  ngene.chr = 5,
                  sam.name = "sample_001",
                  distance = "euclidean",
                  genome = "hg20",
                  n.cores = 4)

# Save results
saveRDS(result, file = "results/sample_001_copykat_result.rds")
```

**Step 4: Exit**
```r
quit(save = "no")
```

---

## Command-Line Arguments

### Using R CMD BATCH

**Create analysis script** (analysis.R):
```r
# analysis.R
library(copykat)

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 3) {
  stop("Usage: Rscript analysis.R <input_file> <output_dir> <sample_name>")
}

input_file <- args[1]
output_dir <- args[2]
sample_name <- args[3]

# Optional parameters with defaults
genome <- ifelse(length(args) > 3, args[4], "hg20")
n_cores <- ifelse(length(args) > 4, as.numeric(args[5]), 4)

# Load data
cat("Loading data from:", input_file, "\n")
data <- read.table(gzfile(input_file),
                   header = TRUE, row.names = 1,
                   sep = "\t", check.names = FALSE)

cat("Data dimensions:", nrow(data), "genes x", ncol(data), "cells\n")

# Create output directory
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
setwd(output_dir)

# Run CopyKAT
cat("Running CopyKAT...\n")
start_time <- Sys.time()

result <- copykat(rawmat = data,
                  id.type = "S",
                  cell.line = "no",
                  ngene.chr = 5,
                  sam.name = sample_name,
                  distance = "euclidean",
                  genome = genome,
                  n.cores = n_cores)

end_time <- Sys.time()
cat("Analysis completed in", difftime(end_time, start_time, units = "mins"), "minutes\n")

# Save R object
saveRDS(result, file = paste0(sample_name, "_copykat_result.rds"))
cat("Results saved to:", output_dir, "\n")
```

**Run from command line**:
```bash
# Basic usage
Rscript analysis.R \
  data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  results/sample_001 \
  sample_001

# With optional parameters
Rscript analysis.R \
  data/raw/melanoma_compressed/GSE72056_melanoma_single_cell_revised_v2.txt.gz \
  results/melanoma_001 \
  melanoma_001 \
  hg20 \
  8
```

---

### Using R Wrapper Script

**Create wrapper** (run_copykat.R):
```r
#!/usr/bin/env Rscript

# run_copykat.R - Full parameter wrapper for CopyKAT

library(copykat)
library(optparse)

# Define command-line options
option_list <- list(
  make_option(c("-i", "--input"), type = "character", default = NULL,
              help = "Input expression matrix file (required)", metavar = "FILE"),
  make_option(c("-o", "--output"), type = "character", default = "results",
              help = "Output directory [default %default]", metavar = "DIR"),
  make_option(c("-n", "--name"), type = "character", default = "sample",
              help = "Sample name [default %default]", metavar = "NAME"),
  make_option(c("-g", "--genome"), type = "character", default = "hg20",
              help = "Genome build: hg20, hg19, mm10, mm9 [default %default]"),
  make_option(c("-t", "--idtype"), type = "character", default = "S",
              help = "Gene ID type: S (Symbol) or E (Ensembl) [default %default]"),
  make_option(c("-c", "--cores"), type = "integer", default = 4,
              help = "Number of CPU cores [default %default]"),
  make_option(c("--cellline"), type = "character", default = "no",
              help = "Cell line sample: yes or no [default %default]"),
  make_option(c("--ngene"), type = "integer", default = 5,
              help = "Min genes per chromosome [default %default]"),
  make_option(c("--lowdr"), type = "numeric", default = 0.05,
              help = "Lower detection rate threshold [default %default]"),
  make_option(c("--updr"), type = "numeric", default = 0.1,
              help = "Upper detection rate threshold [default %default]"),
  make_option(c("--winsize"), type = "integer", default = 25,
              help = "Smoothing window size [default %default]"),
  make_option(c("--kscut"), type = "numeric", default = 0.1,
              help = "KS test p-value cutoff [default %default]"),
  make_option(c("--distance"), type = "character", default = "euclidean",
              help = "Distance metric: euclidean, pearson, spearman [default %default]"),
  make_option(c("--normcells"), type = "character", default = NULL,
              help = "File with known normal cell names (one per line)", metavar = "FILE")
)

# Parse arguments
opt_parser <- OptionParser(option_list = option_list,
                           description = "Run CopyKAT CNV analysis from command line")
opt <- parse_args(opt_parser)

# Validate required arguments
if (is.null(opt$input)) {
  print_help(opt_parser)
  stop("Input file is required (-i/--input)", call. = FALSE)
}

# Load data
cat("Loading data from:", opt$input, "\n")
if (grepl("\\.gz$", opt$input)) {
  data <- read.table(gzfile(opt$input), header = TRUE, row.names = 1,
                     sep = "\t", check.names = FALSE)
} else {
  data <- read.table(opt$input, header = TRUE, row.names = 1,
                     sep = "\t", check.names = FALSE)
}

cat("Data dimensions:", nrow(data), "genes x", ncol(data), "cells\n")

# Load normal cell names if provided
norm_cells <- NULL
if (!is.null(opt$normcells)) {
  norm_cells <- readLines(opt$normcells)
  cat("Loaded", length(norm_cells), "known normal cell names\n")
}

# Create output directory
dir.create(opt$output, showWarnings = FALSE, recursive = TRUE)
setwd(opt$output)

# Run CopyKAT
cat("\n=== CopyKAT Parameters ===\n")
cat("Sample name:", opt$name, "\n")
cat("Genome:", opt$genome, "\n")
cat("ID type:", opt$idtype, "\n")
cat("Cell line:", opt$cellline, "\n")
cat("Cores:", opt$cores, "\n")
cat("Parameters: ngene.chr =", opt$ngene,
    "LOW.DR =", opt$lowdr,
    "UP.DR =", opt$updr,
    "win.size =", opt$winsize,
    "KS.cut =", opt$kscut, "\n")
cat("Distance:", opt$distance, "\n")
cat("=========================\n\n")

start_time <- Sys.time()

result <- copykat(rawmat = data,
                  id.type = opt$idtype,
                  cell.line = opt$cellline,
                  ngene.chr = opt$ngene,
                  LOW.DR = opt$lowdr,
                  UP.DR = opt$updr,
                  win.size = opt$winsize,
                  KS.cut = opt$kscut,
                  sam.name = opt$name,
                  distance = opt$distance,
                  norm.cell.names = norm_cells,
                  genome = opt$genome,
                  n.cores = opt$cores)

end_time <- Sys.time()
runtime <- difftime(end_time, start_time, units = "mins")

# Print summary
cat("\n=== Analysis Complete ===\n")
cat("Runtime:", round(runtime, 2), "minutes\n")
cat("Output directory:", opt$output, "\n")

predictions <- result$prediction
cat("\nCell classifications:\n")
print(table(predictions$copykat.pred))

cat("\nMean confidence scores:\n")
print(tapply(predictions$copykat.confidence,
             predictions$copykat.pred, mean))

# Save R object
saveRDS(result, file = paste0(opt$name, "_copykat_result.rds"))
cat("\nSaved results to:", paste0(opt$name, "_copykat_result.rds"), "\n")
```

**Usage examples**:
```bash
# Make executable
chmod +x run_copykat.R

# Basic usage with defaults
./run_copykat.R \
  -i data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  -o results/gbm_sample \
  -n gbm_001

# High resolution analysis
./run_copykat.R \
  -i data/melanoma.txt.gz \
  -o results/melanoma_highres \
  -n melanoma_001 \
  --winsize 15 \
  --kscut 0.05 \
  --cores 8

# With known normal cells
./run_copykat.R \
  -i data/tumor_sample.txt.gz \
  -o results/tumor_guided \
  -n tumor_001 \
  --normcells data/normal_cells.txt \
  --cores 8

# Cell line analysis
./run_copykat.R \
  -i data/cellline.txt.gz \
  -o results/cellline \
  -n cellline_001 \
  --cellline yes \
  --genome hg20
```

---

## Batch Processing

### Processing Multiple Samples

**Create batch script** (batch_copykat.sh):
```bash
#!/bin/bash

# batch_copykat.sh - Process multiple samples

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="data/raw"
OUTPUT_DIR="results/batch"
CORES=4
GENOME="hg20"

# Sample list (one per line)
SAMPLES=(
  "sample_001:glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"
  "sample_002:melanoma_compressed/GSE72056_melanoma_single_cell_revised_v2.txt.gz"
  "sample_003:ovarian_compressed/GSE118828_RAW/sample3.txt.gz"
)

# Create log directory
mkdir -p "${OUTPUT_DIR}/logs"

# Process each sample
for sample_info in "${SAMPLES[@]}"; do
  # Parse sample info
  IFS=':' read -r sample_name sample_file <<< "$sample_info"

  input_file="${INPUT_DIR}/${sample_file}"
  output_dir="${OUTPUT_DIR}/${sample_name}"
  log_file="${OUTPUT_DIR}/logs/${sample_name}.log"

  echo "Processing ${sample_name}..."
  echo "  Input: ${input_file}"
  echo "  Output: ${output_dir}"

  # Run CopyKAT
  Rscript run_copykat.R \
    -i "$input_file" \
    -o "$output_dir" \
    -n "$sample_name" \
    --genome "$GENOME" \
    --cores "$CORES" \
    > "$log_file" 2>&1

  if [ $? -eq 0 ]; then
    echo "  Status: SUCCESS"
  else
    echo "  Status: FAILED (check ${log_file})"
  fi

  echo ""
done

echo "Batch processing complete!"
echo "Results in: ${OUTPUT_DIR}"
```

**Run batch processing**:
```bash
chmod +x batch_copykat.sh
./batch_copykat.sh
```

---

### Parallel Batch Processing

**Using GNU Parallel**:
```bash
# Install GNU parallel
# macOS: brew install parallel
# Linux: apt-get install parallel

# Create sample list file (samples.txt)
cat > samples.txt << 'EOF'
sample_001 data/raw/sample1.txt.gz results/sample_001
sample_002 data/raw/sample2.txt.gz results/sample_002
sample_003 data/raw/sample3.txt.gz results/sample_003
sample_004 data/raw/sample4.txt.gz results/sample_004
EOF

# Process in parallel (4 at a time)
parallel --colsep ' ' -j 4 \
  'Rscript run_copykat.R -i {2} -o {3} -n {1} --cores 2' \
  :::: samples.txt
```

---

## HPC and Cluster Usage

### SLURM Job Submission

**Create SLURM script** (copykat_slurm.sh):
```bash
#!/bin/bash
#SBATCH --job-name=copykat_analysis
#SBATCH --output=logs/copykat_%j.out
#SBATCH --error=logs/copykat_%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --partition=shared

# Load modules
module load anaconda3
module load R/4.5.1

# Activate conda environment
source activate Project4-CNV-Cancer-RNAseq

# Get parameters from command line
INPUT_FILE=$1
OUTPUT_DIR=$2
SAMPLE_NAME=$3

# Create output directory
mkdir -p $OUTPUT_DIR
mkdir -p logs

# Run CopyKAT
Rscript run_copykat.R \
  -i $INPUT_FILE \
  -o $OUTPUT_DIR \
  -n $SAMPLE_NAME \
  --cores $SLURM_CPUS_PER_TASK \
  --genome hg20

echo "Job complete: $SAMPLE_NAME"
```

**Submit jobs**:
```bash
# Single job
sbatch copykat_slurm.sh \
  data/sample_001.txt.gz \
  results/sample_001 \
  sample_001

# Array job for multiple samples
sbatch --array=1-10 copykat_array.sh
```

**Array job script** (copykat_array.sh):
```bash
#!/bin/bash
#SBATCH --job-name=copykat_array
#SBATCH --output=logs/copykat_%A_%a.out
#SBATCH --error=logs/copykat_%A_%a.err
#SBATCH --array=1-10
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G

# Sample list (modify for your data)
SAMPLES=(
  "sample_001"
  "sample_002"
  "sample_003"
  "sample_004"
  "sample_005"
  "sample_006"
  "sample_007"
  "sample_008"
  "sample_009"
  "sample_010"
)

# Get sample for this array task
SAMPLE_NAME=${SAMPLES[$SLURM_ARRAY_TASK_ID - 1]}
INPUT_FILE="data/raw/${SAMPLE_NAME}.txt.gz"
OUTPUT_DIR="results/${SAMPLE_NAME}"

# Load environment
module load anaconda3 R/4.5.1
source activate Project4-CNV-Cancer-RNAseq

# Run analysis
Rscript run_copykat.R \
  -i $INPUT_FILE \
  -o $OUTPUT_DIR \
  -n $SAMPLE_NAME \
  --cores $SLURM_CPUS_PER_TASK

echo "Array task $SLURM_ARRAY_TASK_ID complete: $SAMPLE_NAME"
```

---

### PBS/Torque Job Submission

```bash
#!/bin/bash
#PBS -N copykat_analysis
#PBS -l nodes=1:ppn=16
#PBS -l walltime=04:00:00
#PBS -l mem=64gb
#PBS -o logs/copykat_${PBS_JOBID}.out
#PBS -e logs/copykat_${PBS_JOBID}.err

cd $PBS_O_WORKDIR

# Load modules
module load R/4.5.1

# Run analysis
Rscript run_copykat.R \
  -i $INPUT_FILE \
  -o $OUTPUT_DIR \
  -n $SAMPLE_NAME \
  --cores 16
```

---

## Automation Scripts

### Complete Analysis Pipeline

**Create pipeline script** (pipeline.sh):
```bash
#!/bin/bash

# pipeline.sh - Complete CopyKAT analysis pipeline

set -e  # Exit on error

SAMPLE_NAME=$1
INPUT_FILE=$2
OUTPUT_DIR=${3:-"results/${SAMPLE_NAME}"}

if [ -z "$SAMPLE_NAME" ] || [ -z "$INPUT_FILE" ]; then
  echo "Usage: ./pipeline.sh <sample_name> <input_file> [output_dir]"
  exit 1
fi

echo "=== CopyKAT Analysis Pipeline ==="
echo "Sample: $SAMPLE_NAME"
echo "Input: $INPUT_FILE"
echo "Output: $OUTPUT_DIR"
echo ""

# Step 1: Quality check
echo "[1/5] Quality check..."
Rscript - <<EOF
data <- read.table(gzfile("$INPUT_FILE"), header=TRUE, row.names=1, sep="\t")
cat("  Dimensions:", nrow(data), "genes x", ncol(data), "cells\n")
cat("  UMI/cell median:", median(colSums(data)), "\n")
cat("  Genes/cell median:", median(colSums(data > 0)), "\n")
mt_genes <- grep("^MT-", rownames(data), value=TRUE)
if (length(mt_genes) > 0) {
  mt_pct <- median(colSums(data[mt_genes,]) / colSums(data)) * 100
  cat("  MT% median:", round(mt_pct, 2), "%\n")
}
EOF

# Step 2: Run CopyKAT
echo ""
echo "[2/5] Running CopyKAT..."
Rscript run_copykat.R \
  -i "$INPUT_FILE" \
  -o "$OUTPUT_DIR" \
  -n "$SAMPLE_NAME" \
  --cores 8

# Step 3: Generate summary report
echo ""
echo "[3/5] Generating summary report..."
Rscript - <<EOF
result <- readRDS("${OUTPUT_DIR}/${SAMPLE_NAME}_copykat_result.rds")
pred <- result\$prediction

# Summary statistics
sink("${OUTPUT_DIR}/${SAMPLE_NAME}_summary.txt")
cat("CopyKAT Analysis Summary\n")
cat("========================\n\n")
cat("Sample:", "$SAMPLE_NAME", "\n\n")
cat("Cell Classifications:\n")
print(table(pred\$copykat.pred))
cat("\nConfidence Scores:\n")
print(tapply(pred\$copykat.confidence, pred\$copykat.pred, summary))
cat("\nAneuploid Fraction:",
    round(sum(pred\$copykat.pred == "aneuploid") / nrow(pred) * 100, 2), "%\n")
sink()

cat("Summary saved to: ${OUTPUT_DIR}/${SAMPLE_NAME}_summary.txt\n")
EOF

# Step 4: Create visualizations
echo ""
echo "[4/5] Creating additional visualizations..."
Rscript - <<EOF
result <- readRDS("${OUTPUT_DIR}/${SAMPLE_NAME}_copykat_result.rds")

# Confidence distribution plot
pdf("${OUTPUT_DIR}/${SAMPLE_NAME}_confidence_distribution.pdf", width=8, height=6)
pred <- result\$prediction
hist(pred\$copykat.confidence, breaks=30,
     main="Confidence Score Distribution",
     xlab="Confidence Score", col="skyblue")
dev.off()

# CNV profile for top aneuploid cell
aneuploid_cells <- pred\$cell.names[pred\$copykat.pred == "aneuploid"]
if (length(aneuploid_cells) > 0) {
  top_cell <- aneuploid_cells[1]
  pdf("${OUTPUT_DIR}/${SAMPLE_NAME}_example_cnv_profile.pdf", width=12, height=6)
  plot(result\$CNV.matrix[, top_cell], type="l",
       main=paste("CNV Profile:", top_cell),
       ylab="Copy Number", xlab="Genome Position")
  abline(h=2, col="red", lty=2, lwd=2)
  dev.off()
}

cat("Visualizations saved\n")
EOF

# Step 5: Compress results
echo ""
echo "[5/5] Compressing results..."
cd "$OUTPUT_DIR"
tar -czf "${SAMPLE_NAME}_copykat_results.tar.gz" \
  "${SAMPLE_NAME}"_copykat_*.txt \
  "${SAMPLE_NAME}"_copykat_*.pdf \
  "${SAMPLE_NAME}"_*.pdf \
  "${SAMPLE_NAME}_summary.txt" \
  "${SAMPLE_NAME}_copykat_result.rds"
cd -

echo ""
echo "=== Pipeline Complete ==="
echo "Results: $OUTPUT_DIR"
echo "Archive: ${OUTPUT_DIR}/${SAMPLE_NAME}_copykat_results.tar.gz"
```

**Run pipeline**:
```bash
chmod +x pipeline.sh

./pipeline.sh sample_001 data/raw/sample_001.txt.gz
```

---

## Output Management

### Organizing Results

**Directory structure**:
```
results/
├── sample_001/
│   ├── sample_001_copykat_prediction.txt
│   ├── sample_001_copykat_CNA_results.txt
│   ├── sample_001_copykat_CNA_raw_results.txt
│   ├── sample_001_copykat_heatmap.pdf
│   ├── sample_001_copykat_result.rds
│   ├── sample_001_summary.txt
│   └── sample_001_copykat_results.tar.gz
├── sample_002/
│   └── ...
└── logs/
    ├── sample_001.log
    └── sample_002.log
```

### Extracting Key Results

**Create extraction script** (extract_results.sh):
```bash
#!/bin/bash

# extract_results.sh - Extract key results from multiple samples

RESULTS_DIR=${1:-"results"}
OUTPUT_CSV="combined_results.csv"

echo "sample_name,total_cells,aneuploid_cells,diploid_cells,aneuploid_pct,mean_conf_aneuploid,mean_conf_diploid" > $OUTPUT_CSV

for sample_dir in $RESULTS_DIR/*/; do
  sample_name=$(basename "$sample_dir")
  pred_file="${sample_dir}${sample_name}_copykat_prediction.txt"

  if [ -f "$pred_file" ]; then
    Rscript - "$pred_file" "$sample_name" >> $OUTPUT_CSV <<'EOF'
args <- commandArgs(trailingOnly = TRUE)
pred <- read.table(args[1], header=TRUE, sep="\t")
sample <- args[2]

total <- nrow(pred)
aneuploid <- sum(pred$copykat.pred == "aneuploid")
diploid <- sum(pred$copykat.pred == "diploid")
pct <- round(aneuploid / total * 100, 2)

conf_aneu <- mean(pred$copykat.confidence[pred$copykat.pred == "aneuploid"])
conf_dip <- mean(pred$copykat.confidence[pred$copykat.pred == "diploid"])

cat(sample, total, aneuploid, diploid, pct,
    round(conf_aneu, 3), round(conf_dip, 3), sep=",", "\n")
EOF
  fi
done

echo "Combined results saved to: $OUTPUT_CSV"
```

---

## Performance Optimization

### Resource Allocation

**CPU cores**:
```bash
# Check available cores
nproc  # Linux
sysctl -n hw.ncpu  # macOS

# Optimal: Use 75% of available cores
# Example: 8 cores available → use 6
Rscript run_copykat.R -i data.txt.gz -n sample --cores 6
```

**Memory estimation**:
```
Required RAM ≈ (cells × genes × 8 bytes × 3-5 factor)

Examples:
- 500 cells × 10,000 genes ≈ 8-12 GB
- 2,000 cells × 15,000 genes ≈ 16-24 GB
- 5,000 cells × 20,000 genes ≈ 32-48 GB
```

### Monitoring Resources

**Create monitoring script**:
```bash
#!/bin/bash

# monitor_copykat.sh - Monitor CopyKAT process

PID=$1

if [ -z "$PID" ]; then
  echo "Usage: ./monitor_copykat.sh <process_id>"
  exit 1
fi

echo "Monitoring process $PID"
echo "Time,CPU%,MEM_GB" > monitor_${PID}.csv

while kill -0 $PID 2>/dev/null; do
  timestamp=$(date +%s)
  cpu=$(ps -p $PID -o %cpu | tail -1)
  mem_kb=$(ps -p $PID -o rss | tail -1)
  mem_gb=$(echo "scale=2; $mem_kb / 1024 / 1024" | bc)

  echo "$timestamp,$cpu,$mem_gb" >> monitor_${PID}.csv
  sleep 30
done

echo "Process complete. Monitoring data: monitor_${PID}.csv"
```

---

## See Also

- [08_BEGINNER_TUTORIAL.md](08_BEGINNER_TUTORIAL.md) - Hands-on tutorial
- [03_PARAMETERS_REFERENCE.md](03_PARAMETERS_REFERENCE.md) - Parameter details
- [06_PYTHON_R_INTEGRATION.md](06_PYTHON_R_INTEGRATION.md) - Python integration
- [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) - Common issues
