# CopyKAT & scRNA-seq Glossary

Comprehensive glossary of terms used in CopyKAT analysis and single-cell RNA sequencing.

---

## A

**Amplification**
- Increase in copy number of a genomic region
- Example: EGFR amplification in glioblastoma (4-8 copies instead of 2)
- Detected as higher expression of all genes in the region

**Aneuploid**
- Having an abnormal number of chromosomes or chromosome regions
- Characteristic of cancer cells
- Opposite of diploid (normal)
- Example: Cell with chr7 gain + chr10 loss = aneuploid

**AnnData**
- Python data structure for annotated data matrices
- Common format for scRNA-seq analysis in Scanpy
- Stores expression + cell/gene metadata

---

## B

**Baseline (Diploid Baseline)**
- Reference expression profile from normal (diploid) cells
- Used to detect CNVs by comparison
- CopyKAT auto-detects this from low-variance cluster

**Batch Effect**
- Systematic technical variation between sample groups
- Can obscure biological signal
- Example: Cells processed on different days showing different patterns

**Bayesian**
- Statistical approach using probability distributions
- CopyKAT uses Bayesian methods for segmentation
- Incorporates prior knowledge and uncertainty

**Breakpoint**
- Position where copy number changes
- Example: chr7 at 55Mb changes from CN=2 to CN=4
- Detected by segmentation algorithms

---

## C

**Cell Barcode**
- Unique identifier for each cell in scRNA-seq
- Example: `AAACCTGAGAAACCAT-1`
- Allows demultiplexing of pooled cells

**CNV (Copy Number Variation)**
- Gain or loss of genomic regions
- Can be:
  - Focal: <5Mb (e.g., single gene)
  - Regional: 5-50Mb
  - Arm-level: >50Mb (whole chromosome arm)
  - Whole chromosome: Entire chromosome

**Copy Number (CN)**
- Number of copies of a genomic region
- Normal (diploid): CN = 2
- Deletion: CN = 0 or 1
- Amplification: CN = 3, 4, 5+

---

## D

**Deletion**
- Loss of genomic material
- Heterozygous deletion: 1 copy (CN=1)
- Homozygous deletion: 0 copies (CN=0)
- Example: chr10 deletion in GBM (PTEN loss)

**Detection Rate**
- Fraction of cells expressing a gene
- Used for filtering (LOW.DR, UP.DR parameters)
- Example: 5% detection rate = expressed in 5% of cells

**Diploid**
- Having the normal number of chromosomes (2N)
- Each chromosome has 2 copies (one from each parent)
- Characteristic of normal cells

**DLM (Dynamic Linear Model)**
- Statistical model for time-series or spatial data
- CopyKAT uses polynomial DLM for chromosomal smoothing
- Separates signal from noise

**Doublet**
- Two cells captured as one in scRNA-seq
- Creates artificial "cell" with mixed signals
- Should be removed before CNV analysis

**Dropout**
- Failure to detect an expressed gene due to technical limitations
- Common in scRNA-seq (especially low-depth protocols)
- Causes sparsity in data matrix

---

## E

**Ensembl ID**
- Gene identifier from Ensembl database
- Example: ENSG00000146648 (EGFR)
- Alternative to gene symbols

**Expression Matrix**
- Table of gene expression values
- Rows = genes, Columns = cells
- Values = UMI counts or normalized expression

---

## F

**Focal CNV**
- Small copy number change (<5Mb)
- Often targets single genes (e.g., EGFR, MYC)
- Requires high-resolution methods to detect

**Freeman-Tukey Transformation (FTT)**
- Variance-stabilizing transformation for count data
- Formula: FTT(x) = √x + √(x+1)
- Makes genes with different expression levels comparable

---

## G

**Gene Symbol**
- Human-readable gene name
- Example: EGFR, TP53, MYC
- Standard nomenclature (HUGO for human)

**Genome Build**
- Version of reference genome sequence
- Human: hg19, hg20 (GRCh37, GRCh38)
- Mouse: mm9, mm10 (GRCm38, GRCm39)

**Genomic Instability**
- Tendency to accumulate genetic changes
- Hallmark of cancer
- Manifests as CNVs, mutations, rearrangements

**GMM (Gaussian Mixture Model)**
- Statistical model assuming data comes from mixture of Gaussians
- CopyKAT uses 3-component GMM:
  - Deletions (CN < 2)
  - Neutral (CN ≈ 2)
  - Amplifications (CN > 2)

---

## H

**Heatmap**
- Color-coded visualization of data matrix
- CNV heatmap:
  - Rows: Cells
  - Columns: Genome positions
  - Colors: Red=gain, Blue=loss, White=neutral

**Heterogeneity (Intratumoral)**
- Diversity within a tumor
- Multiple subclones with different CNV patterns
- Drives treatment resistance

**Heterozygous**
- Having two different alleles
- Heterozygous deletion: Loss of one copy (CN=1)

**Homozygous**
- Having two identical alleles
- Homozygous deletion: Loss of both copies (CN=0)

---

## I

**inferCNV**
- Alternative tool for CNV detection from scRNA-seq
- Requires known normal cell reference
- Generates detailed chromosome heatmaps

---

## K

**Karyotype**
- Complete set of chromosomes in a cell
- CopyKAT infers "transcriptional karyotype" from expression
- Shows all CNVs across genome

