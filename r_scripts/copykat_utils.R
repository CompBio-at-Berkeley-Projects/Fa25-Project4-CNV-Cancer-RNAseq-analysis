# CopyKAT Utility Functions
# Reusable validation, preprocessing, and analysis helper functions

# ============================================================================
# Input Validation Functions
# ============================================================================

#' Validate expression matrix structure
#'
#' @param data Expression matrix (genes x cells)
#' @return List with validation results
validate_expression_matrix <- function(data) {
  results <- list(
    valid = TRUE,
    errors = character(),
    warnings = character(),
    metrics = list()
  )

  # Check basic structure
  if (!is.matrix(data) && !is.data.frame(data)) {
    results$valid <- FALSE
    results$errors <- c(results$errors, "Input is not a matrix or data.frame")
    return(results)
  }

  # Check dimensions
  if (nrow(data) < 100) {
    results$warnings <- c(results$warnings,
                          sprintf("Very few genes (%d). Expected >1000", nrow(data)))
  }

  if (ncol(data) < 50) {
    results$warnings <- c(results$warnings,
                          sprintf("Very few cells (%d). Expected >100 for reliable CNV detection", ncol(data)))
  }

  # Check for row/column names
  if (is.null(rownames(data))) {
    results$errors <- c(results$errors, "Missing gene names (rownames)")
    results$valid <- FALSE
  }

  if (is.null(colnames(data))) {
    results$errors <- c(results$errors, "Missing cell names (colnames)")
    results$valid <- FALSE
  }

  # Check for NA/Inf values
  # Convert to matrix for checking to handle data.frames
  data_matrix <- as.matrix(data)

  if (any(is.na(data_matrix))) {
    na_count <- sum(is.na(data_matrix))
    results$warnings <- c(results$warnings,
                          sprintf("Found %d NA values (%.2f%%)",
                                  na_count, 100 * na_count / length(data_matrix)))
  }

  if (any(is.infinite(data_matrix))) {
    results$errors <- c(results$errors, "Found infinite values")
    results$valid <- FALSE
  }

  # Store metrics
  results$metrics$n_genes <- nrow(data)
  results$metrics$n_cells <- ncol(data)
  results$metrics$sparsity <- sum(data_matrix == 0) / length(data_matrix)

  return(results)
}


#' Check data quality metrics
#'
#' @param data Expression matrix
#' @return List with quality metrics
assess_data_quality <- function(data) {
  quality <- list()

  # Genes per cell
  genes_per_cell <- colSums(data > 0)
  quality$genes_per_cell_median <- median(genes_per_cell)
  quality$genes_per_cell_mean <- mean(genes_per_cell)
  quality$genes_per_cell_min <- min(genes_per_cell)
  quality$genes_per_cell_max <- max(genes_per_cell)

  # UMI per cell (total counts)
  umi_per_cell <- colSums(data)
  quality$umi_per_cell_median <- median(umi_per_cell)
  quality$umi_per_cell_mean <- mean(umi_per_cell)

  # Cells per gene
  cells_per_gene <- rowSums(data > 0)
  quality$cells_per_gene_median <- median(cells_per_gene)

  # Mitochondrial percentage
  mt_genes <- grep("^MT-|^mt-", rownames(data), value = TRUE)
  if (length(mt_genes) > 0) {
    mt_counts <- colSums(data[mt_genes, , drop = FALSE])
    total_counts <- colSums(data)
    quality$mt_percent_median <- median(mt_counts / total_counts * 100)
    quality$mt_percent_mean <- mean(mt_counts / total_counts * 100)
    quality$n_mt_genes <- length(mt_genes)
  } else {
    quality$mt_percent_median <- NA
    quality$mt_percent_mean <- NA
    quality$n_mt_genes <- 0
  }

  # Overall sparsity
  quality$sparsity <- sum(data == 0) / length(data)

  return(quality)
}


# ============================================================================
# Data Preprocessing Functions
# ============================================================================

#' Detect if data is log-transformed
#'
#' @param data Expression matrix
#' @return List with detection results
detect_log_transform <- function(data) {
  results <- list(
    is_log_transformed = FALSE,
    method = "heuristic",
    confidence = "low"
  )

  # Check for negative values (strong indicator of log-transform)
  has_negative <- any(data < 0)

  # Check value range
  data_min <- min(data, na.rm = TRUE)
  data_max <- max(data, na.rm = TRUE)

  # Check distribution
  non_zero_values <- data[data != 0]
  if (length(non_zero_values) > 0) {
    value_range <- data_max - data_min
    mean_val <- mean(non_zero_values)

    # Heuristics:
    # 1. Negative values → definitely log-transformed
    # 2. Max value < 20 and min < 0 → likely log2
    # 3. Max value > 1000 → likely counts

    if (has_negative) {
      results$is_log_transformed <- TRUE
      results$confidence <- "high"
      results$method <- "negative_values"
    } else if (data_max < 20 && mean_val < 10) {
      results$is_log_transformed <- TRUE
      results$confidence <- "medium"
      results$method <- "value_range"
    } else if (data_max > 100) {
      results$is_log_transformed <- FALSE
      results$confidence <- "high"
      results$method <- "high_values"
    }
  }

  return(results)
}


