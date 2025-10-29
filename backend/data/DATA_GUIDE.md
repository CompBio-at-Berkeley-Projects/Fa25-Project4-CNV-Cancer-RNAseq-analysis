# Data Guide: Understanding Cancer Single-Cell RNA-seq Datasets

## Overview

This guide explains the cancer datasets used in this project, designed for researchers who may be new to single-cell RNA sequencing (scRNA-seq) data analysis.

## What is Single-Cell RNA-seq Data?

Single-cell RNA-seq measures gene expression in individual cells, unlike traditional bulk RNA-seq which averages across millions of cells. For cancer research, this is crucial because tumors are heterogeneous mixtures of:
- Malignant (cancer) cells
- Immune cells (T cells, B cells, macrophages)
- Stromal cells (fibroblasts, endothelial cells)
- Other normal cell types

## The Datasets

### 1. GSE72056 - Melanoma Dataset

**Cancer Type**: Melanoma (skin cancer)

**Source**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056

**Scale**:
- Approximately 2,948 single cells
- From 19 melanoma patients
- Fresh tumor resections
- Sequencing method: Smart-seq2

**Significance**:
This landmark study mapped the cellular diversity within melanoma tumors at single-cell resolution. It revealed how malignant cells coexist with diverse immune populations and provided insights into immune evasion mechanisms in melanoma.

**Files in `data/raw/melanoma_compressed/`**:
- `GSE72056_melanoma_single_cell_revised_v2.txt.gz` - Main expression matrix (23,690 genes × ~2,900 cells)
- `GSE72056_series_matrix.txt.gz` - Sample metadata and experimental information
- `GSE72056_family.soft.gz` - GEO SOFT format metadata (not needed for analysis)
- `GSE72056_family.xml.tgz` - XML metadata (not needed for analysis)

### 2. GSE57872 - Glioblastoma Dataset

**Cancer Type**: Glioblastoma multiforme (GBM - aggressive brain cancer)

**Source**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57872

**Scale**:
- 430 tumor cells from 5 patients
- 102 cells from 2 gliomasphere cell lines
- Primary tumors

**Significance**:
This study demonstrated remarkable transcriptional heterogeneity within individual GBM tumors, showing that multiple molecular subtypes can coexist in a single patient's tumor. This challenged the traditional view of GBM classification and revealed the complexity of these aggressive brain cancers.

**Files in `data/raw/glioblastomas_compressed/`**:
- `GSE57872_GBM_data_matrix.txt.gz` - Main expression matrix (5,949 genes × 532 cells)
- `GSE57872_series_matrix.txt.gz` - Sample metadata
- `GSE57872_family.soft.gz` - GEO SOFT format metadata (not needed for analysis)
- `GSE57872_family.xml.tgz` - XML metadata (not needed for analysis)

## Understanding the Expression Matrix Format

### Structure

The main data files are **gene expression matrices** with this structure:

```
            Cell_1    Cell_2    Cell_3    Cell_4    ...
Gene_A      5.23      -2.14     3.87      0.45     ...
Gene_B      -1.42     6.78      4.12      -0.89    ...
Gene_C      2.56      3.21      -3.45     7.89     ...
...
```

**Rows**: Genes (e.g., A2M, AAAS, AAK1, AAMP)
- Melanoma: 23,690 genes
- Glioblastoma: 5,949 genes

**Columns**: Individual cells (cell barcodes/IDs)
- Example cell names: `Cy72_CD45_H02_S758_comb`, `MGH264_A01`
- Each column represents one single cell

**Values**: Log-transformed, normalized gene expression levels
- Positive values: gene is expressed above baseline
- Negative values: gene is expressed below baseline or not detected
- Values like `-3.801469652` or `-5.82024129` indicate very low/no expression
- Higher positive values indicate higher expression

### Cell Naming Conventions

**Melanoma (GSE72056)**:
- Format: `Cy[patient]_[marker]_[well]_[sample]_comb`
- Example: `Cy72_CD45_H02_S758_comb`
  - `Cy72`: Patient 72
  - `CD45`: Cell surface marker (indicates immune cell sorting)
  - `H02`: Well position on plate
  - `S758`: Sample number

