# CopyKAT Algorithm Explained: A Deep Dive

## Table of Contents
1. [Introduction](#introduction)
2. [Algorithm Overview](#algorithm-overview)
3. [Step 1: Input and Preprocessing](#step-1-input-and-preprocessing)
4. [Step 2: Freeman-Tukey Transformation](#step-2-freeman-tukey-transformation)
5. [Step 3: Polynomial Dynamic Linear Model (DLM)](#step-3-polynomial-dynamic-linear-model-dlm)
6. [Step 4: Baseline Estimation](#step-4-baseline-estimation)
7. [Step 5: CNV Profile Inference](#step-5-cnv-profile-inference)
8. [Step 6: Bayesian Segmentation](#step-6-bayesian-segmentation)
9. [Step 7: Aneuploid vs Diploid Classification](#step-7-aneuploid-vs-diploid-classification)
10. [Step 8: Clonal Architecture](#step-8-clonal-architecture)
11. [Complete Example Walkthrough](#complete-example-walkthrough)
12. [Mathematical Foundations](#mathematical-foundations)

---

## Introduction

This document provides a detailed technical explanation of how CopyKAT infers copy number variations from single-cell RNA-seq data. We'll walk through each algorithmic step with:
- Clear explanations of what happens to your data
- Mathematical foundations (accessible to beginners)
- Visual examples
- Why each step matters

By the end, you'll understand exactly what CopyKAT does under the hood and why it works.

---

## Algorithm Overview

### The Pipeline at a Glance

```
Raw Expression Matrix (genes × cells)
         ↓
    [STEP 1: Quality Filtering]
         ↓
    [STEP 2: Freeman-Tukey Transformation]
         ↓
    [STEP 3: Chromosomal Smoothing (DLM)]
         ↓
    [STEP 4: Identify Diploid Baseline]
         ↓
    [STEP 5: Calculate CNV Profiles]
         ↓
    [STEP 6: Genome Segmentation]
         ↓
    [STEP 7: Cell Classification]
         ↓
    [STEP 8: Subclone Detection]
         ↓
Outputs: Heatmap + Classifications + CNV Matrix
```

### Key Innovation

CopyKAT's breakthrough is **automatic baseline detection**. Unlike tools that require you to specify which cells are normal, CopyKAT:
1. Clusters all cells
2. Finds the cluster with **lowest variance** (= most genomically stable)
3. Uses that cluster as the diploid reference

**Why this works**: Normal cells have consistent 2N copy number across the genome, so they show minimal variance. Cancer cells with varied CNVs show high variance.

---

## Step 1: Input and Preprocessing

### What Happens

CopyKAT receives your expression matrix and performs quality control to ensure reliable CNV inference.

### Input Format

```
Gene Expression Matrix:
                Cell_1   Cell_2   Cell_3   ...   Cell_N
Gene_1 (chr1)     23       45       12            67
Gene_2 (chr1)     11       33       8             42
Gene_3 (chr2)     67       12       45            23
...
Gene_M (chr22)    34       56       23            89
```

**Requirements**:
- Genes annotated with chromosomal coordinates
- Genes ordered by chromosome and position
- Expression as raw UMI counts or normalized values

### Quality Filtering

**Cell-level filtering**:
```r
# Remove cells with too few genes detected
min_genes <- param$ngene.chr * 23  # ngene.chr × chromosomes
cells_pass <- colSums(rawmat > 0) >= min_genes
```

**Example**: If `ngene.chr=5` and genome is human (23 chrs):
- Minimum genes per cell: 5 × 23 = 115 genes
- Cells with <115 detected genes are removed

**Why**: Cells with very low gene detection are likely:
- Dead/dying cells
- Empty droplets
- Technical failures

**Gene-level filtering**:
```r
# Remove genes expressed in very few cells
detection_rate <- rowSums(rawmat > 0) / ncol(rawmat)
genes_pass <- detection_rate >= param$LOW.DR
```

**Example**: If `LOW.DR=0.05`:
- Gene must be detected in ≥5% of cells
- If you have 1000 cells, gene needs ≥50 cells expressing it

**Why**: Genes detected in very few cells:
- Contribute mostly noise
- Make smooth patterns hard to detect
- Increase computational burden

### Chromosome Annotation

CopyKAT maps each gene to its genomic position:

```r
# Example annotation
Gene      Chromosome   Start       End
EGFR      chr7         55019017    55211628
TP53      chr17        7661779     7687550
MYC       chr8         127735434   127742951
```

This enables:
- Ordering genes by chromosomal position
- Detecting regional CNV patterns
- Identifying breakpoints

### Output of Step 1

```
Filtered Matrix:
- M' genes (passed detection threshold)
- N' cells (passed quality threshold)
- Gene coordinates attached
- Ready for transformation
```

**Typical filtering results**:
- Start: 20,000 genes, 3,000 cells
- After filtering: 15,000 genes, 2,850 cells
- ~75-95% retention (normal for good quality data)

---

## Step 2: Freeman-Tukey Transformation

### The Problem: Heteroscedasticity

scRNA-seq data has **unequal variance** across expression levels:

```
Low expression genes:  variance ≈ mean (Poisson-like)
High expression genes: variance > mean (overdispersed)
```

**Why this matters**: Statistical methods assume equal variance. Without correction:
- High expression genes dominate
- Low expression genes ignored
- CNV signal obscured

### The Solution: Freeman-Tukey Transformation

**Mathematical formula**:
```
FTT(x) = √x + √(x+1)
```

Where `x` is the gene expression count.

### How It Works

**Example transformation**:

| Raw Count (x) | FTT(x) = √x + √(x+1) |
|---------------|----------------------|
| 0 | 0 + 1 = 1.00 |
| 1 | 1 + 1.41 = 2.41 |
| 4 | 2 + 2.24 = 4.24 |
| 9 | 3 + 3.16 = 6.16 |
| 16 | 4 + 4.12 = 8.12 |
| 100 | 10 + 10.05 = 20.05 |

**Effect on variance**:
```
Before FTT:
Gene A (low expr):  mean=2,  variance=3   (CV=86%)
Gene B (high expr): mean=100, variance=400 (CV=20%)

After FTT:
Gene A: mean=3.15, variance=0.5  (CV=22%)
Gene B: mean=20.01, variance=0.6 (CV=12%)
```

**Result**: Variance is now more uniform across expression levels.

### Visual Example

```
Before FTT:                    After FTT:
Expression                     Transformed

High ●●●●●●●●●                High ●●●●●
     (huge variance)                (moderate variance)

Low  ●●                        Low  ●●●
     (tiny variance)                (moderate variance)
```

### Why CopyKAT Uses This

1. **Stabilizes variance**: Makes genes comparable
2. **Handles zeros**: √0 = 0 (no special case needed)
3. **Maintains order**: Monotonic transformation
4. **Bayesian compatibility**: Better for downstream GMM

### Implementation in CopyKAT

```r
# Simplified version
transformed_matrix <- sqrt(raw_matrix) + sqrt(raw_matrix + 1)
```

Applied to every gene in every cell.

---

## Step 3: Polynomial Dynamic Linear Model (DLM)

### The Problem: Cell-to-Cell Stochasticity

Even for the same cell type with same CNV, expression varies:

```
Cell 1 (cancer):  Gene1=45, Gene2=67, Gene3=23, Gene4=89
Cell 2 (cancer):  Gene1=52, Gene2=71, Gene3=19, Gene4=95
                  (same CNV, different expression due to noise)
```

**Sources of noise**:
- Transcriptional bursting
- Cell cycle effects
- Technical variability
- Sampling (UMI capture)

### The Solution: Chromosomal Smoothing

CopyKAT uses a **Dynamic Linear Model (DLM)** to smooth expression along each chromosome.

**Intuition**: If chromosome 7 is amplified, **all genes on chr7** should show increased expression. Smooth out individual gene fluctuations to reveal the underlying CNV pattern.

### How DLM Works

**Polynomial model**: Expression level follows a smooth polynomial trend along chromosome position.

**For each cell, for each chromosome**:
1. Order genes by chromosomal position
2. Fit a smooth curve through expression values
3. Replace raw values with smoothed trend

### Visual Example

```
Chromosome 7 (raw expression):

Expression
  |     ●
  |   ●   ●        ●
  |  ●  ●   ●    ●  ●
  | ●      ●  ● ●     ●
  |________________________ Position
  Start                 End

After DLM smoothing:

Expression
  |        _______________
  |    ___/
  |  _/
  | /
  |________________________ Position
  Start                 End

  Clear amplification pattern emerges
```

### Mathematical Foundation

**Dynamic Linear Model**:
```
y_t = F_t × θ_t + v_t   (observation equation)
θ_t = G_t × θ_{t-1} + w_t   (state equation)
```

Where:
- `y_t` = expression at position t
- `θ_t` = underlying CNV state at position t
- `v_t`, `w_t` = noise terms

**In plain English**:
- Observed expression = true CNV state + noise
- CNV state changes smoothly along chromosome
- Model separates signal from noise

### Parameters Involved

**`win.size`**: Number of genes per smoothing window
- Small (10-15): More detail, more noise
- Large (50-100): Smoother, may miss focal CNVs
- Default (25): Good balance

**Example with win.size=25**:
```
Chromosome with 1000 genes:
- Divide into ~40 windows of 25 genes each
- Smooth expression within each window
- Result: 40 CNV state estimates along chromosome
```

### Why This Step Matters

**Before smoothing**:
```
Gene expression on chr7:
45, 12, 67, 23, 89, 34, 56, 19, ...
(Hard to see pattern)
```

**After smoothing**:
```
Smoothed CNV signal:
Normal(2.0) → Normal(2.0) → Amplified(3.5) → Amplified(3.5) → ...
(Clear CNV pattern)
```

---

## Step 4: Baseline Estimation

### The Challenge

To detect CNVs, we need a **reference**: what does normal (diploid, 2N) look like?

**Problem**: In a tumor sample, we don't know which cells are normal!

### CopyKAT's Innovation

**Key insight**: Normal cells have **low variance** in CNV profiles.

**Why**:
- Normal cells: All chromosomes = 2N → flat profile → low variance
- Cancer cells: Mixed amplifications/deletions → variable profile → high variance

### The Algorithm

**Step 4a: Hierarchical Clustering**

Cluster all cells based on smoothed expression:

```r
# Simplified
distance_matrix <- dist(smoothed_data, method="euclidean")
clusters <- hclust(distance_matrix)
```

**Result**: Cells grouped by similarity

```
Cluster 1: 150 cells (immune cells)
Cluster 2: 300 cells (cancer subclone A)
Cluster 3: 100 cells (fibroblasts)
Cluster 4: 250 cells (cancer subclone B)
```

**Step 4b: Variance Estimation with GMM**

For each cluster, estimate variance using **Gaussian Mixture Model**:

```r
# For each cluster
for (cluster in clusters) {
  # Fit GMM to CNV values (3 components: gain, neutral, loss)
  gmm <- fit_gaussian_mixture(cluster_data, n_components=3)

  # Calculate variance of "neutral" component
  variance[cluster] <- var(gmm$neutral_component)
}
```

**GMM with 3 components**:
```
Component 1: Deletions (CN < 2)
Component 2: Neutral   (CN ≈ 2)  ← We want this
Component 3: Amplifications (CN > 2)
```

**Step 4c: Select Diploid Baseline**

```r
# Find cluster with lowest variance
diploid_cluster <- clusters[which.min(variance)]
baseline_cells <- cells_in(diploid_cluster)
```

**Example results**:

| Cluster | # Cells | Variance | Classification |
|---------|---------|----------|----------------|
| 1 | 150 | 0.05 | **Diploid (Baseline)** ← Lowest variance |
| 2 | 300 | 0.45 | Aneuploid |
| 3 | 100 | 0.08 | Diploid |
| 4 | 250 | 0.52 | Aneuploid |

**Baseline = Cluster 1** (lowest variance = most stable = diploid)

### Alternative: GMM Definition Mode

For challenging datasets (very few normal cells), CopyKAT has a stricter mode:

**Criteria for "confident diploid"**:
```
If ≥99% of a cell's genes fall in "neutral" GMM component:
  → Cell is confident diploid
```

**Example**:
```
Cell A: 98.5% neutral, 1.0% gain, 0.5% loss  → Diploid
Cell B: 85% neutral, 10% gain, 5% loss       → Not confident
```

### Why This Works

**Normal cells** (diploid):
```
Chr1: 2N ████████████
Chr2: 2N ████████████
Chr3: 2N ████████████
...
(All chromosomes flat → low variance)
```

**Cancer cells** (aneuploid):
```
Chr1: 4N ████████████████████
Chr2: 1N ████
Chr3: 3N ████████████████
...
(Variable CNVs → high variance)
```

CopyKAT finds the flat, low-variance group = diploid baseline.

---

## Step 5: CNV Profile Inference

### Goal

For each cell, estimate copy number across the genome by comparing to the diploid baseline.

### The Process

**Step 5a: Calculate Baseline Profile**

Average the smoothed expression across all diploid cells:

```r
baseline_profile <- rowMeans(diploid_cells_smoothed)
```

This gives the "normal" expression level for each genomic region.

**Example**:
```
Genomic Region      Baseline Expression
chr1:1-220kb        150
chr1:220kb-440kb    145
chr2:1-220kb        200
chr2:220kb-440kb    190
...
```

**Step 5b: Compute Relative Expression**

For each cell, divide its expression by the baseline:

```r
cnv_profile <- cell_expression / baseline_profile
```

**Example for Cell_123**:

| Region | Cell Expr | Baseline | Ratio (CNV) | Interpretation |
|--------|-----------|----------|-------------|----------------|
| chr1:1-220kb | 300 | 150 | 2.0 | Normal (2N) |
| chr1:220kb-440kb | 290 | 145 | 2.0 | Normal (2N) |
| chr7:1-220kb | 600 | 200 | 3.0 | Amplification (3N) |
| chr10:1-220kb | 95 | 190 | 0.5 | Deletion (1N) |

**Step 5c: Discretize Copy Number**

Convert ratios to integer copy numbers:

```r
Copy Number = round(ratio × 2)
```

| Ratio | Inferred CN | Biological State |
|-------|-------------|------------------|
| 0.0-0.25 | 0 | Homozygous deletion |
| 0.25-0.75 | 1 | Heterozygous loss |
| 0.75-1.25 | 2 | Normal (diploid) |
| 1.25-1.75 | 3 | Single copy gain |
| 1.75-2.5 | 4 | Amplification |
| >2.5 | 5+ | High-level amplification |

### Visual Example

```
Cell CNV Profile:

Copy Number
  5 |                        ████
  4 |         ████           ████
  3 |         ████  ████     ████
  2 |  ████   ████  ████  ████████  ████
  1 |  ████   ████  ████  ████████  ████  ██
  0 |______________________________________|____
     Chr1  Chr2  Chr7  Chr9  Chr10 Chr13 Chr17

Interpretation:
- Chr1: Normal (2N)
- Chr2: Deleted (1N)
- Chr7: Amplified (4N)
- Chr9: Normal (2N)
- Chr10: Amplified (3N)
- Chr13: Normal (2N)
- Chr17: Deleted (1N)
```

### Output of Step 5

**CNV Matrix** (regions × cells):

```
                Cell_1  Cell_2  Cell_3  ...
chr1:1-220kb    2.0     2.0     3.5     ...
chr1:220kb-440kb 2.0    2.0     3.5     ...
chr7:1-220kb    4.0     2.0     4.0     ...
chr10:1-220kb   1.0     2.0     1.0     ...
```

This matrix captures genome-wide CNV landscape for every cell.

---

## Step 6: Bayesian Segmentation

### The Goal

Identify **breakpoints** where copy number changes along chromosomes.

### Why Segmentation Matters

Raw CNV profiles are noisy:

```
Chromosome 7:
2.1, 2.0, 3.8, 4.1, 3.9, 4.0, 3.8, 4.2, 4.0, ...

Segmented:
[2.0, 2.0] → BREAKPOINT → [4.0, 4.0, 4.0, 4.0, ...]
```

**Segments** = contiguous regions with same copy number.

### The Algorithm

CopyKAT uses **hierarchical Bayesian segmentation** with the **Kolmogorov-Smirnov (KS) test**.

**Step 6a: KS Test for Breakpoints**

For each potential breakpoint position, test if left and right sides differ:

```r
# Test if segments differ
ks_statistic <- ks.test(left_segment, right_segment)

if (ks_statistic > threshold) {
  # Significant difference → breakpoint
} else {
  # Merge segments
}
```

**`KS.cut` parameter** controls threshold:
- `KS.cut = 0.1` (default): Moderate sensitivity
- `KS.cut = 0.05`: High sensitivity (more breakpoints)
- `KS.cut = 0.3`: Low sensitivity (fewer breakpoints)

**Example**:

```
Raw CNV values along chr7:
2.0, 2.1, 2.0, 4.1, 3.9, 4.0, 4.2, 3.8, 2.0, 1.9

Position 3-4 test:
Left:  [2.0, 2.1, 2.0]  mean=2.03
Right: [4.1, 3.9, 4.0]  mean=4.0
KS statistic = 1.0 (p < 0.001)
→ BREAKPOINT detected

Result:
Segment 1: positions 1-3, CN=2
Segment 2: positions 4-8, CN=4
Segment 3: positions 9-10, CN=2
```

**Step 6b: Merge Similar Segments**

Adjacent segments with similar CN are merged:

```r
if (abs(segment_i_mean - segment_j_mean) < threshold) {
  merge(segment_i, segment_j)
}
```

**Example**:
```
Before merging:
Seg1: CN=2.0
Seg2: CN=2.1  ← Similar to Seg1
Seg3: CN=4.0

After merging:
Seg1+2: CN=2.05
Seg3: CN=4.0
```

### Visual Segmentation Example

```
Before Segmentation:
CN
5 |     ● ●●●  ●●●●
4 |   ●●● ● ●●●  ●●●
3 |  ●  ●● ●  ● ●  ●
2 | ● ● ●  ●● ●  ●●  ●
1 |____________________
   Chr7 position →

After Segmentation:
CN
5 |
4 |   ████████████████
3 |
2 | ████          ████
1 |____________________
   Chr7 position →

Segments identified:
- 1-5kb: CN=2
- 5-15kb: CN=4 (AMPLIFICATION)
- 15-20kb: CN=2
```

### Parameters Affecting Segmentation

| Parameter | Effect |
|-----------|--------|
| `win.size` | Larger → smoother segments |
| `KS.cut` | Lower → more breakpoints |
| `ngene.chr` | Minimum genes for reliable segmentation |

### Output of Step 6

**Segmented CNV Profile**:

```
Cell_123:
chr1: [1-50Mb: CN=2] [50-120Mb: CN=2] [120-249Mb: CN=2]
chr7: [1-55Mb: CN=2] [55-100Mb: CN=4] [100-159Mb: CN=2]
chr10: [1-135Mb: CN=1]
```

Clean, interpretable CNV karyotype for each cell.

---

## Step 7: Aneuploid vs Diploid Classification

### Goal

Classify each cell as:
- **Diploid**: Normal, CN ≈ 2 across genome
- **Aneuploid**: Cancer, significant CNV deviations

### The Decision Process

**Step 7a: Calculate Genome-wide CNV Burden**

For each cell, measure how much it deviates from diploid:

```r
cnv_burden <- sum(abs(cnv_profile - 2)) / genome_size
```

**Example**:
```
Cell A:
chr1-22: all CN=2  → burden = 0
Cell A is diploid

Cell B:
chr7: CN=4 (50Mb region)  → deviation = 2 × 50Mb = 100
chr10: CN=1 (135Mb region) → deviation = 1 × 135Mb = 135
Total deviation = 235Mb
Burden = 235 / 3000 (genome size) = 0.078
Cell B is aneuploid
```

**Step 7b: Clustering-Based Classification**

CopyKAT also uses hierarchical clustering on CNV profiles:

```r
# Cluster cells by CNV similarity
cnv_clusters <- hclust(dist(cnv_profiles))

# Clusters with high CNV burden → aneuploid
# Clusters with low CNV burden → diploid
```

**Step 7c: Confidence Scoring**

Each classification gets a confidence score:

```r
confidence <- bootstrapping_stability(cell, n_iterations=100)
```

- High confidence (>0.9): Clear, consistent classification
- Medium confidence (0.7-0.9): Likely correct
- Low confidence (<0.7): Uncertain, borderline case

### Classification Examples

**Cell 1 (Clear Diploid)**:
```
CNV Profile: Chr1-22 all CN≈2
Burden: 0.01
Cluster: Diploid group
Confidence: 0.98
→ Classification: diploid (high confidence)
```

**Cell 2 (Clear Aneuploid)**:
```
CNV Profile: Chr7(CN=4), Chr10(CN=1), Chr13(CN=3)
Burden: 0.15
Cluster: Aneuploid group
Confidence: 0.95
→ Classification: aneuploid (high confidence)
```

**Cell 3 (Borderline)**:
```
CNV Profile: Mostly CN=2, small chr7 gain
Burden: 0.04
Cluster: Mixed
Confidence: 0.65
→ Classification: diploid (low confidence)
WARNING: Manual review recommended
```

### Output of Step 7

**Prediction Table**:
```
cell_name         copykat.pred  copykat.confidence
Cell_1            diploid       0.98
Cell_2            aneuploid     0.95
Cell_3            diploid       0.65
Cell_4            aneuploid     0.92
...
```

---

## Step 8: Clonal Architecture

### Goal

Among aneuploid cells, identify **subclones** (tumor subpopulations with shared CNV patterns).

### The Process

**Step 8a: Cluster Aneuploid Cells**

```r
# Take only aneuploid cells
aneuploid_cells <- cells[classification == "aneuploid"]

# Cluster by CNV profile similarity
subclones <- hclust(dist(aneuploid_cnv_profiles))
```

**Step 8b: Identify Distinct Subclones**

Cut the dendrogram to define groups:

```r
subclone_groups <- cutree(subclones, h=height_threshold)
```

### Example: Subclone Structure

```
Tumor with 500 aneuploid cells:

Subclone A (200 cells):
- chr7 amplification
- chr10 deletion
- Likely dominant clone

Subclone B (150 cells):
- chr7 amplification
- chr10 deletion
- chr13 amplification ← Additional event
- Likely evolved from Subclone A

Subclone C (100 cells):
- chr7 amplification
- chr10 deletion
- chr17 deletion ← Different additional event
- Parallel evolution from Subclone A

Subclone D (50 cells):
- chr1 amplification
- chr6 deletion
- Independent origin
```

### Evolutionary Tree

```
        [Diploid Ancestor]
               |
          [Founding clone]
       chr7+, chr10-
               |
      ╔════════╬════════╗
      ↓        ↓        ↓
  Subclone A  Subclone B  Subclone C
  (200)       +chr13      +chr17
              (150)       (100)
```

### Why This Matters

**Clinical implications**:
- Subclone diversity → treatment resistance
- Dominant clone → likely therapy target
- Rare subclones → potential resistant reservoirs

**Research insights**:
- Tumor evolution dynamics
- Driver event timing
- Metastatic seeding patterns

---

## Complete Example Walkthrough

Let's trace a single cell through the entire pipeline.

### Input: Cell_123 from Glioblastoma Sample

**Raw expression** (5 example genes):

| Gene | Chr | Raw Count | Cell_123 |
|------|-----|-----------|----------|
| EGFR | chr7 | 450 | (chr7 amplified) |
| PTEN | chr10 | 15 | (chr10 deleted) |
| TP53 | chr17 | 120 | (normal) |
| GAPDH | chr12 | 300 | (normal) |
| ACTB | chr7 | 480 | (chr7 amplified) |

### Step 1: Filtering
- Cell_123 has 4,500 genes detected ✓
- Passes quality filter (threshold = 115 genes)

### Step 2: FTT Transformation

| Gene | Raw | FTT |
|------|-----|-----|
| EGFR | 450 | 21.21 + 21.23 = 42.44 |
| PTEN | 15 | 3.87 + 4.00 = 7.87 |
| TP53 | 120 | 10.95 + 11.00 = 21.95 |

### Step 3: DLM Smoothing

```
Chr7 genes (EGFR, ACTB, etc.):
Raw:      450, 480, 420, 510, 390, ...
Smoothed: 470, 470, 470, 470, 470, ...
(Amplification pattern emerges)

Chr10 genes (PTEN, etc.):
Raw:      15, 18, 12, 20, 14, ...
Smoothed: 16, 16, 16, 16, 16, ...
(Deletion pattern emerges)
```

### Step 4: Baseline Estimation

```
All cells clustered:
- Cluster 1 (normal astrocytes): variance = 0.05 ← BASELINE
- Cluster 2 (GBM cells): variance = 0.45
- Cluster 3 (immune cells): variance = 0.08

Cell_123 is in Cluster 2 (high variance)
```

### Step 5: CNV Inference

```
Baseline expression (Cluster 1 average):
chr7 region: 200
chr10 region: 150

Cell_123 ratios:
chr7: 470 / 200 = 2.35 → CN = 2.35 × 2 ≈ 5 (amplification!)
chr10: 16 / 150 = 0.11 → CN = 0.11 × 2 ≈ 0 (deletion!)
```

### Step 6: Segmentation

```
Chr7: [1-55Mb: CN=2] [55-100Mb: CN=5] [100-159Mb: CN=2]
Chr10: [1-135Mb: CN=0]

Breakpoint at chr7:55Mb detected (KS test p<0.001)
```

### Step 7: Classification

```
CNV burden = (chr7:45Mb × 3) + (chr10:135Mb × 2) = 405Mb
Burden ratio = 405 / 3000 = 0.135 (high!)
→ Classification: ANEUPLOID
→ Confidence: 0.95
```

### Step 8: Subclone Assignment

```
Cell_123 clusters with 200 other cells sharing:
- chr7 amplification
- chr10 deletion
→ Assigned to Subclone A
```

### Final Output for Cell_123

```
Prediction:
  cell.name: Cell_123
  copykat.pred: aneuploid
  copykat.confidence: 0.95
  subclone: A

CNV Profile:
  chr7:55-100Mb: CN=5 (AMPLIFICATION)
  chr10:1-135Mb: CN=0 (HOMOZYGOUS DELETION)
  (other chromosomes: CN=2)
```

---

## Mathematical Foundations

### Freeman-Tukey Transformation

**Derivation**:

Variance of count data follows:
```
Var(X) ≈ E(X)  (Poisson)
```

We want constant variance. The FTT achieves this:
```
FTT(x) = √x + √(x+1)

Var(FTT(X)) ≈ constant
```

**Why it works**: The square root transformation reduces variance of large values more than small values, equalizing them.

### Dynamic Linear Model

**State-space formulation**:
```
y_t = F_t θ_t + v_t,  v_t ~ N(0, V)   (observation)
θ_t = G_t θ_{t-1} + w_t,  w_t ~ N(0, W)   (evolution)
```

**Filtering (Kalman)**:
```
Prediction: θ_{t|t-1} = G_t θ_{t-1|t-1}
Update: θ_{t|t} = θ_{t|t-1} + K_t (y_t - F_t θ_{t|t-1})
```

Where K_t is the Kalman gain.

### Gaussian Mixture Model

**3-component GMM**:
```
p(x) = π_1 N(μ_1, σ_1²) + π_2 N(μ_2, σ_2²) + π_3 N(μ_3, σ_3²)

Where:
Component 1: Deletions (μ_1 < 2)
Component 2: Neutral (μ_2 ≈ 2)
Component 3: Amplifications (μ_3 > 2)

Constraints: π_1 + π_2 + π_3 = 1
```

**EM algorithm** fits parameters by iteratively:
1. E-step: Assign genes to components
2. M-step: Update component parameters

### Kolmogorov-Smirnov Test

**Test statistic**:
```
D = sup_x |F_1(x) - F_2(x)|
```

Where F_1, F_2 are empirical CDFs of left and right segments.

**Null hypothesis**: Segments drawn from same distribution

**p-value**: Probability of observing D under null

**Decision**: If p < KS.cut, reject null → breakpoint

---

**Next**: [03_PARAMETERS_REFERENCE.md](03_PARAMETERS_REFERENCE.md) - Detailed guide to all parameters

**See Also**:
- [01_COPYKAT_OVERVIEW.md](01_COPYKAT_OVERVIEW.md) - High-level introduction
- [08_BEGINNER_TUTORIAL.md](08_BEGINNER_TUTORIAL.md) - Hands-on walkthrough
- [GLOSSARY.md](GLOSSARY.md) - Technical terms explained
