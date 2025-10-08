# CopyKAT Overview: Understanding Copy Number Variation Analysis

## Table of Contents
1. [What is CopyKAT?](#what-is-copykat)
2. [Why Use CopyKAT?](#why-use-copykat)
3. [The Biological Basis: CNVs in Cancer](#the-biological-basis-cnvs-in-cancer)
4. [How CopyKAT Works (High-Level)](#how-copykat-works-high-level)
5. [When to Use CopyKAT](#when-to-use-copykat)
6. [Comparison to Other Tools](#comparison-to-other-tools)
7. [Quick Start Example](#quick-start-example)
8. [Expected Inputs and Outputs](#expected-inputs-and-outputs)
9. [Next Steps](#next-steps)

---

## What is CopyKAT?

**CopyKAT** (Copy Number Karyotyping of Tumors) is a computational tool that detects **copy number variations (CNVs)** in single cells using RNA sequencing data.

### In Simple Terms:

Imagine you have a tumor sample containing thousands of individual cells. Some cells are cancerous, some are normal (like immune cells or connective tissue). CopyKAT looks at the gene expression in each cell and determines:

1. **Which cells are cancer cells** (aneuploid - having abnormal chromosome numbers)
2. **Which cells are normal** (diploid - having normal chromosome numbers)
3. **What specific chromosomal gains and losses** each cancer cell has

### Key Capabilities:

- **Automatic classification**: Separates tumor cells from normal cells without prior knowledge
- **Genome-wide CNV detection**: Identifies gains and losses across all chromosomes
- **Subclone identification**: Groups cancer cells into subpopulations with similar CNV patterns
- **Works with standard scRNA-seq data**: No special sequencing protocols required

---

## Why Use CopyKAT?

### The Research Challenge

When you sequence a tumor at single-cell resolution, you get a mixture of:
- Malignant (cancer) cells: ~30-90% of cells
- Immune cells (T cells, B cells, macrophages): ~10-40%
- Stromal cells (fibroblasts, endothelial cells): ~5-15%
- Other normal cell types

**Problem**: How do you tell them apart?

Traditional gene expression clustering can identify cell types (e.g., "T cells" vs "fibroblasts"), but it struggles to distinguish malignant cells from their normal counterparts because:
- Cancer cells can resemble normal tissue cells
- Gene expression varies by cell state, not just cell identity
- Some normal cells (like activated immune cells) have unusual expression patterns

### The CopyKAT Solution

**Cancer cells have a unique signature**: **genomic instability**.

Unlike normal cells that maintain 2 copies of each chromosome (diploid), cancer cells often have:
- **Amplifications**: 3, 4, or more copies of chromosome regions (to boost oncogenes)
- **Deletions**: 1 or 0 copies of regions (to silence tumor suppressors)

CopyKAT exploits this fundamental difference:

```
Normal Cell:  chr1 [==] chr2 [==] chr3 [==] ... (all chromosomes = 2 copies)
Cancer Cell:  chr1 [====] chr2 [=] chr3 [===] ... (variable copy numbers)
                     ↑        ↑        ↑
                  amplified deleted amplified
```

This genomic signature is:
- **Stable** across cell states
- **Distinguishes** malignant from normal
- **Reveals** tumor evolution and subclones

---

## The Biological Basis: CNVs in Cancer

### What Are Copy Number Variations?

In a healthy human cell:
- You inherit **23 pairs of chromosomes** (46 total)
- Each gene has **2 copies** (one from mom, one from dad)
- This is called being **diploid** (2n)

In cancer cells, this breaks down:

| Chromosome Region | Normal | Cancer Example | Effect |
|-------------------|--------|----------------|--------|
| Chromosome 7 | 2 copies | 4 copies | Amplification (drives growth) |
| Chromosome 10 | 2 copies | 1 copy | Deletion (loses tumor suppressor) |
| Chromosome 13 | 2 copies | 0 copies | Complete loss (oncogenic) |

### Why CNVs Happen in Cancer

Cancer cells accumulate CNVs through:
1. **Chromosomal instability**: Errors in cell division
2. **Selective advantage**: Cells with beneficial CNVs outgrow others
3. **Evolutionary pressure**: Treatment kills sensitive clones, resistant ones expand

### Real Examples from Cancer

**Glioblastoma (brain cancer)**:
- Chromosome 7 gain: Amplifies EGFR (growth signal)
- Chromosome 10 loss: Deletes PTEN (tumor suppressor)
- Found in 80-90% of cases

**Melanoma (skin cancer)**:
- Chromosome 1q gain: Common early event
- Chromosome 6q loss: Frequent in metastasis
- Highly heterogeneous patterns

### How Gene Expression Reveals CNVs

**Key Principle**: When a chromosomal region is amplified or deleted, **all genes** in that region show coordinated expression changes.

**Example**:
If chromosome 7 is amplified (4 copies instead of 2), then:
- Gene A on chr7: 2× higher expression
- Gene B on chr7: 2× higher expression
- Gene C on chr7: 2× higher expression
- ... (all genes on chr7 show increased expression)

CopyKAT detects this **coordinated pattern** across many adjacent genes, which is the hallmark of a true CNV (not just individual gene changes).

---

## How CopyKAT Works (High-Level)

### The 10-Step Pipeline

**Step 1: Data Input**
- You provide: Gene expression matrix (genes × cells)
- CopyKAT receives: Thousands of genes, hundreds to thousands of cells

**Step 2: Quality Filtering**
- Remove low-quality cells (too few genes detected)
- Remove uninformative genes (expressed in too few cells)
- Ensures reliable CNV inference

**Step 3: Variance Stabilization**
- Transform data to reduce technical noise
- Makes expression values comparable across genes

**Step 4: Chromosomal Smoothing**
- Smooth gene expression along each chromosome
- Reduces cell-to-cell variability
- Reveals large-scale patterns

**Step 5: Find Normal (Diploid) Cells**
- Cluster cells by expression patterns
- Identify the cluster with **lowest variance** (= most stable = likely normal)
- Use these cells as **baseline reference**

**Step 6: Infer CNVs in All Cells**
- Compare each cell to the diploid baseline
- Regions with higher expression = amplifications
- Regions with lower expression = deletions

**Step 7: Segment the Genome**
- Divide chromosomes into regions of similar copy number
- Find breakpoints where copy number changes
- Creates the "karyotype" of each cell

**Step 8: Classify Cells**
- **Diploid**: Cells with minimal CNVs (normal cells)
- **Aneuploid**: Cells with extensive CNVs (cancer cells)
- Confidence score assigned to each

**Step 9: Identify Subclones**
- Cluster aneuploid cells by CNV similarity
- Reveals tumor subpopulations
- Tracks evolutionary relationships

**Step 10: Generate Outputs**
- CNV heatmap visualization
- Cell classification table
- Confidence scores
- Optional IGV files for genome browser

### Visual Summary

```
Raw Data
   ↓
Filter & Clean
   ↓
Stabilize & Smooth
   ↓
Find Diploid Baseline ← [Cluster with lowest variance]
   ↓
Calculate CNVs → [Amplifications & Deletions]
   ↓
Segment Genome → [Breakpoint detection]
   ↓
Classify Cells → [Aneuploid vs Diploid]
   ↓
Results: Heatmap + Classification + Subclones
```

For detailed algorithm explanation, see [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md).

---

## When to Use CopyKAT

### Ideal Use Cases

**1. Tumor Cell Identification**
- **Scenario**: You have scRNA-seq from a tumor sample
- **Goal**: Separate malignant from stromal/immune cells
- **Why CopyKAT**: Automatic, unsupervised, high accuracy

**2. Intratumoral Heterogeneity**
- **Scenario**: Understanding tumor diversity
- **Goal**: Identify cancer cell subpopulations
- **Why CopyKAT**: Reveals clonal architecture

**3. Treatment Response Studies**
- **Scenario**: Pre vs post-treatment samples
- **Goal**: Track which subclones survive therapy
- **Why CopyKAT**: CNV profiles are stable markers

**4. Metastasis Analysis**
- **Scenario**: Primary tumor vs metastatic sites
- **Goal**: Trace evolutionary relationships
- **Why CopyKAT**: CNV patterns reveal lineage

### When NOT to Use CopyKAT

**1. Normal Tissue Only**
- If your sample has no cancer cells, CopyKAT may create false positives
- Solution: Use known cell type markers first

**2. Liquid Tumors (Some Cases)**
- Leukemias/lymphomas may have subtle or no CNVs
- Solution: Validate with other methods

**3. Pediatric Tumors**
- Some childhood cancers are CNV-quiet
- Solution: Check literature for expected CNV frequency

**4. Very Small Datasets**
- <50 cells: Not enough for baseline estimation
- Solution: Pool replicates or use different methods

**5. Detecting Focal CNVs**
- CopyKAT works at ~5Mb resolution
- Small gene-level amplifications may be missed
- Solution: Use targeted methods for known focal events

---

## Comparison to Other Tools

### CopyKAT vs inferCNV

| Feature | CopyKAT | inferCNV |
|---------|---------|----------|
| **Baseline requirement** | Auto-detects diploid cells | Requires known normal cells |
| **Best for** | Unknown mixtures | Samples with defined normal population |
| **Resolution** | ~5Mb | ~1-5Mb |
| **Speed** | Moderate | Slow |
| **scRNA-seq compatibility** | Excellent (3'/5' data) | Good (full-length better) |
| **Output** | Classification + CNVs | CNVs only |

**When to use CopyKAT**: Unknown cell populations, 10x data, need automatic classification

**When to use inferCNV**: You know which cells are normal, need detailed chromosome visualization

### CopyKAT vs HoneyBADGER

| Feature | CopyKAT | HoneyBADGER |
|---------|---------|-------------|
| **Input** | Expression only | Expression + SNPs |
| **Allelic resolution** | No | Yes (detects LOH) |
| **Data requirement** | Standard scRNA-seq | Needs SNP coverage |
| **Ease of use** | Simple | Complex |

**When to use CopyKAT**: Standard workflow, expression-only data

**When to use HoneyBADGER**: Need allele-specific events, have SNP data

---

## Quick Start Example

### Minimal Working Example (R)

```r
# Load library
library(copykat)

# Load your data (genes × cells matrix)
expression_data <- read.table("my_tumor_data.txt",
                              header = TRUE,
                              row.names = 1)

# Run CopyKAT with default settings
results <- copykat(rawmat = expression_data,
                   id.type = "S",        # Symbol gene names
                   sam.name = "my_tumor",
                   genome = "hg20",      # Human genome
                   n.cores = 4)          # Use 4 CPU cores

# View classification
head(results$prediction)
```

### What Happens:

1. CopyKAT loads your expression matrix
2. Filters low-quality cells and genes (~2-5 min)
3. Identifies diploid baseline cells (~5-10 min)
4. Infers CNVs for all cells (~10-20 min)
5. Generates heatmap and classification

### Output Files Created:

```
my_tumor_copykat_prediction.txt       # Cell classifications
my_tumor_copykat_CNA_results.txt      # CNV matrix (220kb bins)
my_tumor_copykat_CNA_raw_results.txt  # Raw CNV data
my_tumor_copykat_heatmap.png          # Visualization
```

### Interpreting the Classification

```r
# Count results
table(results$prediction$copykat.pred)

# Example output:
# aneuploid diploid
#       450     150
```

This tells you:
- **450 cells are aneuploid** (likely cancer cells)
- **150 cells are diploid** (likely normal cells)

For complete CLI tutorial, see [04_CLI_USAGE_GUIDE.md](04_CLI_USAGE_GUIDE.md).

---

## Expected Inputs and Outputs

### Input Requirements

**Primary Input: Gene Expression Matrix**

Format:
```
              Cell_1    Cell_2    Cell_3    Cell_4
Gene_A        5.23      2.14      3.87      0.45
Gene_B        1.42      6.78      4.12      0.89
Gene_C        2.56      3.21      3.45      7.89
...
```

Requirements:
- **Rows**: Gene names (Ensembl or Symbol)
- **Columns**: Cell barcodes/IDs
- **Values**: Expression counts (raw UMI counts or TPM/CPM)
- **Format**: Tab-delimited text file, CSV, or R data frame

**Optional Input: Known Normal Cells**

If you know which cells are normal (e.g., from marker genes):
```r
normal_cells <- c("Cell_5", "Cell_12", "Cell_19", ...)
```

### Output Files

**1. Prediction Table** (`*_prediction.txt`)

```
cell.names         copykat.pred           copykat.confidence
Cell_1             aneuploid              0.92
Cell_2             diploid                0.85
Cell_3             aneuploid              0.78
```

**2. CNV Matrix** (`*_CNA_results.txt`)

220kb genomic bins × cells matrix showing copy number estimates:
```
              Cell_1    Cell_2    Cell_3
chr1:1-220000 2.1       2.0       3.5
chr1:220001-  1.8       2.0       1.2
```

**3. Heatmap** (`*_heatmap.png`)

Visual representation:
- Rows: Cells (sorted by cluster)
- Columns: Chromosomes (left to right)
- Colors: Red = gain, Blue = loss, White = neutral

**4. Optional SEG File** (`*.seg`)

For IGV genome browser visualization (if `output.seg=TRUE`)

### Data Size Expectations

| Dataset Size | Processing Time | Memory Required |
|--------------|-----------------|-----------------|
| 500 cells, 10k genes | 5-10 min | 4 GB RAM |
| 2,000 cells, 15k genes | 15-30 min | 8 GB RAM |
| 10,000 cells, 20k genes | 1-2 hours | 16-32 GB RAM |

---

## Next Steps

### For Beginners:

1. **Read**: [08_BEGINNER_TUTORIAL.md](08_BEGINNER_TUTORIAL.md) - Complete hands-on walkthrough
2. **Try**: Run CopyKAT on the included test data (glioblastoma)
3. **Understand**: [09_RESULTS_INTERPRETATION.md](09_RESULTS_INTERPRETATION.md) - Learn to read outputs

### For Parameter Tuning:

1. **Reference**: [03_PARAMETERS_REFERENCE.md](03_PARAMETERS_REFERENCE.md) - All parameters explained
2. **Quick Lookup**: [10_PARAMETER_QUICK_REFERENCE.md](10_PARAMETER_QUICK_REFERENCE.md) - Decision guide

### For Dashboard Development:

1. **UI Design**: [05_STREAMLIT_DASHBOARD_DESIGN.md](05_STREAMLIT_DASHBOARD_DESIGN.md)
2. **Integration**: [06_PYTHON_R_INTEGRATION.md](06_PYTHON_R_INTEGRATION.md)

### For Troubleshooting:

1. **Common Issues**: [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)
2. **Algorithm Details**: [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md)

### For Deep Understanding:

1. **Algorithm**: [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md) - How it works internally
2. **Glossary**: [GLOSSARY.md](GLOSSARY.md) - Technical terms explained

---

## Additional Resources

### Official Documentation
- **GitHub**: https://github.com/navinlabcode/copykat
- **Publication**: Gao et al., Nature Biotechnology 2021
  - DOI: 10.1038/s41587-020-00795-2
  - Title: "Delineating copy number and clonal substructure in human tumors from single-cell transcriptomes"

### Related Tools
- **inferCNV**: https://github.com/broadinstitute/infercnv
- **HoneyBADGER**: https://github.com/JEFworks-Lab/HoneyBADGER

### Learning Resources
- **Single-cell analysis**: https://www.singlecellcourse.org/
- **CNV biology**: https://www.nature.com/articles/nrg2958

### Project-Specific Data
- **Glioblastoma dataset**: GSE57872 (Patel et al., Science 2014)
- **Melanoma dataset**: GSE72056 (Tirosh et al., Science 2016)

---

**Last Updated**: 2025-10-07
**Version**: 1.0
**Part of**: CNV-Cancer-RNAseq-analysis Project Documentation
