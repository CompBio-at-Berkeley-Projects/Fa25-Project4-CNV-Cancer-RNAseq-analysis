#!/usr/bin/env Rscript

# =============================================================================
# Automated CopyKAT Analysis Pipeline
# =============================================================================
# Production-grade pipeline with comprehensive error handling, validation,
# preprocessing, analysis, and reporting
#
# Usage:
#   Rscript automated_copykat_analysis.R [config_file]
#   Rscript automated_copykat_analysis.R --input data.txt.gz --name sample_001
#
# =============================================================================

# Suppress startup messages
suppressPackageStartupMessages({
  library(copykat)
  library(yaml)
  library(logger)
})

# Source utility functions
source("r_scripts/copykat_utils.R")

# =============================================================================
# Configuration and Setup
# =============================================================================

#' Parse command line arguments
parse_args <- function() {
  args <- commandArgs(trailingOnly = TRUE)

  if (length(args) == 0) {
    # Use default config
    return(list(config_file = "config/analysis_config.yaml", mode = "config"))
  } else if (length(args) == 1 && !grepl("^--", args[1])) {
    # Config file specified
    return(list(config_file = args[1], mode = "config"))
  } else {
    # Parse named arguments
    params <- list(mode = "cli")
    i <- 1
    while (i <= length(args)) {
      if (args[i] == "--input" && i < length(args)) {
        params$input_file <- args[i + 1]
        i <- i + 2
      } else if (args[i] == "--output" && i < length(args)) {
        params$output_dir <- args[i + 1]
        i <- i + 2
      } else if (args[i] == "--name" && i < length(args)) {
        params$sample_name <- args[i + 1]
        i <- i + 2
      } else if (args[i] == "--genome" && i < length(args)) {
        params$genome <- args[i + 1]
        i <- i + 2
      } else if (args[i] == "--cores" && i < length(args)) {
        params$n_cores <- as.integer(args[i + 1])
        i <- i + 2
      } else {
        i <- i + 1
      }
    }
    return(params)
  }
}


#' Load configuration from YAML file
load_config <- function(config_file) {
  if (!file.exists(config_file)) {
    stop(sprintf("Config file not found: %s", config_file))
  }

  tryCatch(
    {
      config <- yaml::read_yaml(config_file)
      log_info("Configuration loaded from: {config_file}")
      return(config)
    },
    error = function(e) {
      stop(sprintf("Error loading config file: %s", conditionMessage(e)))
    }
  )
}