**KS Test (Kolmogorov-Smirnov Test)**
- Statistical test comparing two distributions
- CopyKAT uses it for breakpoint detection
- Tests if adjacent genome segments differ

---

## L

**Log-normalization**
- Logarithmic transformation of expression values
- Reduces skewness, stabilizes variance
- Common preprocessing step

**Loss of Heterozygosity (LOH)**
- Loss of one allele's function
- Can result from deletion or mutation
- Not detected by expression-based methods like CopyKAT

---

## M

**Malignant**
- Cancerous, invasive, abnormal
- Malignant cells typically show CNVs
- Synonymous with "tumor" or "aneuploid" in CNV context

**Mitochondrial Genes**
- Genes encoded in mitochondrial genome
- High % indicates dying/stressed cells
- Used for quality control filtering

---

## N

**Normalization**
- Adjusting expression values for technical factors
- Methods: TPM, CPM, scran, SCTransform
- Makes cells/genes comparable

**Normal Cells**
- Non-cancerous cells in tumor sample
- Immune cells (CD45+)
- Stromal cells (fibroblasts, endothelium)
- Usually diploid

---

## O

**Oncogene**
- Gene that promotes cancer when amplified/activated
- Examples: MYC, EGFR, KRAS
- Often targeted by amplifications

---

## P

**PDX (Patient-Derived Xenograft)**
- Patient tumor grown in mouse
- Contains human tumor + some mouse cells
- Mixed species requires careful analysis

**Ploidy**
- Number of chromosome sets
- Diploid (2N): Normal
- Triploid (3N), Tetraploid (4N): Whole-genome duplications

---

## Q

**Quality Control (QC)**
- Filtering low-quality cells and genes
- Metrics: genes/cell, UMI/cell, % mitochondrial
- Critical before CNV analysis

---

## R

**Resolution (Genomic)**
- Smallest CNV size detectable
- Determined by window size
- CopyKAT: typically ~5Mb

**RPKM / FPKM / TPM**
- Normalization methods
- RPKM/FPKM: Reads Per Kilobase Million
- TPM: Transcripts Per Million
- Account for gene length and library size

---

## S

**Segmentation**
- Dividing genome into regions of similar copy number
- Identifies breakpoints
- Creates cleaner CNV profiles

**Smart-seq2**
- Full-length scRNA-seq protocol
- Higher sensitivity than droplet-based methods
- Better for CNV detection

**Sparse (Data)**
- Many zero values in matrix
- Common in scRNA-seq due to dropout
- Requires special handling

**Subclone**
- Distinct tumor cell population
- Shares some CNVs, differs in others
- Represents evolutionary branches

---

## T

**Tumor Purity**
- Fraction of cells that are malignant
- High purity: >80% tumor cells
- Low purity: <50% tumor cells
- Affects baseline detection

**Tumor Suppressor**
- Gene that prevents cancer when functional
- Examples: TP53, PTEN, RB1
- Often lost by deletions

---

## U

**UMI (Unique Molecular Identifier)**
- Barcode attached to each RNA molecule
- Allows absolute counting (not PCR amplification bias)
- Standard in modern scRNA-seq (10x Genomics)

**UP.DR (Upper Detection Rate)**
- CopyKAT parameter
- Minimum gene detection rate for segmentation
- Higher threshold than LOW.DR

---

## V

**Variance Stabilization**
- Making variance independent of mean
- Necessary for many statistical methods
- Freeman-Tukey transformation achieves this

---

## W

**Window Size**
- Number of genes per segment
- CopyKAT parameter: `win.size`
- Larger = smoother, lower resolution

---

## 10x Genomics

**10x Genomics**
- Leading scRNA-seq platform
- Droplet-based, high-throughput
- Versions: v2 (~2000 UMI/cell), v3 (~5000 UMI/cell)

---

## Common Abbreviations

| Abbreviation | Full Name |
|--------------|-----------|
| CN | Copy Number |
| CNV | Copy Number Variation |
| CNA | Copy Number Aberration (same as CNV) |
| DLM | Dynamic Linear Model |
| FTT | Freeman-Tukey Transformation |
| GBM | Glioblastoma Multiforme |
| GMM | Gaussian Mixture Model |
| IGV | Integrative Genomics Viewer |
| KS | Kolmogorov-Smirnov |
| LOH | Loss of Heterozygosity |
| PDX | Patient-Derived Xenograft |
| QC | Quality Control |
| scRNA-seq | Single-Cell RNA Sequencing |
| TPM | Transcripts Per Million |
| UMI | Unique Molecular Identifier |

---

## Conceptual Relationships

```
Cancer Cell
    ↓
Genomic Instability
    ↓
Copy Number Variations (CNVs)
    ↓
Expression Changes
    ↓
CopyKAT Detection
    ↓
Aneuploid Classification
```

```
scRNA-seq Experiment
    ↓
Expression Matrix
    ↓
Quality Control
    ↓
Normalization
    ↓
CNV Inference (CopyKAT)
    ↓
Cell Classification
    ↓
Biological Interpretation
```

---

**See Also**:
- [01_COPYKAT_OVERVIEW.md](01_COPYKAT_OVERVIEW.md) - Introduction to concepts
- [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md) - Technical details
- [DATA_GUIDE.md](../data/DATA_GUIDE.md) - Dataset-specific terms