**Glioblastoma (GSE57872)**:
- Format: `MGH[patient]_[well]` or `CSC[line]_[well]`
- Example: `MGH264_A01`
  - `MGH264`: Patient from Massachusetts General Hospital
  - `A01`: Well position
- Example: `CSC6_A05`
  - `CSC6`: Cancer stem cell line 6
  - `A05`: Well position

## What is Copy Number Variation (CNV)?

### The Biology

**Normal cells** are diploid - they have 2 copies of each chromosome (one from each parent).

**Cancer cells** often become aneuploid - they gain or lose entire chromosome arms or regions, resulting in:
- Amplifications: 3, 4, or more copies of a region
- Deletions: 1 or 0 copies of a region

### Why CNVs Matter in Cancer

CNVs are hallmarks of cancer cells because:
1. Oncogene amplification (e.g., MYC, EGFR) drives tumor growth
2. Tumor suppressor loss (e.g., TP53, PTEN) removes growth brakes
3. Genomic instability is a fundamental cancer characteristic
4. CNV patterns can distinguish malignant from normal cells

### How We Detect CNVs from Expression Data

**Key Principle**: When a chromosomal region is amplified or deleted, ALL genes in that region show coordinated expression changes.

Example:
- If chromosome 7 is amplified (common in glioblastoma), all genes on chr7 will show higher expression
- If chromosome 10 is deleted, all genes on chr10 will show lower expression

**Tools exploit this pattern**:
- Order genes by chromosomal position
- Look for large regions with coordinated expression changes
- Regions with many consecutive overexpressed genes = amplification
- Regions with many consecutive underexpressed genes = deletion

## The CNV Analysis Tools

### CopyKAT (Primary Tool for This Project)

**Full Name**: Copy Number Karyotyping of Tumors

**How it works**:
1. Takes the expression matrix as input
2. Segments genome into regions
3. Uses Bayesian statistics to estimate copy number in each cell
4. Classifies cells as:
   - **Diploid** (normal, 2n) - likely non-malignant
   - **Aneuploid** (abnormal) - likely malignant

**Advantages**:
- Automatic tumor/normal classification
- No reference population required
- Handles noisy scRNA-seq data well

**Output**:
- CNV heatmap showing gains/losses across genome
- Cell classifications (diploid vs aneuploid)
- Prediction confidence scores

### inferCNV (Future Enhancement)

**How it differs**:
- Requires known reference normal cells
- Compares tumor cells to reference
- Generates detailed chromosome-level heatmaps
- More manual interpretation required

## Data File Details

### Which Files to Use

**For analysis, you only need**:
- Melanoma: `GSE72056_melanoma_single_cell_revised_v2.txt.gz`
- Glioblastoma: `GSE57872_GBM_data_matrix.txt.gz`

**Can ignore**:
- `.soft` files: GEO database format metadata
- `.xml` files: Alternative metadata format
- `series_matrix` files: May contain useful sample annotations but not required for CNV analysis

### File Sizes

After decompression:
- Melanoma matrix: ~680 MB (23,690 genes × ~2,900 cells)
- Glioblastoma matrix: ~27 MB (5,949 genes × 532 cells)

### How to Read the Data

**In R**:
```r
# Read compressed file directly
data <- read.table(gzfile("GSE72056_melanoma_single_cell_revised_v2.txt.gz"),
                   header = TRUE,
                   row.names = 1,
                   sep = "\t")
```

**In Python**:
```python
import pandas as pd

# Read compressed file directly
data = pd.read_csv("GSE72056_melanoma_single_cell_revised_v2.txt.gz",
                   sep="\t",
                   index_col=0,
                   compression='gzip')
```

## Expected Cell Composition

### Melanoma Tumors (GSE72056)

Typical composition:
- **Malignant melanoma cells**: 30-60% (highly variable)
- **T cells**: 20-40% (CD45+ cells)
- **B cells**: 1-5%
- **Macrophages**: 10-20%
- **Fibroblasts**: 5-15%
- **Endothelial cells**: 2-5%

CNV analysis will separate malignant from immune/stromal cells.

### Glioblastoma Tumors (GSE57872)

