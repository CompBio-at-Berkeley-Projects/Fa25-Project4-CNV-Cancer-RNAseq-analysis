#!/usr/bin/env Rscript

# Simple working CopyKAT analysis script
# This is a minimal implementation that actually runs CopyKAT

suppressPackageStartupMessages({
  library(copykat)
})

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Default parameters
input_file <- NULL
sample_name <- "sample"
output_dir <- "backend/results"
genome <- "hg20"
n_cores <- 2

# Parse arguments
i <- 1
while (i <= length(args)) {
  if (args[i] == "--input" && i < length(args)) {
    input_file <- args[i + 1]
    i <- i + 2
  } else if (args[i] == "--name" && i < length(args)) {
    sample_name <- args[i + 1]
    i <- i + 2
  } else if (args[i] == "--output" && i < length(args)) {
    output_dir <- args[i + 1]
    i <- i + 2
  } else if (args[i] == "--genome" && i < length(args)) {
    genome <- args[i + 1]
    i <- i + 2
  } else if (args[i] == "--cores" && i < length(args)) {
    n_cores <- as.integer(args[i + 1])
    i <- i + 2
  } else {
    i <- i + 1
  }
}

# Validate required arguments
if (is.null(input_file)) {
  cat("Error: --input is required\n", file = stderr())
  quit(save = "no", status = 1)
}

if (!file.exists(input_file)) {
  cat(paste0("Error: Input file not found: ", input_file, "\n"), file = stderr())
  quit(save = "no", status = 1)
}

# Create output directory with timestamp
timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
output_subdir <- file.path(output_dir, paste0(sample_name, "_", timestamp))
dir.create(output_subdir, showWarnings = FALSE, recursive = TRUE)

cat(paste0("Starting CopyKAT analysis...\n"))
cat(paste0("Input: ", input_file, "\n"))
cat(paste0("Output: ", output_subdir, "\n"))
cat(paste0("Sample: ", sample_name, "\n"))
cat(paste0("Genome: ", genome, "\n"))

# Load data
cat("Loading data...\n")
if (grepl("\\.gz$", input_file)) {
  exp_data <- read.table(gzfile(input_file), header = TRUE, row.names = 1, sep = "\t", check.names = FALSE)
} else if (grepl("\\.rds$", input_file)) {
  exp_data <- readRDS(input_file)
} else {
  exp_data <- read.table(input_file, header = TRUE, row.names = 1, sep = "\t", check.names = FALSE)
}

cat(paste0("Loaded: ", nrow(exp_data), " genes x ", ncol(exp_data), " cells\n"))

# Check for log-transformed data and convert to counts if needed
max_val <- max(exp_data, na.rm = TRUE)
min_val <- min(exp_data, na.rm = TRUE)
cat(paste0("Data range: ", round(min_val, 2), " to ", round(max_val, 2), "\n"))

if (max_val < 50 && min_val >= 0) {
  cat("Data appears log-transformed. Converting to counts...\n")
  # Assume log2 transformation: counts = 2^data - 1
  exp_data <- 2^exp_data - 1
  exp_data[exp_data < 0] <- 0  # Ensure no negative values
  cat("Conversion complete\n")
} else if (min_val < 0) {
  cat("Data contains negative values. Adding offset...\n")
  exp_data <- exp_data - min_val
}

# Check minimum requirements
if (ncol(exp_data) < 50) {
  cat("Warning: CopyKAT works best with at least 50 cells\n", file = stderr())
}

# Change to output directory (CopyKAT writes files to working directory)
orig_wd <- getwd()
setwd(output_subdir)

# Run CopyKAT
cat("Running CopyKAT analysis...\n")
tryCatch(
  {
    copykat_result <- copykat(
      rawmat = exp_data,
      id.type = "S",
      cell.line = "no",
      ngene.chr = 5,
      LOW.DR = 0.05,
      UP.DR = 0.10,
      win.size = 25,
      KS.cut = 0.1,
      sam.name = sample_name,
      distance = "euclidean",
      norm.cell.names = "",
      output.seg = "FALSE",
      plot.genes = "TRUE",
      genome = genome,
      n.cores = n_cores
    )

    cat("CopyKAT analysis complete!\n")

    # Print summary
    predictions <- copykat_result$prediction
    class_counts <- table(predictions$copykat.pred)
    cat("\nCell Classifications:\n")
    for (class_name in names(class_counts)) {
      count <- class_counts[class_name]
      pct <- round(count / nrow(predictions) * 100, 2)
      cat(paste0("  ", class_name, ": ", count, " (", pct, "%)\n"))
    }

    cat(paste0("\nResults saved to: ", output_subdir, "\n"))

    # Return to original directory
    setwd(orig_wd)

    # Exit successfully
    quit(save = "no", status = 0)
  },
  error = function(e) {
    cat(paste0("Error during CopyKAT analysis: ", conditionMessage(e), "\n"), file = stderr())
    setwd(orig_wd)
    quit(save = "no", status = 1)
  }
)
