# Test script for CopyKAT installation and basic functionality
# This script tests the environment setup and runs CopyKAT on a subset of the data

cat("==================================================\n")
cat("CopyKAT Test Script\n")
cat("==================================================\n\n")

# Test 1: Load required libraries
cat("Test 1: Loading CopyKAT library...\n")
tryCatch({
  library(copykat)
  cat("SUCCESS: CopyKAT loaded successfully\n\n")
}, error = function(e) {
  cat("ERROR: Failed to load CopyKAT\n")
  cat("Error message:", e$message, "\n")
  cat("Please make sure you have installed CopyKAT using:\n")
  cat("R -e 'remotes::install_github(\"navinlabcode/copykat\")'\n\n")
  quit(status = 1)
})

# Test 2: Check data files exist
cat("Test 2: Checking for data files...\n")
melanoma_file <- "data/raw/melanoma_compressed/GSE72056_melanoma_single_cell_revised_v2.txt.gz"
glio_file <- "data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"

if (file.exists(melanoma_file)) {
  cat("SUCCESS: Melanoma data file found\n")
} else {
  cat("WARNING: Melanoma data file not found at:", melanoma_file, "\n")
}

if (file.exists(glio_file)) {
  cat("SUCCESS: Glioblastoma data file found\n")
} else {
  cat("WARNING: Glioblastoma data file not found at:", glio_file, "\n")
}
cat("\n")

# Test 3: Load a small subset of glioblastoma data (smaller dataset for quick testing)
cat("Test 3: Loading glioblastoma data (small dataset for testing)...\n")
tryCatch({
  raw_data <- read.table(gzfile(glio_file),
                         header = TRUE,
                         row.names = 1,
                         sep = "\t",
                         check.names = FALSE)

  cat("SUCCESS: Data loaded successfully\n")
  cat("  Dimensions:", nrow(raw_data), "genes x", ncol(raw_data), "cells\n")
  cat("  First few gene names:", paste(head(rownames(raw_data), 5), collapse = ", "), "\n")
  cat("  First few cell names:", paste(head(colnames(raw_data), 5), collapse = ", "), "\n\n")
}, error = function(e) {
  cat("ERROR: Failed to load data\n")
  cat("Error message:", e$message, "\n\n")
  quit(status = 1)
})

# Test 4: Run CopyKAT on a larger subset (100 cells for better results)
cat("Test 4: Running CopyKAT on subset of data (100 cells)...\n")
cat("This will take 5-15 minutes. Please wait...\n\n")

# Select first 100 cells - CopyKAT needs enough cells for baseline
test_data <- raw_data[, seq_len(min(100, ncol(raw_data)))]

# Convert negative values to 0 and ensure data is non-negative
# The data appears to be log-transformed, so we need to handle it properly
cat("Preprocessing data: converting to counts format...\n")
test_data[test_data < 0] <- 0
test_data <- 2^test_data - 1  # Reverse log2 transformation
test_data[test_data < 0] <- 0  # Ensure no negative values
test_data <- round(test_data)  # CopyKAT expects integer-like counts

cat("  Data range after preprocessing: min =",
    min(test_data), ", max =", max(test_data), "\n\n")

# Create output directory
if (!dir.exists("results")) {
  dir.create("results", recursive = TRUE)
}

# Change to results directory for output
setwd("results")

tryCatch({
  # Run CopyKAT with adjusted parameters
  copykat_test <- copykat(
    rawmat = test_data,
    id.type = "S",  # Symbol gene names
    cell.line = "no",
    ngene.chr = 5,  # Minimum genes per chromosome
    win.size = 25,  # Window size for smoothing
    KS.cut = 0.1,   # Statistical threshold
    sam.name = "test_glioblastoma",
    distance = "euclidean",
    norm.cell.names = "",
    output.seg = "FALSE",
    plot.genes = "TRUE",
    genome = "hg20",
    n.cores = 1
  )

  cat("\nSUCCESS: CopyKAT analysis completed\n")
  cat("Output files saved in results/ directory:\n")
  cat("  - results/test_glioblastoma_copykat_prediction.txt\n")
  cat("  - results/test_glioblastoma_copykat_CNA_results.txt\n")
  cat("  - results/test_glioblastoma_copykat_CNA_raw_results.txt\n\n")

  # Print prediction summary
  if (!is.null(copykat_test$prediction)) {
    pred_table <- table(copykat_test$prediction$copykat.pred)
    cat("Cell classification results:\n")
    print(pred_table)
    cat("\n")
  }

  cat("If you see output files and classification results,\n")
  cat("CopyKAT is working correctly!\n\n")

}, error = function(e) {
  cat("ERROR: CopyKAT analysis failed\n")
  cat("Error message:", e$message, "\n")
  cat("\nThis could be due to:\n")
  cat("  1. Data format issues\n")
  cat("  2. Insufficient memory\n")
  cat("  3. Missing dependencies\n\n")
})

cat("==================================================\n")
cat("Test Complete\n")
cat("==================================================\n")
cat("\nNext steps:\n")
cat("1. Check the output files generated in the current directory\n")
cat("2. If successful, you can run full analysis on complete datasets\n")
cat("3. Adjust parameters as needed for your analysis\n\n")