#' Setup output directory and logging
setup_output <- function(config) {
  # Create output directory with absolute path
  base_dir <- config$output$directory
  sample_name <- config$output$sample_name

  if (config$output$timestamp) {
    timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
    output_dir <- file.path(base_dir, paste0(sample_name, "_", timestamp))
  } else {
    output_dir <- file.path(base_dir, sample_name)
  }

  dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
  output_dir <- normalizePath(output_dir)  # Convert to absolute path
  dir.create(file.path(output_dir, "logs"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(output_dir, "plots"), showWarnings = FALSE, recursive = TRUE)

  # Setup logging with absolute path (survives setwd changes)
  log_file <- normalizePath(file.path(output_dir, "logs", "analysis.log"), mustWork = FALSE)
  log_appender(appender_tee(log_file))
  log_threshold(config$logging$level)

  log_info(paste(rep("=", 80), collapse = ""))
  log_info("CopyKAT Automated Analysis Pipeline")
  log_info(paste(rep("=", 80), collapse = ""))
  log_info("Start time: {Sys.time()}")
  log_info("Output directory: {output_dir}")
  log_info("")

  return(output_dir)
}


# =============================================================================
# Data Loading and Validation
# =============================================================================

#' Load expression matrix
load_data <- function(config) {
  input_file <- config$input$file

  log_info("STEP 1: Loading Data")
  log_info(paste(rep("-", 80), collapse = ""))
  log_info("Input file: {input_file}")

  if (!file.exists(input_file)) {
    log_error("Input file not found: {input_file}")
    stop("Input file not found")
  }

  tryCatch(
    {
      # Determine separator
      sep <- switch(config$input$separator,
                    "tab" = "\t",
                    "comma" = ",",
                    "space" = " ",
                    "\t")

      # Load data
      if (grepl("\\.gz$", input_file)) {
        data <- read.table(gzfile(input_file),
                           header = config$input$header,
                           row.names = if (config$input$row_names) 1 else NULL,
                           sep = sep,
                           check.names = FALSE)
      } else if (grepl("\\.rds$", input_file)) {
        data <- readRDS(input_file)
      } else {
        data <- read.table(input_file,
                           header = config$input$header,
                           row.names = if (config$input$row_names) 1 else NULL,
                           sep = sep,
                           check.names = FALSE)
      }

      log_info("Data loaded successfully")
      log_info("Dimensions: {nrow(data)} genes x {ncol(data)} cells")

      return(data)
    },
    error = function(e) {
      log_error("Failed to load data: {conditionMessage(e)}")
      stop(e)
    }
  )
}


#' Validate loaded data
validate_data <- function(data) {
  log_info("")
  log_info("STEP 2: Data Validation")
  log_info("-" |> rep(80) |> paste(collapse = ""))

  validation <- validate_expression_matrix(data)

  if (!validation$valid) {
    log_error("Data validation failed:")
    for (err in validation$errors) {
      log_error("  - {err}")
    }
    stop("Data validation failed")
  }

  if (length(validation$warnings) > 0) {
    log_warn("Data validation warnings:")
    for (warn in validation$warnings) {
      log_warn("  - {warn}")
    }
  }

  log_info("Data validation: PASSED")
  log_info("  Genes: {validation$metrics$n_genes}")
  log_info("  Cells: {validation$metrics$n_cells}")
  log_info("  Sparsity: {round(validation$metrics$sparsity * 100, 2)}%")

  return(validation)
}


# =============================================================================
# Quality Control and Preprocessing
# =============================================================================

#' Run quality control assessment
run_qc <- function(data, config, output_dir) {
  log_info("")
  log_info("STEP 3: Quality Control")
  log_info("-" |> rep(80) |> paste(collapse = ""))

  quality <- assess_data_quality(data)

  log_info("Quality Metrics:")
  log_info("  Median genes/cell: {round(quality$genes_per_cell_median, 0)}")
  log_info("  Median UMI/cell: {round(quality$umi_per_cell_median, 0)}")
  log_info("  Median cells/gene: {round(quality$cells_per_gene_median, 0)}")

  if (!is.na(quality$mt_percent_median)) {
    log_info("  Median MT%: {round(quality$mt_percent_median, 2)}%")
  }
  log_info("  Data sparsity: {round(quality$sparsity * 100, 2)}%")

  # Plot QC metrics
  if (config$quality_control$plot_qc) {
    qc_plot_file <- file.path(output_dir, "plots", "qc_metrics.pdf")
    log_info("Generating QC plots: {qc_plot_file}")
    plot_qc_metrics(data, qc_plot_file)
  }

  return(quality)
}


#' Preprocess data
preprocess_data <- function(data, config) {
  log_info("")
  log_info("STEP 4: Data Preprocessing")
  log_info("-" |> rep(80) |> paste(collapse = ""))

  processed_data <- data

  # Detect log transformation
  if (config$preprocessing$detect_log_transform) {
    log_detection <- detect_log_transform(data)
    log_info("Log-transform detection: {log_detection$method}")
    log_info("  Is log-transformed: {log_detection$is_log_transformed}")
    log_info("  Confidence: {log_detection$confidence}")

    if (log_detection$is_log_transformed && config$preprocessing$convert_to_counts) {
      log_info("Converting log-transformed data to counts...")
      processed_data <- convert_log_to_counts(data, config$preprocessing$log_base)
      log_info("Conversion complete")
    }
  }

  # Filter cells
  if (config$quality_control$auto_filter) {
    log_info("Filtering low-quality cells...")
    cell_filter <- filter_cells(
      processed_data,
      min_genes = config$quality_control$min_genes_per_cell,
      min_umi = config$quality_control$min_umi_per_cell,
      max_mt_percent = config$quality_control$max_mt_percent
    )

    log_info("  Removed: {cell_filter$n_removed} cells")
    log_info("  Kept: {cell_filter$n_kept} cells")

    processed_data <- cell_filter$data

    # Filter genes
    log_info("Filtering low-abundance genes...")
    gene_filter <- filter_genes(
      processed_data,
      min_cells = config$quality_control$min_cells_per_gene
    )

    log_info("  Removed: {gene_filter$n_removed} genes")
    log_info("  Kept: {gene_filter$n_kept} genes")

    processed_data <- gene_filter$data
  }

  log_info("Preprocessing complete")
  log_info("Final dimensions: {nrow(processed_data)} genes x {ncol(processed_data)} cells")

  return(processed_data)
}


# =============================================================================
# CopyKAT Analysis
# =============================================================================

#' Run CopyKAT analysis
run_analysis <- function(data, config, output_dir) {
  log_info("")
  log_info("STEP 5: CopyKAT Analysis")
  log_info("-" |> rep(80) |> paste(collapse = ""))

  # Change to output directory for CopyKAT outputs
  original_wd <- getwd()
  setwd(output_dir)

  # Prepare parameters
  params <- list(
    id.type = config$copykat$id_type,
    cell.line = config$copykat$cell_line,
    ngene.chr = config$copykat$ngene_chr,
    LOW.DR = config$copykat$LOW_DR,
    UP.DR = config$copykat$UP_DR,
    win.size = config$copykat$win_size,
    KS.cut = config$copykat$KS_cut,
    sam.name = config$output$sample_name,
    distance = config$copykat$distance,
    genome = config$copykat$genome,
    n.cores = config$copykat$n_cores,
    plot.genes = config$copykat$plot_genes
  )

  # Load normal cell names if provided
  if (config$copykat$norm_cell_names != "") {
    if (file.exists(config$copykat$norm_cell_names)) {
      params$norm.cell.names <- readLines(config$copykat$norm_cell_names)
      log_info("Loaded {length(params$norm.cell.names)} known normal cell names")
    }
  }

  log_info("CopyKAT Parameters:")
  for (name in names(params)) {
    if (name != "norm.cell.names") {
      log_info("  {name}: {params[[name]]}")
    }
  }

  # Run CopyKAT
  start_time <- Sys.time()
  log_info("Starting CopyKAT analysis...")

  result <- tryCatch(
    {
      copykat_result <- do.call(copykat, c(list(rawmat = data), params))
      log_info("CopyKAT analysis completed successfully")
      list(success = TRUE, result = copykat_result, error = NULL)
    },
    error = function(e) {
      log_error("CopyKAT analysis failed: {conditionMessage(e)}")
      list(success = FALSE, result = NULL, error = conditionMessage(e))
    },
    warning = function(w) {
      log_warn("CopyKAT warning: {conditionMessage(w)}")
      copykat_result <- suppressWarnings(do.call(copykat, c(list(rawmat = data), params)))
      list(success = TRUE, result = copykat_result, error = NULL)
    }
  )

  end_time <- Sys.time()
  runtime <- difftime(end_time, start_time, units = "mins")
  log_info("Runtime: {round(runtime, 2)} minutes")

  # Return to original directory
  setwd(original_wd)

  if (!result$success) {
    if (config$logging$continue_on_error) {
      log_warn("Continuing despite error")
      return(NULL)
    } else {
      stop("CopyKAT analysis failed")
    }
  }

  return(result$result)
}


# =============================================================================
# Results Processing and Visualization
# =============================================================================

#' Process and summarize results
process_results <- function(result, config, output_dir) {
  if (is.null(result)) {
    log_warn("No results to process (analysis failed)")
    return(NULL)
  }

  log_info("")
  log_info("STEP 6: Processing Results")
  log_info("-" |> rep(80) |> paste(collapse = ""))

  predictions <- result$prediction

  # Summary statistics
  class_table <- table(predictions$copykat.pred)
  log_info("Cell Classifications:")
  for (class_name in names(class_table)) {
    count <- class_table[class_name]
    pct <- round(count / nrow(predictions) * 100, 2)
    log_info("  {class_name}: {count} cells ({pct}%)")
  }

  # Confidence scores (with error handling for not.defined cases)
  log_info("Confidence Scores:")
  tryCatch(
    {
      conf_by_class <- tapply(predictions$copykat.confidence,
                              predictions$copykat.pred,
                              function(x) mean(x, na.rm = TRUE))
      for (class_name in names(conf_by_class)) {
        if (!is.na(conf_by_class[class_name])) {
          log_info("  {class_name}: {round(conf_by_class[class_name], 3)}")
        } else {
          log_info("  {class_name}: NA (no confidence scores)")
        }
      }
    },
    error = function(e) {
      log_warn("Could not calculate confidence scores: {conditionMessage(e)}")
    }
  )

  # Generate summary plots
  if (config$advanced$extra_plots) {
    log_info("Generating summary plots...")
    tryCatch(
      {
        summary_plot_file <- file.path(output_dir, "plots", "copykat_summary.pdf")
        plot_copykat_summary(result, summary_plot_file)
        log_info("Summary plots saved: {summary_plot_file}")
      },
      error = function(e) {
        log_warn("Could not generate summary plots: {conditionMessage(e)}")
      }
    )
  }

  # Chromosome-level summary
  if (config$advanced$chr_summary) {
    log_info("Generating chromosome-level summary...")
    tryCatch(
      {
        chr_summary <- create_chr_summary(result, output_dir)
      },
      error = function(e) {
        log_warn("Could not generate chromosome summary: {conditionMessage(e)}")
      }
    )
  }

  # Export to CSV
  if (config$advanced$export_csv) {
    log_info("Exporting results to CSV...")
    tryCatch(
      {
        export_results_csv(result, output_dir, config$output$sample_name)
      },
      error = function(e) {
        log_warn("Could not export CSV files: {conditionMessage(e)}")
      }
    )
  }

  return(predictions)
}


#' Create chromosome-level summary
create_chr_summary <- function(result, output_dir) {
  tryCatch(
    {
      cnv_file <- file.path(output_dir,
                            paste0(basename(output_dir), "_copykat_CNA_results.txt"))

      if (!file.exists(cnv_file)) {
        # Try without timestamp
        files <- list.files(output_dir, pattern = "_copykat_CNA_results.txt$", full.names = TRUE)
        if (length(files) > 0) {
          cnv_file <- files[1]
        } else {
          log_warn("CNV results file not found")
          return(NULL)
        }
      }

      cnv_data <- read.table(cnv_file, header = TRUE, row.names = 1)
      chromosomes <- cnv_data$chrom

      predictions <- result$prediction
      aneuploid_cells <- predictions$cell.names[predictions$copykat.pred == "aneuploid"]

      if (length(aneuploid_cells) == 0) {
        log_warn("No aneuploid cells found")
        return(NULL)
      }

      cnv_matrix <- result$CNV.matrix
      aneuploid_cnv <- cnv_matrix[, aneuploid_cells, drop = FALSE]

      mean_cn_per_bin <- rowMeans(aneuploid_cnv)
      chr_means <- tapply(mean_cn_per_bin, chromosomes, mean)

      chr_summary <- data.frame(
        Chromosome = names(chr_means),
        Mean_CN = chr_means,
        Status = ifelse(chr_means > 2.3, "Amplified",
                        ifelse(chr_means < 1.7, "Deleted", "Normal")),
        row.names = NULL
      )

      output_file <- file.path(output_dir, "chromosome_summary.csv")
      write.csv(chr_summary, output_file, row.names = FALSE)
      log_info("Chromosome summary saved: {output_file}")

      return(chr_summary)
    },
    error = function(e) {
      log_warn("Failed to create chromosome summary: {conditionMessage(e)}")
      return(NULL)
    }
  )
}


#' Export results to CSV files
export_results_csv <- function(result, output_dir, sample_name) {
  # Export predictions
  pred_file <- file.path(output_dir, paste0(sample_name, "_predictions.csv"))
  write.csv(result$prediction, pred_file, row.names = FALSE)
  log_info("Predictions exported: {pred_file}")

  # Export CNV matrix
  cnv_file <- file.path(output_dir, paste0(sample_name, "_cnv_matrix.csv"))
  write.csv(result$CNV.matrix, cnv_file)
  log_info("CNV matrix exported: {cnv_file}")
}


# =============================================================================
# Report Generation
# =============================================================================

#' Generate HTML report
generate_report <- function(config, output_dir, data, result, quality, validation) {
  if (!config$advanced$generate_report) {
    log_info("Report generation disabled")
    return(NULL)
  }

  log_info("")
  log_info("STEP 7: Generating HTML Report")
  log_info("-" |> rep(80) |> paste(collapse = ""))

  template <- config$advanced$report_template

  if (!file.exists(template)) {
    log_warn("Report template not found: {template}")
    log_warn("Skipping report generation")
    return(NULL)
  }

  tryCatch(
    {
      # Check if rmarkdown is available
      if (!requireNamespace("rmarkdown", quietly = TRUE)) {
        log_warn("rmarkdown package not installed. Skipping report generation.")
        return(NULL)
      }

      report_params <- list(
        sample_name = config$output$sample_name,
        output_dir = output_dir,
        data = data,
        result = result,
        quality = quality,
        validation = validation,
        config = config
      )

      output_file <- file.path(output_dir, paste0(config$output$sample_name, "_report.html"))

      log_info("Rendering report...")
      rmarkdown::render(
        template,
        params = report_params,
        output_file = output_file,
        quiet = TRUE
      )

      log_info("Report generated: {output_file}")
      return(output_file)
    },
    error = function(e) {
      log_warn("Report generation failed: {conditionMessage(e)}")
      return(NULL)
    }
  )
}


# =============================================================================
# Main Pipeline
# =============================================================================

main <- function() {
  # Parse arguments
  args <- parse_args()

  # Load configuration
  if (args$mode == "config") {
    config <- load_config(args$config_file)
  } else {
    # Build config from CLI args
    config <- load_config("config/analysis_config.yaml")  # Use as base
    if (!is.null(args$input_file)) config$input$file <- args$input_file
    if (!is.null(args$output_dir)) config$output$directory <- args$output_dir
    if (!is.null(args$sample_name)) config$output$sample_name <- args$sample_name
    if (!is.null(args$genome)) config$copykat$genome <- args$genome
    if (!is.null(args$n_cores)) config$copykat$n_cores <- args$n_cores
  }

  # Setup output and logging
  output_dir <- setup_output(config)

  # Pipeline execution with error handling
  tryCatch(
    {
      # 1. Load data
      data <- load_data(config)

      # 2. Validate data
      validation <- validate_data(data)

      # 3. Quality control
      quality <- run_qc(data, config, output_dir)

      # 4. Preprocess data
      processed_data <- preprocess_data(data, config)

      # 5. Run CopyKAT
      result <- run_analysis(processed_data, config, output_dir)

      # 6. Process results
      predictions <- process_results(result, config, output_dir)

      # 7. Generate report
      report_file <- generate_report(config, output_dir, processed_data, result,
                                      quality, validation)

      # Final summary
      log_info("")
      log_info(paste(rep("=", 80), collapse = ""))
      log_info("ANALYSIS COMPLETE")
      log_info(paste(rep("=", 80), collapse = ""))
      log_info("Output directory: {output_dir}")
      log_info("End time: {Sys.time()}")
      log_info("")

      if (!is.null(result)) {
        log_info("SUCCESS: Analysis completed successfully")
      } else {
        log_warn("PARTIAL SUCCESS: Analysis completed with warnings")
      }

      return(invisible(0))
    },
    error = function(e) {
      log_error(paste(rep("=", 80), collapse = ""))
      log_error("ANALYSIS FAILED")
      log_error(paste(rep("=", 80), collapse = ""))
      log_error("Error: {conditionMessage(e)}")
      log_error("Traceback:")
      log_error(paste(capture.output(traceback()), collapse = "\n"))
      log_error("")
      return(invisible(1))
    }
  )
}

# Run main function if executed as script
if (!interactive()) {
  exit_code <- main()
  quit(save = "no", status = exit_code)
}