Typical composition:
- **Malignant GBM cells**: 60-90%
- **Microglia/Macrophages**: 5-20%
- **Oligodendrocytes**: 2-10%
- **Astrocytes**: 1-5%
- **Endothelial cells**: 1-3%

GBM has higher malignant cell proportion than melanoma.

## Quality Metrics

### What Makes a Good scRNA-seq Dataset?

1. **Sequencing Depth**:
   - Number of genes detected per cell (typically 2,000-8,000 for Smart-seq2)
   - Total reads per cell

2. **Cell Viability**:
   - Low mitochondrial gene percentage (<10-20%)
   - Indicates healthy cells, not dying/stressed cells

3. **Technical Quality**:
   - Batch effects minimized
   - Even coverage across genome
   - Low doublet rate (two cells in one droplet)

### Dataset Quality Notes

**GSE72056 (Melanoma)**:
- High-quality Smart-seq2 protocol
- Full-length transcript coverage
- Well-validated cell type annotations available

**GSE57872 (Glioblastoma)**:
- Pioneering early scRNA-seq study
- Smaller scale but high impact
- Well-characterized tumors with clinical data

## Common Data Challenges

### 1. Sparsity

scRNA-seq data is sparse - many genes show zero expression in many cells due to:
- Biological reality (gene not active)
- Technical dropout (RNA molecule not captured)

**Impact**: Expression values of `-3.8` to `-7.0` are common, representing very low/zero expression.

### 2. Batch Effects

Cells processed on different days/plates may show systematic differences.

**Solution**: CopyKAT and inferCNV focus on large-scale chromosomal patterns, which are more robust to batch effects than individual gene expression.

### 3. Cell Type Heterogeneity

Tumors contain diverse cell types with different baseline expression patterns.

**Solution**: CNV analysis works because chromosomal aberrations are independent of cell type identity.

## Validation Strategy

### Melanoma Dataset Validation

The original study provided cell classifications. Our pipeline validation:
1. Run CopyKAT on melanoma data
2. Compare our aneuploid/diploid calls to author classifications
3. Calculate concordance: `matching cells / total cells`
4. **Success criterion**: >90% concordance

### What Good CNV Results Look Like

**Malignant cells**:
- Clear chromosomal gains and losses
- Consistent CNV patterns across malignant cells from same tumor
- Known cancer-associated alterations visible

**Normal cells**:
- Relatively flat CNV profile
- Minimal large-scale aberrations
- Diploid state maintained

## Next Steps for Analysis

1. **Data Loading**: Decompress and load expression matrices
2. **Quality Control**: Filter low-quality cells
3. **CNV Inference**: Run CopyKAT
4. **Visualization**: Generate heatmaps
5. **Cell Classification**: Identify malignant vs normal
6. **Validation**: Compare to known annotations

## Additional Resources

**GEO Database**:
- Melanoma: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056
- Glioblastoma: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57872

**Original Publications**:
- GSE72056: Tirosh et al., Science 2016 - "Dissecting the multicellular ecosystem of metastatic melanoma by single-cell RNA-seq"
- GSE57872: Patel et al., Science 2014 - "Single-cell RNA-seq highlights intratumoral heterogeneity in primary glioblastoma"

**Tool Documentation**:
- CopyKAT: https://github.com/navinlabcode/copykat
- inferCNV: https://github.com/broadinstitute/infercnv

## Glossary

**Aneuploid**: Abnormal number of chromosomes or chromosome regions

**Diploid**: Normal two copies of each chromosome (2n)

**CNV**: Copy Number Variation - gain or loss of genomic regions

**scRNA-seq**: Single-cell RNA sequencing

**Expression Matrix**: Table with genes as rows, cells as columns, expression values in cells

**Barcode**: Unique identifier for each cell

**Smart-seq2**: Full-length transcript sequencing protocol

**Log-normalization**: Mathematical transformation to make expression values comparable across genes/cells

**Heatmap**: Color-coded visualization where colors represent expression or CNV levels

**Batch Effect**: Systematic technical variation between sample groups

**Doublet**: Two cells accidentally captured as one, creating artifact

**Mitochondrial Genes**: Genes from mitochondrial genome, high % indicates dying cells
