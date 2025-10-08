# CopyKAT Results Interpretation Guide

## Table of Contents
1. [Output Files Overview](#output-files-overview)
2. [Prediction Table](#prediction-table)
3. [CNV Matrix](#cnv-matrix)
4. [Heatmap Visualization](#heatmap-visualization)
5. [Confidence Scores](#confidence-scores)
6. [Biological Interpretation](#biological-interpretation)
7. [Quality Assessment](#quality-assessment)
8. [Publication-Ready Figures](#publication-ready-figures)

---

## Output Files Overview

After running CopyKAT, you'll find these files in your output directory:

```
results/
├── sample_copykat_prediction.txt        # Cell classifications
├── sample_copykat_CNA_results.txt       # CNV matrix (220kb bins)
├── sample_copykat_CNA_raw_results.txt   # Raw CNV estimates
├── sample_copykat_heatmap.png           # Visualization
└── sample.seg                           # Optional: IGV file
```

### File Purposes

| File | Purpose | When to Use |
|------|---------|-------------|
| **prediction.txt** | Cell classifications | Identify tumor vs normal cells |
| **CNA_results.txt** | CNV matrix | Detailed CNV analysis, custom plots |
| **CNA_raw_results.txt** | Pre-segmentation data | Advanced users, debugging |
| **heatmap.png** | Quick visualization | Initial results review, presentations |
| **.seg** | IGV format | Genome browser visualization |

---

## Prediction Table

### File: `*_copykat_prediction.txt`

**Structure**:
```
cell.names            copykat.pred          copykat.confidence
Cell_1                aneuploid             0.92
Cell_2                diploid               0.88
Cell_3                aneuploid             0.75
Cell_4                diploid               0.95
...
```

### Columns Explained

**1. cell.names**
- Cell barcode or ID
- Matches column names from input matrix
- Example: `AAACCTGAGAAACCAT-1`, `Cell_123`

**2. copykat.pred**
- Classification result
- Values:
  - `"aneuploid"` = Cancer/tumor cell (abnormal CNVs)
  - `"diploid"` = Normal cell (no significant CNVs)
  - `"not.defined"` = Uncertain (rare)

**3. copykat.confidence**
- Classification confidence (0-1)
- Interpretation:
  - **>0.9**: High confidence (very reliable)
  - **0.7-0.9**: Good confidence (reliable)
  - **0.5-0.7**: Low confidence (review manually)
  - **<0.5**: Very uncertain (likely borderline case)

### Reading the Results in R

```r
# Load predictions
predictions <- read.table("sample_copykat_prediction.txt",
                          header = TRUE,
                          sep = "\t",
                          stringsAsFactors = FALSE)

# Summary statistics
table(predictions$copykat.pred)
# Example output:
# aneuploid  diploid
#       450      150

# Mean confidence by group
tapply(predictions$copykat.confidence,
       predictions$copykat.pred,
       mean)
# aneuploid   diploid
#      0.87      0.91

# Identify low-confidence cells
low_conf <- predictions[predictions$copykat.confidence < 0.7, ]
print(low_conf)
```

### Typical Results for Different Samples

**Patient glioblastoma**:
```
aneuploid: 600 cells (80%)  # Tumor cells
diploid:   150 cells (20%)  # Immune/stromal cells
```

**Patient melanoma**:
```
aneuploid: 300 cells (45%)  # Tumor cells
diploid:   366 cells (55%)  # High immune infiltration
```

**Pure cell line (HeLa)**:
```
aneuploid: 500 cells (100%) # All cancer cells
diploid:     0 cells (0%)   # No normal cells
```

---

## CNV Matrix

### File: `*_copykat_CNA_results.txt`

**Structure**:
```
chrom    chrompos         abspos      Cell_1  Cell_2  Cell_3  ...
chr1     1_220000         1           2.1     2.0     3.5     ...
chr1     220001_440000    220001      1.9     2.0     3.4     ...
chr1     440001_660000    440001      2.0     2.0     3.6     ...
...
chr22    50000001_END     3088270000  2.0     2.1     2.0     ...
```

### Columns Explained

**1-3: Position Information**
- `chrom`: Chromosome (chr1, chr2, ..., chr22)
- `chrompos`: Position range within chromosome
- `abspos`: Absolute position in genome (for plotting)

**4+: Cell CNV Values**
- One column per cell
- Values represent inferred copy number
- Interpretation:
  - `0-0.5`: Homozygous deletion
  - `0.5-1.5`: Heterozygous loss
  - `1.5-2.5`: Normal (diploid)
  - `2.5-3.5`: Single copy gain
  - `3.5+`: Amplification

### Interpreting CNV Values

**Example cell CNV profile**:
```
chr1: 2.0, 2.1, 2.0, 2.0  → Normal
chr7: 4.2, 4.1, 4.3, 4.0  → Amplification
chr10: 0.9, 1.0, 0.8, 1.1 → Deletion
chr17: 2.0, 2.1, 2.0, 1.9 → Normal
```

**Biological meaning**:
- Chr7 amplification: ~4 copies (2× normal)
- Chr10 deletion: ~1 copy (half normal)
- Known in glioblastoma: EGFR (chr7) gain + PTEN (chr10) loss

### Reading CNV Matrix in R

```r
# Load CNV matrix
cnv_matrix <- read.table("sample_copykat_CNA_results.txt",
                         header = TRUE,
                         sep = "\t",
                         row.names = 1,
                         check.names = FALSE)

# Remove position columns
cnv_data <- cnv_matrix[, -(1:2)]  # Remove chrom and abspos
position_info <- cnv_matrix[, 1:2]

# Inspect specific cell
cell_profile <- cnv_data[, "Cell_123"]
plot(cell_profile, type="l", main="Cell_123 CNV Profile",
     ylab="Copy Number", xlab="Genome Position")
abline(h=2, col="red", lty=2)  # Diploid baseline

# Find regions with CNVs
amplifications <- cell_profile > 2.5
deletions <- cell_profile < 1.5

# Which chromosomes are altered?
chrom_means <- tapply(cell_profile, position_info$chrom, mean)
print(chrom_means)
```

### Common CNV Patterns by Cancer Type

**Glioblastoma**:
```
chr7 gain:  ~4.0 (EGFR amplification)
chr10 loss: ~1.0 (PTEN deletion)
chr9p loss: ~1.0 (CDKN2A deletion)
```

**Melanoma**:
```
chr1q gain:  ~3.0
chr6q loss:  ~1.0
chr7 gain:   ~3.0
```

**Breast cancer (Her2+)**:
```
chr17q gain: ~3-4 (ERBB2/Her2 amplification)
chr1q gain:  ~3.0
```

---

## Heatmap Visualization

### File: `*_copykat_heatmap.png`

**Layout**:
```
        [Dendrogram]
            ↓
┌────────────────────────────┐
│  Cell clustering tree      │
├────────────────────────────┤
│                            │
│   [CNV Heatmap]            │
│   Rows = Cells             │
│   Columns = Chromosomes    │
│   Colors = CN values       │
│                            │
└────────────────────────────┘
     chr1 chr2 ... chr22
```

### Color Scheme

```
Deep Blue     Blue      White     Red      Deep Red
    ↓          ↓         ↓        ↓          ↓
   CN=0      CN=1      CN=2     CN=3       CN≥4
(Hom Del)  (Het Del) (Normal) (Gain)  (Amplification)
```

### Reading the Heatmap

**1. Overall Pattern**
- **Mostly white**: Normal cells (diploid)
- **Red and blue bands**: Tumor cells (aneuploid)
- **Vertical bands**: Chromosome-level CNVs

**2. Cell Clustering (Rows)**
- **Top cluster**: Often diploid cells
- **Bottom clusters**: Aneuploid cells with similar CNVs
- **Sub-clusters**: Tumor subclones

**3. Genomic Regions (Columns)**
- **Red columns**: Commonly amplified chromosomes
- **Blue columns**: Commonly deleted chromosomes
- **Mixed columns**: Heterogeneous alterations

### Example Interpretations

**Heatmap Pattern 1: Clear Separation**
```
[Dendrogram shows 2 distinct branches]

Cluster 1 (White rows):     Diploid cells (immune/stromal)
Cluster 2 (Red/Blue rows):  Aneuploid cells (tumor)
```
**Conclusion**: Good quality, clear tumor/normal separation

**Heatmap Pattern 2: Multiple Subclones**
```
[Dendrogram shows 3+ branches]

Cluster 1 (White):      Diploid
Cluster 2 (Red chr7):   Subclone A (chr7 gain)
Cluster 3 (Red chr7,    Subclone B (chr7 gain + chr13 gain)
           chr13):
```
**Conclusion**: Intratumoral heterogeneity, multiple evolutionary branches

**Heatmap Pattern 3: Poor Quality**
```
[Dendrogram poorly separated]

All cells:  Random red/blue speckles, no clear patterns
```
**Conclusion**: Noisy data, unreliable results - check data quality

---

## Confidence Scores

### Understanding Confidence

**High confidence (>0.9)**:
- Cell clearly belongs to cluster
- CNV pattern unambiguous
- Classification reliable

**Medium confidence (0.7-0.9)**:
- Cell assigned to cluster but with some uncertainty
- May be transitional or intermediate
- Generally trustworthy

**Low confidence (<0.7)**:
- Cell classification uncertain
- May be borderline between diploid/aneuploid
- Requires manual review

### Distribution of Confidence Scores

**Healthy distribution**:
```r
summary(predictions$copykat.confidence)
#   Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
#  0.550   0.850   0.910   0.890   0.950   0.990
```
Most cells have >0.85 confidence

**Problematic distribution**:
```r
summary(predictions$copykat.confidence)
#   Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
#  0.320   0.550   0.650   0.640   0.720   0.880
```
Many cells <0.7 suggests poor separation

### What to Do with Low-Confidence Cells

**Option 1: Manual review**
```r
# Visualize low-confidence cells
low_conf_cells <- predictions$cell.names[predictions$copykat.confidence < 0.7]

for (cell in low_conf_cells) {
  plot(cnv_data[, cell], type="l", main=cell)
  abline(h=2, col="red", lty=2)
}
```

**Option 2: Exclude from downstream analysis**
```r
# Keep only high-confidence cells
high_conf <- predictions[predictions$copykat.confidence > 0.8, ]

# Subset expression matrix
reliable_cells <- high_conf$cell.names
filtered_matrix <- raw_data[, reliable_cells]
```

**Option 3: Re-run with adjusted parameters**
```r
# Try different settings
copykat(rawmat = data,
        KS.cut = 0.05,  # More sensitive
        ...)
```

---

## Biological Interpretation

### Linking CNVs to Biology

**Step 1: Identify Altered Chromosomes**
```r
# For aneuploid cells
aneuploid_cells <- predictions$cell.names[predictions$copykat.pred == "aneuploid"]
aneuploid_cnv <- cnv_data[, aneuploid_cells]

# Mean CNV per chromosome
chr_means <- tapply(colMeans(aneuploid_cnv), position_info$chrom, mean)

# Chromosomes with alterations
amplified <- names(chr_means[chr_means > 2.3])
deleted <- names(chr_means[chr_means < 1.7])

print(paste("Amplified:", paste(amplified, collapse=", ")))
print(paste("Deleted:", paste(deleted, collapse=", ")))
```

**Step 2: Map to Cancer Genes**

| Chromosome | Common Gene | Cancer Association |
|------------|-------------|-------------------|
| chr7 gain | EGFR, MET | Glioblastoma, lung cancer |
| chr8 gain | MYC | Many cancers |
| chr10 loss | PTEN | Glioblastoma, prostate |
| chr13 gain | CDK8, RB1 | Breast, bladder |
| chr17p loss | TP53 | Most cancers |
| chr17q gain | ERBB2 | Breast cancer (Her2+) |

**Step 3: Compare to Literature**

Search for: "[Cancer type] + CNV + [chromosome]"

Example results for glioblastoma:
- Chr7 gain: Found in 80-90% of GBM (Verhaak et al., Cancer Cell 2010)
- Chr10 loss: Found in 70-80% of GBM (TCGA, Nature 2008)
- Your results match known biology ✓

---

## Quality Assessment

### Checklist for Good Results

- [ ] Clear separation in heatmap (diploid vs aneuploid clusters)
- [ ] Confidence scores mostly >0.8
- [ ] Aneuploid fraction matches expectations (30-90% for tumors)
- [ ] CNV patterns match known biology
- [ ] Few "not.defined" cells (<5%)
- [ ] Reproducible with slightly different parameters

### Red Flags

**Warning Sign 1**: All cells classified as aneuploid
```
Possible causes:
- No normal cells in sample (pure cell line?)
- Baseline detection failed
- Parameters too sensitive
```

**Warning Sign 2**: All cells diploid
```
Possible causes:
- Sample is actually all normal
- Parameters too stringent
- Subtle CNVs not detected
```

**Warning Sign 3**: Random speckled heatmap
```
Possible causes:
- Poor data quality
- Dropout too severe
- win.size too small
```

**Warning Sign 4**: Many low-confidence cells (>30%)
```
Possible causes:
- Mixed populations hard to separate
- Batch effects
- Insufficient cells
```

### Validation Approaches

**1. Marker gene expression**
```r
# Check immune markers in diploid cells
diploid_cells <- predictions$cell.names[predictions$copykat.pred == "diploid"]
immune_markers <- c("PTPRC", "CD3D", "CD8A")  # T cells

# Should be high
raw_data[immune_markers, diploid_cells]
```

**2. CNV concordance with known alterations**
```r
# For glioblastoma, expect chr7 gain + chr10 loss
# Calculate fraction with expected pattern

aneuploid_cells <- predictions$cell.names[predictions$copykat.pred == "aneuploid"]
chr7_values <- cnv_data["chr7_mean", aneuploid_cells]
chr10_values <- cnv_data["chr10_mean", aneuploid_cells]

expected_pattern <- (chr7_values > 2.5) & (chr10_values < 1.5)
concordance <- sum(expected_pattern) / length(aneuploid_cells)

print(paste("Concordance with GBM signature:", round(concordance*100, 1), "%"))
```

**3. Compare to author annotations**
```r
# If original study provided cell type annotations
author_labels <- metadata$cell_type

# How well do CopyKAT calls match?
comparison <- table(Predicted = predictions$copykat.pred,
                    Actual = author_labels)
print(comparison)

# Calculate accuracy
accuracy <- sum(diag(comparison)) / sum(comparison)
```

---

## Publication-Ready Figures

### Creating Custom Heatmaps

```r
library(pheatmap)

# Load data
cnv <- read.table("sample_copykat_CNA_results.txt",
                  header=TRUE, row.names=1, check.names=FALSE)
predictions <- read.table("sample_copykat_prediction.txt",
                          header=TRUE)

# Prepare matrix (cells × genome)
cnv_matrix <- t(as.matrix(cnv[, -(1:2)]))

# Annotation
annotation_row <- data.frame(
  Classification = predictions$copykat.pred,
  Confidence = predictions$copykat.confidence
)
rownames(annotation_row) <- predictions$cell.names

# Colors
ann_colors <- list(
  Classification = c(aneuploid="red", diploid="blue"),
  Confidence = colorRampPalette(c("white", "darkgreen"))(100)
)

# Plot
pheatmap(cnv_matrix,
         color = colorRampPalette(c("blue", "white", "red"))(100),
         breaks = seq(0, 4, length.out=101),
         annotation_row = annotation_row,
         annotation_colors = ann_colors,
         show_rownames = FALSE,
         show_colnames = FALSE,
         cluster_cols = FALSE,
         main = "CNV Landscape",
         filename = "publication_heatmap.pdf",
         width = 10,
         height = 8)
```

### Summary Statistics for Papers

```r
# Classification summary
class_summary <- table(predictions$copykat.pred)

# Report as:
# "CopyKAT identified 450 aneuploid cells (75%) and 150 diploid cells (25%)"

# Confidence metrics
conf_stats <- tapply(predictions$copykat.confidence,
                     predictions$copykat.pred,
                     function(x) c(mean=mean(x), sd=sd(x)))

# Report as:
# "Mean confidence scores: aneuploid = 0.87 ± 0.08, diploid = 0.91 ± 0.05"

# Common CNVs
# (Calculate from CNV matrix as shown above)
# Report as:
# "Recurrent CNVs included chr7 gain (85% of aneuploid cells) and
#  chr10 loss (72% of aneuploid cells), consistent with glioblastoma
#  genomic signatures."
```

---

**Next Steps**:
- [08_BEGINNER_TUTORIAL.md](08_BEGINNER_TUTORIAL.md) - Complete walkthrough
- [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) - If results look unexpected
- [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md) - Understanding the algorithm