#' Convert log-transformed data to counts
#'
#' @param data Expression matrix (log-transformed)
#' @param base Log base (2 for log2, exp(1) for natural log)
#' @return Count matrix
convert_log_to_counts <- function(data, base = 2) {
  # Handle negative values
  data[data < 0] <- 0

  # Reverse log transformation
  if (base == 2) {
    counts <- 2^data - 1
  } else if (base == exp(1)) {
    counts <- exp(data) - 1
  } else if (base == 10) {
    counts <- 10^data - 1
  } else {
    counts <- base^data - 1
  }

  # Remove any negative values from rounding errors
  counts[counts < 0] <- 0

  # Round to integers
  counts <- round(counts)

  return(counts)
}


#' Filter low-quality cells
#'
#' @param data Expression matrix
#' @param min_genes Minimum genes per cell
#' @param min_umi Minimum UMI per cell
#' @param max_mt_percent Maximum mitochondrial percentage
#' @return Filtered matrix
filter_cells <- function(data,
                         min_genes = 200,
                         min_umi = 500,
                         max_mt_percent = 20) {

  genes_per_cell <- colSums(data > 0)
  umi_per_cell <- colSums(data)

  # Mitochondrial filtering
  mt_genes <- grep("^MT-|^mt-", rownames(data), value = TRUE)
  if (length(mt_genes) > 0) {
    mt_percent <- colSums(data[mt_genes, , drop = FALSE]) / umi_per_cell * 100
    keep_cells <- (genes_per_cell >= min_genes) &
                  (umi_per_cell >= min_umi) &
                  (mt_percent <= max_mt_percent)
  } else {
    keep_cells <- (genes_per_cell >= min_genes) & (umi_per_cell >= min_umi)
  }

  filtered_data <- data[, keep_cells, drop = FALSE]

  return(list(
    data = filtered_data,
    n_removed = sum(!keep_cells),
    n_kept = sum(keep_cells)
  ))
}


#' Filter low-abundance genes
#'
#' @param data Expression matrix
#' @param min_cells Minimum cells expressing gene
#' @return Filtered matrix
filter_genes <- function(data, min_cells = 3) {
  cells_per_gene <- rowSums(data > 0)
  keep_genes <- cells_per_gene >= min_cells

  filtered_data <- data[keep_genes, , drop = FALSE]

  return(list(
    data = filtered_data,
    n_removed = sum(!keep_genes),
    n_kept = sum(keep_genes)
  ))
}


# ============================================================================
# Analysis Helper Functions
# ============================================================================

#' Safely run CopyKAT with error handling
#'
#' @param data Expression matrix
#' @param params List of CopyKAT parameters
#' @return CopyKAT result or NULL if failed
run_copykat_safe <- function(data, params) {
  result <- tryCatch(
    {
      do.call(copykat::copykat, c(list(rawmat = data), params))
    },
    error = function(e) {
      list(
        success = FALSE,
        error = conditionMessage(e),
        result = NULL
      )
    },
    warning = function(w) {
      # Continue despite warnings
      list(
        success = TRUE,
        warning = conditionMessage(w),
        result = suppressWarnings(do.call(copykat::copykat, c(list(rawmat = data), params)))
      )
    }
  )

  return(result)
}


# ============================================================================
# Visualization Functions
# ============================================================================

