# CopyKAT Troubleshooting Guide

## Table of Contents
1. [Data Quality Issues](#data-quality-issues)
2. [Parameter Tuning Problems](#parameter-tuning-problems)
3. [Convergence Warnings](#convergence-warnings)
4. [Memory and Performance Issues](#memory-and-performance-issues)
5. [Interpretation Issues](#interpretation-issues)
6. [Installation and Environment Problems](#installation-and-environment-problems)
7. [Common Error Messages](#common-error-messages)

---

## Data Quality Issues

### Issue: "WARNING: low data quality; assigned LOW.DR to UP.DR..."

**Symptoms**:
- Warning message during step 1
- CopyKAT automatically sets UP.DR = LOW.DR
- Analysis continues but may be unreliable

**Root Cause**:
- Too few genes pass the UP.DR detection rate threshold
- Data is very sparse (many zeros)
- Low sequencing depth

**Solutions**:

**Option 1: Decrease Detection Rate Thresholds**
```r
copykat(rawmat = data,
        LOW.DR = 0.02,  # Decrease from 0.05
        UP.DR = 0.02,   # Set equal to LOW.DR
        ...)
```

**Option 2: Increase Window Size**
```r
copykat(rawmat = data,
        LOW.DR = 0.03,
        UP.DR = 0.03,
        win.size = 50,  # Increase from 25
        ...)
```

**Option 3: Filter Data First**
```r
# Remove very sparse genes
gene_detection <- rowSums(rawmat > 0) / ncol(rawmat)
filtered_data <- rawmat[gene_detection > 0.01, ]

copykat(rawmat = filtered_data, ...)
```

**Prevention**:
- Ensure >2000 UMI per cell median
- Use appropriate sequencing depth for your questions
- Consider pooling technical replicates

---

### Issue: All Cells Filtered Out

**Symptoms**:
```
Error: No cells remain after filtering
```

**Root Cause**:
- `ngene.chr` threshold too strict
- Very poor quality data
- Cells don't have enough genes on each chromosome

**Solutions**:

**Step 1: Check gene detection**
```r
# How many genes per chromosome per cell?
genes_per_chr <- apply(rawmat > 0, 2, function(cell) {
  tapply(cell, gene_chromosome, sum)
})

summary(genes_per_chr)
```

**Step 2: Decrease ngene.chr**
```r
copykat(rawmat = data,
        ngene.chr = 1,  # Very permissive
        ...)
```

**Step 3: Check for systematic issues**
```r
# Cell quality metrics
colSums(rawmat > 0)  # Genes per cell
colSums(rawmat)      # UMI per cell

# If most cells have <500 genes, data quality is too low
```

---

### Issue: High Mitochondrial Content

**Symptoms**:
- Many cells with >20% mitochondrial reads
- Poor CNV detection
- Noisy results

**Root Cause**:
- Stressed or dying cells
- Poor sample handling
- Apoptotic cells

**Solutions**:

**Filter high-MT cells before CopyKAT**:
```r
# Calculate MT percentage
mt_genes <- grep("^MT-", rownames(rawmat), value = TRUE)
mt_pct <- colSums(rawmat[mt_genes, ]) / colSums(rawmat)

# Keep cells with <20% MT
keep_cells <- mt_pct < 0.2
filtered_data <- rawmat[, keep_cells]

copykat(rawmat = filtered_data, ...)
```

---

## Parameter Tuning Problems

### Issue: No Aneuploid Cells Detected

**Symptoms**:
- All cells classified as diploid
- No CNVs detected
- You know sample contains tumor cells

**Root Causes**:
1. Sample is actually all normal cells
2. Parameters too stringent
3. Tumor cells have subtle CNVs

**Solutions**:

**Step 1: Verify sample composition**
```r
# Check for known cancer markers
cancer_markers <- c("EGFR", "MYC", "CCND1")
marker_expr <- rawmat[cancer_markers, ]

# High expression suggests tumor cells present
```

**Step 2: Increase sensitivity**
```r
copykat(rawmat = data,
        KS.cut = 0.05,  # Decrease from 0.1 (more sensitive)
        win.size = 15,  # Decrease from 25 (higher resolution)
        ...)
```

**Step 3: Check if cell line sample**
```r
# If pure cancer cell line, use:
copykat(rawmat = data,
        cell.line = "yes",  # Skip diploid detection
        ...)
```

**Step 4: Manual inspection**
```r
# Look at raw CNV matrix
cnv_data <- result$CNV.matrix

# Check for any regions with deviation
rowMeans(cnv_data)  # Should see values != 2 if CNVs present
```

---

### Issue: Too Many Breakpoints (Noisy Profile)

**Symptoms**:
- CNV heatmap looks very fragmented
- Many small segments
- Unrealistic karyotype

**Root Cause**:
- KS.cut too low (over-segmentation)
- win.size too small
- Noisy data

**Solutions**:

**Increase KS.cut**:
```r
copykat(rawmat = data,
        KS.cut = 0.2,  # Increase from 0.1
        ...)
```

**Increase window size**:
```r
copykat(rawmat = data,
        win.size = 50,  # Increase from 25
        KS.cut = 0.15,
        ...)
```

**Example comparison**:
```r
# Too sensitive (noisy)
KS.cut = 0.05, win.size = 10

# Balanced
KS.cut = 0.1, win.size = 25

# Smooth
KS.cut = 0.2, win.size = 50
```

---

### Issue: Poor Tumor/Normal Separation

**Symptoms**:
- Diploid cluster contains obvious tumor cells
- Aneuploid cluster contains obvious normal cells
- Low confidence scores

**Root Cause**:
- Baseline detection failed
- Mixed sample with few normal cells
- Batch effects

**Solutions**:

**Option 1: Provide known normal cells**
```r
# Identify immune cells by markers
cd45_cells <- colnames(data)[data["PTPRC", ] > 5]  # PTPRC = CD45

copykat(rawmat = data,
        norm.cell.names = cd45_cells,
        ...)
```

**Option 2: Use correlation distance**
```r
copykat(rawmat = data,
        distance = "pearson",  # Instead of euclidean
        ...)
```

**Option 3: Batch correction first**
```r
# If batch effects present
library(sva)
batch_corrected <- ComBat(rawmat, batch = batch_ids)

copykat(rawmat = batch_corrected, ...)
```

---

## Convergence Warnings

### Issue: "WARNING! NOT CONVERGENT!"

**Symptoms**:
```
[1] "cell: 1"
WARNING! NOT CONVERGENT!
number of iterations= 500
```

**What it means**:
- GMM fitting didn't converge for that cell
- Maximum iterations (500) reached
- Cell may have unusual CNV pattern

**Is it serious?**
- **Few cells (<10%)**: Usually fine, continue
- **Many cells (>50%)**: Data quality issue

**Solutions**:

**If few cells affected**:
- Ignore warnings, check final results
- These cells may be borderline cases

**If many cells affected**:
```r
# Reduce complexity
copykat(rawmat = data,
        win.size = 50,  # Larger windows
        LOW.DR = 0.02,  # Lower thresholds
        UP.DR = 0.02,
        ...)
```

---

### Issue: "low confidence in classification"

**Symptoms**:
```
[1] "low confidence in classification"
```

**Root Cause**:
- Unclear separation between diploid and aneuploid clusters
- Too few cells
- Subtle CNVs

**Solutions**:

**Check cluster separation**:
```r
# Visualize clustering
hclust_result <- result$hclustering
plot(hclust_result)

# If clusters not well separated, results uncertain
```

**Increase sample size**:
- Need >100 cells for reliable classification
- Pool biological replicates if possible

**Manual review**:
```r
# Check CNV profiles of "low confidence" cells
low_conf <- result$prediction[result$prediction$copykat.confidence < 0.7, ]

# Inspect their CNV patterns manually
```

---

## Memory and Performance Issues

### Issue: R Session Crashes / "Cannot allocate vector"

**Symptoms**:
```
Error: cannot allocate vector of size X GB
```

**Root Cause**:
- Insufficient RAM
- Large dataset (>5000 cells)
- Distance matrix too large

**Solutions**:

**Option 1: Reduce dataset size**
```r
# Subsample cells
set.seed(123)
sample_cells <- sample(colnames(rawmat), 2000)
subset_data <- rawmat[, sample_cells]

copykat(rawmat = subset_data, ...)
```

**Option 2: Use fewer cores**
```r
# Paradoxically, fewer cores may use less memory
copykat(rawmat = data,
        n.cores = 1,  # Instead of 8
        ...)
```

**Option 3: Increase swap/virtual memory**
- macOS: Automatic
- Linux: Create swap file
- Windows: Increase page file

**Option 4: Run on high-memory machine**
- Cloud instance (AWS, GCP)
- HPC cluster
- Workstation with 32-64GB RAM

**Prevention**:
- For >10,000 cells, use machine with ≥32GB RAM
- Close other applications
- Use `gc()` between analyses to free memory

---

### Issue: Analysis is Very Slow

**Symptoms**:
- Takes >2 hours for 1000 cells
- CPU at 100% for extended periods

**Solutions**:

**Increase cores**:
```r
copykat(rawmat = data,
        n.cores = 8,  # Use more cores
        ...)
```

**Disable gene labels**:
```r
copykat(rawmat = data,
        plot.genes = "FALSE",  # Speeds up plotting
        ...)
```

**Reduce resolution**:
```r
copykat(rawmat = data,
        win.size = 50,  # Fewer windows = faster
        ...)
```

**Expected runtimes** (varies by system):
| Cells | Genes | Cores | Time |
|-------|-------|-------|------|
| 500 | 10k | 4 | 5-10 min |
| 2000 | 15k | 4 | 20-40 min |
| 5000 | 20k | 8 | 1-2 hrs |
| 10000 | 20k | 16 | 3-6 hrs |

---

## Interpretation Issues

### Issue: Unexpected Cell Classifications

**Symptoms**:
- Known immune cells classified as aneuploid
- Known tumor cells classified as diploid

**Root Cause**:
- False positives/negatives
- Unusual biology
- Technical artifacts

**Diagnostic steps**:

**Step 1: Check marker genes**
```r
# Immune markers
immune_cells <- result$prediction$cell.names[result$prediction$copykat.pred == "diploid"]
immune_markers <- c("PTPRC", "CD3D", "CD8A")  # T cell markers

# Should be high if truly immune cells
rawmat[immune_markers, immune_cells]
```

**Step 2: Visualize CNV profiles**
```r
# For suspicious cells
suspicious_cell <- "Cell_123"
cnv_profile <- result$CNV.matrix[, suspicious_cell]

plot(cnv_profile, type="l", main=suspicious_cell)
abline(h=2, col="red", lty=2)  # Diploid baseline

# If flat around 2 → diploid
# If varies → aneuploid
```

**Step 3: Cross-validate**
```r
# Run with different parameters
result1 <- copykat(..., KS.cut=0.05)
result2 <- copykat(..., KS.cut=0.15)

# Check if classifications agree
table(result1$prediction$copykat.pred,
      result2$prediction$copykat.pred)
```

---

### Issue: Cannot Distinguish Tumor Subclones

**Symptoms**:
- All aneuploid cells in one cluster
- Expected multiple subclones
- Very similar CNV patterns

**Root Cause**:
- Tumor is clonal (actually one clone)
- Subclones differ by point mutations, not CNVs
- Resolution too low

**Solutions**:

**Increase resolution**:
```r
copykat(rawmat = data,
        win.size = 15,  # Smaller windows
        KS.cut = 0.05,  # More sensitive
        ...)
```

**Manual hierarchical clustering**:
```r
# Use CNV matrix for clustering
library(pheatmap)

pheatmap(result$CNV.matrix,
         clustering_distance_rows = "euclidean",
         cutree_rows = 3)  # Force 3 clusters
```

**Alternative: Use gene expression**
```r
# Subclones may differ in expression, not just CNV
library(Seurat)
# Standard clustering on expression data
```

---

## Installation and Environment Problems

### Issue: CopyKAT Package Not Found

**Symptoms**:
```
Error: package 'copykat' not found
```

**Solutions**:

**Install from GitHub**:
```r
install.packages("remotes")
remotes::install_github("navinlabcode/copykat")
```

**Check installation**:
```r
library(copykat)
packageVersion("copykat")
```

**If fails with dependency errors**:
```r
# Install dependencies first
install.packages(c("Rcpp", "mixtools", "MCMCpack"))

# Then retry CopyKAT
remotes::install_github("navinlabcode/copykat")
```

---

### Issue: Conda Environment Issues

**Symptoms**:
```
conda: command not found
Error loading copykat in conda environment
```

**Solutions**:

**Activate environment properly**:
```bash
# macOS/Linux
source ~/anaconda3/bin/activate Project4-CNV-Cancer-RNAseq

# Or if using full path
/Users/hansonwen/anaconda3/bin/conda activate Project4-CNV-Cancer-RNAseq
```

**Reinstall in environment**:
```bash
conda activate Project4-CNV-Cancer-RNAseq
R -e 'remotes::install_github("navinlabcode/copykat")'
```

---

## Common Error Messages

### "Error in read.table: no lines available in input"

**Cause**: Input file is empty or corrupted

**Solution**:
```r
# Check file
file.info("input.txt")  # Should show size > 0

# Try reading first few lines
readLines("input.txt", n=5)
```

---

### "subscript out of bounds"

**Cause**: Gene or cell name mismatch

**Solution**:
```r
# Check dimensions
dim(rawmat)

# Check for NAs
any(is.na(rawmat))

# Check rownames/colnames exist
length(rownames(rawmat))
length(colnames(rawmat))
```

---

### "arguments imply differing number of rows"

**Cause**: Metadata doesn't match expression matrix

**Solution**:
```r
# Ensure dimensions match
nrow(metadata) == ncol(rawmat)  # Should be TRUE

# Check cell names match
all(rownames(metadata) %in% colnames(rawmat))
```

---

## Diagnostic Workflow

When encountering issues, follow this systematic approach:

```
1. Check data quality
   ├─ Dimensions (>50 cells, >1000 genes)
   ├─ No NAs or negative values
   └─ Reasonable expression range

2. Verify parameters
   ├─ genome matches species
   ├─ id.type matches gene names
   └─ cell.line appropriate for sample

3. Start with defaults
   └─ Only adjust if warnings/errors

4. Adjust incrementally
   ├─ Change one parameter at a time
   └─ Document what works

5. Validate results
   ├─ Check known cell types
   ├─ Visualize CNV profiles
   └─ Cross-validate with markers
```

---

## Getting Help

**If still stuck**:

1. **Check GitHub Issues**: https://github.com/navinlabcode/copykat/issues
2. **Review Documentation**: [01_COPYKAT_OVERVIEW.md](01_COPYKAT_OVERVIEW.md)
3. **Example Datasets**: Use test data first to verify installation
4. **Post Issue**: Include:
   - Data dimensions
   - Parameters used
   - Full error message
   - sessionInfo()

---

**See Also**:
- [03_PARAMETERS_REFERENCE.md](03_PARAMETERS_REFERENCE.md) - Parameter details
- [10_PARAMETER_QUICK_REFERENCE.md](10_PARAMETER_QUICK_REFERENCE.md) - Quick fixes
- [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md) - Understanding how it works
