# CopyKAT Parameters Reference Guide

## Table of Contents
1. [Parameter Overview](#parameter-overview)
2. [rawmat - Input Expression Matrix](#rawmat---input-expression-matrix)
3. [id.type - Gene ID Type](#idtype---gene-id-type)
4. [cell.line - Sample Type](#cellline---sample-type)
5. [ngene.chr - Gene Per Chromosome Filter](#ngenechr---gene-per-chromosome-filter)
6. [LOW.DR - Low Detection Rate Threshold](#lowdr---low-detection-rate-threshold)
7. [UP.DR - Upper Detection Rate Threshold](#updr---upper-detection-rate-threshold)
8. [win.size - Segmentation Window Size](#winsize---segmentation-window-size)
9. [norm.cell.names - Known Normal Cells](#normcellnames---known-normal-cells)
10. [KS.cut - Segmentation Threshold](#kscut---segmentation-threshold)
11. [sam.name - Sample Name](#samname---sample-name)
12. [distance - Distance Metric](#distance---distance-metric)
13. [output.seg - SEG File Output](#outputseg---seg-file-output)
14. [plot.genes - Gene Labels in Heatmap](#plotgenes---gene-labels-in-heatmap)
15. [genome - Reference Genome](#genome---reference-genome)
16. [n.cores - CPU Cores](#ncores---cpu-cores)

---

## Parameter Overview

### Complete Function Signature

```r
copykat(
  rawmat = rawdata,
  id.type = "S",
  cell.line = "no",
  ngene.chr = 5,
  LOW.DR = 0.05,
  UP.DR = 0.1,
  win.size = 25,
  norm.cell.names = "",
  KS.cut = 0.1,
  sam.name = "",
  distance = "euclidean",
  output.seg = "FALSE",
  plot.genes = "TRUE",
  genome = "hg20",
  n.cores = 1
)
```

### Parameter Categories

| Category | Parameters |
|----------|------------|
| **Input Data** | `rawmat`, `id.type`, `norm.cell.names` |
| **Quality Filtering** | `ngene.chr`, `LOW.DR`, `UP.DR` |
| **Algorithm Tuning** | `win.size`, `KS.cut`, `distance` |
| **Sample Properties** | `cell.line`, `genome` |
| **Output Control** | `sam.name`, `output.seg`, `plot.genes` |
| **Performance** | `n.cores` |

---

## rawmat - Input Expression Matrix

### What It Is

The gene expression matrix containing your single-cell RNA-seq data.

### Format Requirements

**Structure**:
```
              Cell_1   Cell_2   Cell_3   ...   Cell_N
Gene_1        23       45       12             67
Gene_2        11       33       8              42
Gene_3        67       12       45             23
...
Gene_M        34       56       23             89
```

**Requirements**:
- **Rows**: Genes (with gene names as row names)
- **Columns**: Cells (with cell IDs as column names)
- **Values**: Expression counts (UMI counts, TPM, or CPM)
- **Type**: R data frame or matrix

### Data Types Accepted

| Data Type | Recommended | Notes |
|-----------|-------------|-------|
| Raw UMI counts | ✓ Best | Directly from 10x, Drop-seq, etc. |
| TPM (Transcripts Per Million) | ✓ Good | Normalized counts |
| CPM (Counts Per Million) | ✓ Good | Normalized counts |
| RPKM/FPKM | ✓ Acceptable | Length-normalized |
| Log-transformed | ✗ Avoid | CopyKAT performs own transformation |
| Scaled/Z-score | ✗ Do not use | Breaks CNV inference |

### Loading Your Data

**From text file**:
```r
rawmat <- read.table("expression_matrix.txt",
                     header = TRUE,
                     row.names = 1,
                     sep = "\t",
                     check.names = FALSE)
```

**From compressed file**:
```r
rawmat <- read.table(gzfile("expression_matrix.txt.gz"),
                     header = TRUE,
                     row.names = 1,
                     sep = "\t",
                     check.names = FALSE)
```

**From CSV**:
```r
rawmat <- read.csv("expression_matrix.csv",
                   row.names = 1,
                   check.names = FALSE)
```

**From Seurat object**:
```r
library(Seurat)
rawmat <- GetAssayData(seurat_object, slot = "counts")
```

**From SingleCellExperiment**:
```r
library(SingleCellExperiment)
rawmat <- counts(sce_object)
```

### Common Issues

**Issue 1: Transposed matrix**
```r
# Check dimensions
dim(rawmat)  # Should be genes × cells, not cells × genes

# If transposed:
rawmat <- t(rawmat)
```

**Issue 2: Missing row/column names**
```r
# Check names
head(rownames(rawmat))  # Should be gene names
head(colnames(rawmat))  # Should be cell IDs

# If missing, add them:
rownames(rawmat) <- gene_names
colnames(rawmat) <- cell_ids
```

**Issue 3: Negative values**
```r
# CopyKAT expects non-negative values
# If you have log-transformed data with negative values:
# Convert back: rawmat <- 2^rawmat - 1
# Or use original counts
```

### Size Recommendations

| Dataset Size | Cells | Genes | Memory | Runtime |
|--------------|-------|-------|--------|---------|
| Small | 100-500 | 5k-15k | 2-4 GB | 5-15 min |
| Medium | 500-2000 | 10k-20k | 4-8 GB | 15-45 min |
| Large | 2000-10000 | 15k-25k | 8-16 GB | 1-3 hrs |
| Very Large | >10000 | 20k-30k | 16-64 GB | 3-8 hrs |

### Streamlit UI Recommendation

```python
import streamlit as st

uploaded_file = st.file_uploader(
    "Upload Expression Matrix",
    type=["txt", "csv", "tsv", "gz"],
    help="Gene × Cell matrix. Genes in rows, cells in columns."
)

# Display preview
if uploaded_file:
    preview = pd.read_csv(uploaded_file, nrows=5, index_col=0)
    st.write(f"**Preview**: {preview.shape[0]} genes × {preview.shape[1]} cells")
    st.dataframe(preview)
```

---

## id.type - Gene ID Type

### What It Is

Specifies whether gene names are **Symbols** (e.g., EGFR, TP53) or **Ensembl IDs** (e.g., ENSG00000146648).

### Options

| Value | Meaning | Example Gene Names |
|-------|---------|-------------------|
| `"S"` | Symbol (default) | EGFR, TP53, MYC, PTEN |
| `"E"` | Ensembl | ENSG00000146648, ENSG00000141510 |

### Why It Matters

CopyKAT needs to map genes to chromosomal coordinates. Gene ID type determines which annotation database to use.

### How to Check Your Data

```r
# Look at gene names
head(rownames(rawmat))

# If you see:
# "EGFR", "TP53", "MYC"  → Use id.type="S"
# "ENSG00000146648", ... → Use id.type="E"
```

### Mixed IDs

If you have mixed IDs (some symbols, some Ensembl):

```r
# Convert all to symbols using biomaRt
library(biomaRt)
mart <- useMart("ensembl", dataset="hsapiens_gene_ensembl")

# Get conversions
conversions <- getBM(attributes=c("ensembl_gene_id", "hgnc_symbol"),
                     filters="ensembl_gene_id",
                     values=rownames(rawmat),
                     mart=mart)

# Replace Ensembl IDs with symbols
rownames(rawmat) <- conversions$hgnc_symbol[match(rownames(rawmat),
                                                   conversions$ensembl_gene_id)]
```

### CLI Examples

```r
# Using symbols (most common)
copykat(rawmat = data, id.type = "S", ...)

# Using Ensembl IDs
copykat(rawmat = data, id.type = "E", ...)
```

### Streamlit UI Recommendation

```python
id_type = st.selectbox(
    "Gene ID Type",
    options=["S", "E"],
    format_func=lambda x: "Symbol (EGFR, TP53, ...)" if x == "S"
                          else "Ensembl (ENSG00000146648, ...)",
    index=0,  # Default to Symbol
    help="Check your gene names. Most datasets use gene symbols."
)

# Auto-detection
gene_names = df.index.tolist()[:5]
if all(name.startswith("ENSG") for name in gene_names):
    st.info("Detected Ensembl IDs - setting id.type='E'")
    id_type = "E"
```

---

## cell.line - Sample Type

### What It Is

Indicates whether your data comes from a **pure cell line** or a **mixed tumor sample**.

### Options

| Value | Use When | Examples |
|-------|----------|----------|
| `"no"` (default) | Mixed sample with tumor + normal cells | Patient tumors, organoids |
| `"yes"` | Pure cancer cell line | HeLa, MCF7, U87, A375 |

### Why It Matters

**Pure cell lines (`"yes"`)**:
- All cells are aneuploid
- Skip diploid baseline detection
- Faster processing
- Uses first cell as reference

**Mixed samples (`"no"`)**:
- Contains tumor AND normal cells
- Performs diploid baseline detection
- Classifies each cell
- Full algorithm

### When to Use `"yes"`

```r
# Scenarios for cell.line="yes":
- Pure HeLa cell culture
- Immortalized cell line experiments
- Cells known to be 100% cancer

# In these cases, you want to:
# 1. Skip baseline detection (no normal cells to find)
# 2. Focus on CNV differences between cells
# 3. Identify subclones within the cell line
```

### When to Use `"no"`

```r
# Scenarios for cell.line="no":
- Patient tumor biopsies
- Tumor organoids (contain some normal cells)
- PDX models (mixed populations)
- Any sample where cell identity is unknown

# This enables:
# 1. Automatic tumor/normal separation
# 2. Diploid baseline detection
# 3. Cell classification
```

### CLI Examples

```r
# Mixed tumor sample (default)
copykat(rawmat = tumor_data, cell.line = "no", ...)

# Pure cell line
copykat(rawmat = hela_data, cell.line = "yes", ...)
```

### Common Mistake

```r
# WRONG: Using "yes" for patient tumors
copykat(rawmat = patient_gbm, cell.line = "yes", ...)
# Result: Poor baseline, incorrect CNVs

# CORRECT: Use "no" for patient samples
copykat(rawmat = patient_gbm, cell.line = "no", ...)
```

### Streamlit UI Recommendation

```python
cell_line = st.radio(
    "Sample Type",
    options=["no", "yes"],
    format_func=lambda x: "Mixed sample (tumor + normal cells)" if x == "no"
                          else "Pure cell line (all cancer cells)",
    index=0,  # Default to mixed
    help="""
    - Choose 'Mixed sample' for patient tumors, organoids, PDX models
    - Choose 'Pure cell line' only for established cell lines (HeLa, MCF7, etc.)
    """
)
```

---

## ngene.chr - Gene Per Chromosome Filter

### What It Is

Minimum number of genes that must be detected per chromosome for a cell to be included in the analysis.

### Default Value

`ngene.chr = 5`

### What It Does

**Filtering logic**:
```r
# For each cell
for (cell in cells) {
  genes_per_chr <- count_genes_per_chromosome(cell)

  if (any(genes_per_chr < ngene.chr)) {
    exclude_cell(cell)  # Too few genes on some chromosome
  }
}
```

**Example**:
```
Cell_A:
chr1: 150 genes ✓
chr2: 120 genes ✓
chr3: 4 genes   ✗ (< 5)
→ Cell_A excluded
```

### Why It Matters

**Chromosomes with too few genes**:
- Unreliable CNV inference
- Noisy estimates
- False positives/negatives

**This filter ensures**:
- Each chromosome has sufficient data
- CNV calls are based on multiple genes
- Quality control

### Tuning Guidelines

| Value | Effect | Use When |
|-------|--------|----------|
| 1-3 | Very permissive | Poor quality data, want to retain maximum cells |
| 5 (default) | Balanced | Standard datasets |
| 8-10 | Strict | High-quality data, prioritize accuracy |
| 15-20 | Very strict | Deeply sequenced data, eliminate any doubt |

### Impact on Cell Retention

**Example dataset: 1000 cells**

```r
ngene.chr = 1:  995 cells retained (99.5%)
ngene.chr = 5:  920 cells retained (92%)   ← Default
ngene.chr = 10: 850 cells retained (85%)
ngene.chr = 20: 650 cells retained (65%)
```

### Real Example

**10x Genomics dataset (3000 UMI median)**:
```r
# Check gene detection per chromosome
genes_per_chr <- apply(rawmat > 0, 2, function(cell) {
  tapply(cell, gene_chr, sum)
})

summary(genes_per_chr["chr22", ])
# Min: 2, Median: 12, Max: 45

# With ngene.chr = 5: Cells with <5 genes on chr22 excluded
# With ngene.chr = 10: More cells excluded
```

### CLI Examples

```r
# Default (recommended)
copykat(rawmat = data, ngene.chr = 5, ...)

# Permissive (keep more cells, lower quality data)
copykat(rawmat = sparse_data, ngene.chr = 2, ...)

# Strict (high quality only)
copykat(rawmat = deep_seq_data, ngene.chr = 10, ...)
```

### Relationship to Sequencing Depth

| Sequencing Depth | Typical UMI/cell | Recommended ngene.chr |
|------------------|------------------|-----------------------|
| Low (Smart-seq2) | 1000-2000 | 3-5 |
| Medium (10x v2) | 2000-5000 | 5-8 |
| High (10x v3) | 5000-10000 | 8-15 |
| Very High | >10000 | 15-20 |

### Streamlit UI Recommendation

```python
ngene_chr = st.slider(
    "Minimum Genes Per Chromosome",
    min_value=1,
    max_value=20,
    value=5,  # Default
    step=1,
    help="""
    Cells must have at least this many genes detected on each chromosome.
    - Lower (1-3): Keep more cells, tolerate lower quality
    - Higher (10-20): Stricter quality, fewer cells
    - Default (5): Good balance for most datasets
    """
)

# Preview filtering impact
if data_loaded:
    filtered_count = count_cells_passing_filter(data, ngene_chr)
    st.info(f"Approximately {filtered_count}/{total_cells} cells will pass filter")
```

---

## LOW.DR - Low Detection Rate Threshold

### What It Is

Minimum fraction of cells in which a gene must be expressed to be included in **smoothing** analysis.

### Default Value

`LOW.DR = 0.05` (5% of cells)

### What It Does

**Gene filtering for smoothing**:
```r
# For each gene
detection_rate <- sum(gene_expression > 0) / n_cells

if (detection_rate >= LOW.DR) {
  use_for_smoothing(gene)
} else {
  exclude_from_smoothing(gene)
}
```

**Example with 1000 cells**:
```
Gene A: Expressed in 80 cells  (8%)  → INCLUDED (≥ 5%)
Gene B: Expressed in 30 cells  (3%)  → EXCLUDED (< 5%)
Gene C: Expressed in 500 cells (50%) → INCLUDED
```

### Why It Matters

**Rarely detected genes**:
- Mostly zeros (dropout or true absence)
- Contribute noise to smoothing
- Obscure true CNV signals

**This filter**:
- Removes uninformative genes
- Focuses on reliably detected genes
- Improves signal-to-noise ratio

### Tuning Guidelines

| Value | Effect | Use When |
|-------|--------|----------|
| 0.01-0.03 | Very permissive | Sparse data, want maximum genes |
| 0.05 (default) | Balanced | Standard scRNA-seq |
| 0.1-0.2 | Strict | High-quality, high-depth data |

### Impact on Gene Count

**Example: 20,000 genes, 1000 cells**

```r
LOW.DR = 0.01 (1%):   18,500 genes retained (93%)
LOW.DR = 0.05 (5%):   15,000 genes retained (75%)  ← Default
LOW.DR = 0.1 (10%):   12,000 genes retained (60%)
LOW.DR = 0.2 (20%):    8,000 genes retained (40%)
```

### Relationship to UP.DR

`LOW.DR` must be ≤ `UP.DR`

```r
# Valid
LOW.DR = 0.05, UP.DR = 0.1  ✓

# Invalid
LOW.DR = 0.1, UP.DR = 0.05  ✗ Error
```

### CLI Examples

```r
# Default
copykat(rawmat = data, LOW.DR = 0.05, ...)

# Sparse data (10x v2)
copykat(rawmat = sparse_data, LOW.DR = 0.02, ...)

# High-depth data
copykat(rawmat = deep_data, LOW.DR = 0.1, ...)
```

### Common Adjustments

**Low data quality warning appears**:
```
[1] "WARNING: low data quality; assigned LOW.DR to UP.DR..."
```

**Solution**:
```r
# CopyKAT automatically sets UP.DR = LOW.DR
# You can manually increase both:
copykat(rawmat = data,
        LOW.DR = 0.02,
        UP.DR = 0.02,  # Set equal for very sparse data
        ...)
```

### Streamlit UI Recommendation

```python
low_dr = st.slider(
    "Gene Detection Rate (Smoothing)",
    min_value=0.01,
    max_value=0.3,
    value=0.05,
    step=0.01,
    format="%.2f",
    help="""
    Genes must be detected in this fraction of cells to be used in smoothing.
    - Lower (0.01-0.03): Keep more genes, sparse data
    - Higher (0.1-0.2): Stricter filtering, dense data
    - Default (0.05): 5% of cells
    """
)

# Show gene retention estimate
if data_loaded:
    n_genes_kept = estimate_genes_retained(data, low_dr)
    st.info(f"~{n_genes_kept}/{total_genes} genes will be used")
```

---

## UP.DR - Upper Detection Rate Threshold

### What It Is

Minimum fraction of cells in which a gene must be expressed to be used in **segmentation** analysis.

### Default Value

`UP.DR = 0.1` (10% of cells)

### What It Does

**Gene filtering for segmentation**:
```r
# For each gene (after LOW.DR filtering)
if (detection_rate >= UP.DR) {
  use_for_segmentation(gene)
} else {
  exclude_from_segmentation(gene)  # Still used in smoothing
}
```

**Two-tier filtering**:
```
All genes (20,000)
    ↓ LOW.DR filter
Smoothing genes (15,000)
    ↓ UP.DR filter
Segmentation genes (12,000)
```

### Why Two Thresholds?

**Smoothing** (LOW.DR):
- Needs broader gene coverage
- Benefits from more data points
- More tolerant of sparse genes

**Segmentation** (UP.DR):
- Requires reliable detection
- Breakpoint calls need high confidence
- Stricter threshold

### Tuning Guidelines

| LOW.DR | UP.DR | Use Case |
|--------|-------|----------|
| 0.05 | 0.1 | Default, standard data |
| 0.02 | 0.05 | Sparse data (10x v2) |
| 0.1 | 0.2 | High-depth data |
| 0.05 | 0.05 | Very sparse (set equal) |

### Automatic Adjustment

CopyKAT may warn:
```
[1] "WARNING: low data quality; assigned LOW.DR to UP.DR..."
```

Meaning:
- Too few genes pass UP.DR threshold
- CopyKAT sets UP.DR = LOW.DR automatically
- Analysis proceeds with relaxed criteria

### CLI Examples

```r
# Default
copykat(rawmat = data, LOW.DR = 0.05, UP.DR = 0.1, ...)

# Sparse data
copykat(rawmat = data, LOW.DR = 0.02, UP.DR = 0.05, ...)

# Very sparse (set equal)
copykat(rawmat = data, LOW.DR = 0.03, UP.DR = 0.03, ...)

# High-quality data
copykat(rawmat = data, LOW.DR = 0.1, UP.DR = 0.2, ...)
```

### Relationship Constraints

```r
# Must satisfy: LOW.DR ≤ UP.DR

# Valid
LOW.DR = 0.05, UP.DR = 0.1   ✓
LOW.DR = 0.05, UP.DR = 0.05  ✓ (equal is OK)

# Invalid
LOW.DR = 0.1, UP.DR = 0.05   ✗ Will cause error
```

### Streamlit UI Recommendation

```python
col1, col2 = st.columns(2)

with col1:
    low_dr = st.slider(
        "LOW.DR (Smoothing)",
        0.01, 0.3, 0.05, 0.01,
        help="Gene detection rate for smoothing step"
    )

with col2:
    up_dr = st.slider(
        "UP.DR (Segmentation)",
        low_dr, 0.3, max(0.1, low_dr), 0.01,  # min = low_dr
        help="Gene detection rate for segmentation (must be ≥ LOW.DR)"
    )

# Validation
if up_dr < low_dr:
    st.error("UP.DR must be ≥ LOW.DR")
```

---

## win.size - Segmentation Window Size

### What It Is

Number of genes per window used for segmentation and smoothing.

### Default Value

`win.size = 25` genes

### What It Does

**Genome divided into windows**:
```
Chromosome 1 (2000 genes):
- Window 1: genes 1-25
- Window 2: genes 26-50
- Window 3: genes 51-75
- ...
- Window 80: genes 1976-2000
```

Each window gets a single CNV estimate.

### Resolution vs Noise Tradeoff

**Small windows (10-15 genes)**:
- **Pro**: High resolution, detect focal CNVs
- **Con**: More noise, unstable estimates

**Large windows (50-100 genes)**:
- **Pro**: Smooth, stable estimates
- **Con**: Miss focal events, low resolution

**Default (25 genes)**:
- Balanced approach
- ~5Mb genomic resolution
- Detects large-scale CNVs

### Tuning Guidelines

| win.size | Resolution | Use When |
|----------|------------|----------|
| 10-15 | High (~2-3Mb) | Looking for focal amplifications/deletions |
| 25 (default) | Medium (~5Mb) | General CNV detection |
| 50-100 | Low (~10-20Mb) | Noisy data, arm-level events only |
| 100-150 | Very low | Very noisy, chromosome-level only |

### Impact on CNV Calls

**Example: EGFR amplification on chr7**

```r
win.size = 10:
  Breakpoints at: 54.5Mb, 55.5Mb, 56.2Mb
  Fine-grained amplification boundaries

win.size = 25 (default):
  Breakpoints at: 54Mb, 57Mb
  Clear amplification detected

win.size = 100:
  Breakpoint at: 50Mb
  Broad chr7 gain detected
```

### Relationship to Genome Size

**Human genome**: ~3000 Mb, ~20,000 genes

```r
win.size = 25:
  ~20,000 genes / 25 = 800 windows
  ~3000 Mb / 800 = 3.75 Mb per window

win.size = 50:
  ~400 windows
  ~7.5 Mb per window
```

### CLI Examples

```r
# Default resolution
copykat(rawmat = data, win.size = 25, ...)

# High resolution (focal CNVs)
copykat(rawmat = data, win.size = 15, ...)

# Low resolution (noisy data)
copykat(rawmat = data, win.size = 50, ...)

# Very low resolution (chromosome arms)
copykat(rawmat = data, win.size = 100, ...)
```

### Real Examples

**Detecting EGFR focal amplification**:
```r
# EGFR locus: chr7:55,019,017-55,211,628 (~200kb)
# Contains ~10 genes in region

win.size = 10:  May detect focal EGFR amp
win.size = 25:  Detects broader chr7q amp
win.size = 100: Detects whole chr7 gain
```

**Detecting chr10 loss in GBM**:
```r
# chr10: whole chromosome deletion
# Any window size will detect this

win.size = 10, 25, 50, 100:  All detect chr10 loss
```

### Streamlit UI Recommendation

```python
win_size = st.slider(
    "Window Size (genes per segment)",
    min_value=10,
    max_value=150,
    value=25,
    step=5,
    help="""
    Number of genes per window for segmentation.
    - Smaller (10-15): High resolution, detects focal CNVs, more noise
    - Larger (50-100): Low resolution, smooth results, misses focal events
    - Default (25): Balanced, ~5Mb genomic resolution
    """
)

# Visual guide
st.caption(f"Genomic resolution: ~{estimate_resolution(win_size)}Mb per segment")
```

---

Due to length constraints, I'll create the remaining parameter sections in a continuation. Let me save what we have and continue with the rest of the parameters.

**Progress**: Parameters 1-8 of 16 completed. Continuing with remaining parameters...