#' Plot quality control metrics
#'
#' @param data Expression matrix
#' @param output_file PDF output file
plot_qc_metrics <- function(data, output_file = NULL) {
  if (!is.null(output_file)) {
    pdf(output_file, width = 12, height = 8)
  }

  par(mfrow = c(2, 3))

  # Genes per cell
  genes_per_cell <- colSums(data > 0)
  hist(genes_per_cell, breaks = 50, main = "Genes per Cell",
       xlab = "Number of Genes", col = "skyblue", border = "white")
  abline(v = median(genes_per_cell), col = "red", lwd = 2, lty = 2)

  # UMI per cell (handle negative values from log-transformed data)
  umi_per_cell <- colSums(data)
  if (any(umi_per_cell < 0)) {
    # Plot raw values for log-transformed data
    hist(umi_per_cell, breaks = 50, main = "Expression Sum per Cell",
         xlab = "Sum of Expression", col = "lightgreen", border = "white")
  } else {
    hist(log10(umi_per_cell + 1), breaks = 50, main = "UMI per Cell (log10)",
         xlab = "log10(UMI + 1)", col = "lightgreen", border = "white")
  }

  # Cells per gene
  cells_per_gene <- rowSums(data > 0)
  hist(cells_per_gene, breaks = 50, main = "Cells per Gene",
       xlab = "Number of Cells", col = "lightcoral", border = "white")

  # MT percentage
  mt_genes <- grep("^MT-|^mt-", rownames(data), value = TRUE)
  if (length(mt_genes) > 0) {
    mt_percent <- colSums(data[mt_genes, , drop = FALSE]) / umi_per_cell * 100
    hist(mt_percent, breaks = 50, main = "Mitochondrial %",
         xlab = "MT%", col = "plum", border = "white")
    abline(v = 20, col = "red", lwd = 2, lty = 2)
  } else {
    plot.new()
    text(0.5, 0.5, "No MT genes detected", cex = 1.5)
  }

  # Sparsity
  sparsity_per_cell <- colSums(data == 0) / nrow(data) * 100
  hist(sparsity_per_cell, breaks = 50, main = "Data Sparsity",
       xlab = "% Zeros per Cell", col = "wheat", border = "white")

  # Gene expression distribution
  non_zero_expr <- data[data > 0]
  if (length(non_zero_expr) > 0) {
    hist(log10(non_zero_expr + 1), breaks = 100,
         main = "Expression Distribution (non-zero)",
         xlab = "log10(Expression + 1)", col = "lightblue", border = "white")
  }

  par(mfrow = c(1, 1))

  if (!is.null(output_file)) {
    dev.off()
  }
}


#' Plot CNV profile for a single cell
#'
#' @param cnv_matrix CNV matrix from CopyKAT
#' @param cell_name Cell name
#' @param chr_data Chromosome annotation
plot_cnv_profile <- function(cnv_matrix, cell_name, chr_data = NULL) {
  if (!cell_name %in% colnames(cnv_matrix)) {
    stop(sprintf("Cell %s not found in CNV matrix", cell_name))
  }

  profile <- cnv_matrix[, cell_name]

  plot(profile, type = "l", lwd = 1.5,
       main = paste("CNV Profile:", cell_name),
       ylab = "Copy Number",
       xlab = "Genomic Position",
       ylim = c(0, max(4, max(profile, na.rm = TRUE))))

  abline(h = 2, col = "red", lty = 2, lwd = 2)

  # Add chromosome boundaries if available
  if (!is.null(chr_data)) {
    chr_breaks <- which(diff(as.numeric(factor(chr_data$chrom))) != 0)
    abline(v = chr_breaks, col = "gray70", lty = 3)
  }

  legend("topright", legend = "Diploid (2N)", col = "red", lty = 2, lwd = 2)
}


#' Create summary plots for CopyKAT results
#'
#' @param result CopyKAT result object
#' @param output_file PDF output file
plot_copykat_summary <- function(result, output_file = NULL) {
  if (!is.null(output_file)) {
    pdf(output_file, width = 12, height = 8)
  }

  par(mfrow = c(2, 2))

  predictions <- result$prediction

  # Classification distribution
  class_table <- table(predictions$copykat.pred)
  barplot(class_table, main = "Cell Classification",
          ylab = "Number of Cells", col = c("skyblue", "coral"),
          names.arg = names(class_table))

  # Confidence distribution
  hist(predictions$copykat.confidence, breaks = 30,
       main = "Confidence Score Distribution",
       xlab = "Confidence Score", col = "lightgreen", border = "white")
  abline(v = 0.8, col = "red", lty = 2, lwd = 2)

  # Confidence by classification
  boxplot(copykat.confidence ~ copykat.pred, data = predictions,
          main = "Confidence by Classification",
          ylab = "Confidence Score",
          col = c("skyblue", "coral"))

  # Aneuploid fraction pie chart
  aneu_frac <- sum(predictions$copykat.pred == "aneuploid") / nrow(predictions)
  pie(c(aneu_frac, 1 - aneu_frac),
      labels = c(sprintf("Aneuploid\n%.1f%%", aneu_frac * 100),
                 sprintf("Diploid\n%.1f%%", (1 - aneu_frac) * 100)),
      col = c("coral", "skyblue"),
      main = "Cell Type Distribution")

  par(mfrow = c(1, 1))

  if (!is.null(output_file)) {
    dev.off()
  }
}
