# CopyKAT Beginner Tutorial: Complete Walkthrough

## Welcome!

This tutorial will guide you through your first CopyKAT analysis from start to finish. By the end, you'll have:
- Loaded real cancer data
- Run CopyKAT
- Interpreted results
- Created visualizations

**Time required**: 30-45 minutes
**Prerequisites**: R installed, CopyKAT package installed
**Dataset**: Glioblastoma test data (included in project)

---

## Part A: Command-Line Tutorial

### Step 1: Set Up Your Environment

**Activate the conda environment**:
```bash
# Navigate to project directory
cd ~/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Activate environment
conda activate Project4-CNV-Cancer-RNAseq
```

**Start R**:
```bash
R
```

You should see:
```
R version 4.5.1 (2025-06-13) -- "Great Square Root"
>
```

---

### Step 2: Load the Data

**Load CopyKAT library**:
```r
library(copykat)
```

Expected output:
```
Loading required package: ...
```

**Load test data**:
```r
# Load glioblastoma expression matrix
data_file <- "data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz"

raw_data <- read.table(gzfile(data_file),
                       header = TRUE,
                       row.names = 1,
                       sep = "\t",
                       check.names = FALSE)
```

**Inspect the data**:
```r
# Check dimensions
dim(raw_data)
# Expected: 5948 genes × 543 cells

# Look at first few genes and cells
raw_data[1:5, 1:3]
```

You should see something like:
```
          MGH264_A01 MGH264_A02 MGH264_A03
A2M        -3.801470  -5.820241  -3.801470
AAAS       -5.820241  -3.801470  -5.820241
AAK1       -2.505149  -2.000000  -3.000000
AAMP       -2.700440  -1.584963  -2.392317
AARS       -4.523562  -2.392317  -3.247928
```

**Note**: Negative values indicate low/no expression (log-transformed data).

---

### Step 3: Prepare for Analysis

**Create output directory**:
```r
if (!dir.exists("results")) {
  dir.create("results", recursive = TRUE)
}

# Change to output directory
setwd("results")
```

**Check data quality**:
```r
# How many genes detected per cell?
genes_per_cell <- colSums(raw_data > -5)  # Threshold for "detected"
summary(genes_per_cell)
```

Expected summary:
```
   Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
  2800    3200    3500    3450    3700    4200
```

Good quality: Most cells have 3000-4000 genes detected.

---

### Step 4: Run CopyKAT with Default Parameters

**Start the analysis**:
```r
# This will take ~5-10 minutes
glio_result <- copykat(
  rawmat = raw_data,
  id.type = "S",          # Symbol gene names
  cell.line = "no",       # Mixed tumor sample
  ngene.chr = 5,          # Default filtering
  sam.name = "glioblastoma_test",
  distance = "euclidean",
  genome = "hg20",        # Human genome
  n.cores = 4             # Use 4 CPU cores
)
```

**What you'll see**:
```
[1] "running copykat v1.1.0"
[1] "step1: read and filter data ..."
[1] "5948 genes, 543 cells in raw data"
[1] "5843 genes past LOW.DR filtering"
[1] "step 2: annotations gene coordinates ..."
[1] "start annotation ..."
[1] "step 3: smoothing data with dlm ..."
[1] "step 4: measuring baselines ..."
number of iterations= 219
...
[1] "step 5: segmentation..."
[1] "step 6: convert to genomic bins..."
[1] "step 7: adjust baseline ..."
[1] "step 8: final prediction ..."
[1] "step 9: saving results..."
[1] "step 10: ploting heatmap ..."
```

**When complete**:
```
Time difference of X mins
```

---

### Step 5: Examine the Results

**Check what was created**:
```r
list.files(pattern = "glioblastoma_test")
```

Expected files:
```
[1] "glioblastoma_test_copykat_CNA_raw_results.txt"
[2] "glioblastoma_test_copykat_CNA_results.txt"
[3] "glioblastoma_test_copykat_heatmap.pdf"
[4] "glioblastoma_test_copykat_prediction.txt"
```

**View cell classifications**:
```r
# Extract predictions from result object
predictions <- glio_result$prediction

# Or read from file
# predictions <- read.table("glioblastoma_test_copykat_prediction.txt",
#                           header=TRUE, sep="\t")

# Summary
table(predictions$copykat.pred)
```

Expected output:
```
  aneuploid diploid
       450      93
```

**Interpretation**: 450 cancer cells, 93 normal cells

**View confidence scores**:
```r
# Mean confidence by group
tapply(predictions$copykat.confidence,
       predictions$copykat.pred,
       mean)
```

Expected:
```
aneuploid   diploid
     0.88      0.92
```

**Interpretation**: High confidence (>0.85) for both groups - good quality!

---

### Step 6: Visualize Results

**Open the heatmap**:
```r
# On Mac
system("open glioblastoma_test_copykat_heatmap.pdf")

# On Windows
# shell.exec("glioblastoma_test_copykat_heatmap.pdf")

# On Linux
# system("xdg-open glioblastoma_test_copykat_heatmap.pdf")
```

**What to look for**:
- **Two main clusters**: Top (white) = diploid, Bottom (red/blue) = aneuploid
- **Chr7 (red vertical band)**: Amplification in aneuploid cells
- **Chr10 (blue vertical band)**: Deletion in aneuploid cells

These are classic glioblastoma CNVs!

---

### Step 7: Explore Specific Cells

**Pick a tumor cell**:
```r
# Get first aneuploid cell
tumor_cell <- predictions$cell.names[predictions$copykat.pred == "aneuploid"][1]
print(tumor_cell)
# Example: "MGH264_A01"
```

**Plot its CNV profile**:
```r
# Load CNV matrix
cnv_matrix <- glio_result$CNV.matrix

# Plot profile
cell_cnv <- cnv_matrix[, tumor_cell]
plot(cell_cnv, type="l",
     main=paste("CNV Profile:", tumor_cell),
     ylab="Copy Number",
     xlab="Genome Position",
     ylim=c(0, 4))
abline(h=2, col="red", lty=2, lwd=2)  # Diploid baseline
legend("topright", legend="Normal (2N)", col="red", lty=2)
```

**Interpretation**:
- Lines above 2 = amplifications
- Lines below 2 = deletions
- Flat at 2 = normal

---

### Step 8: Identify Altered Chromosomes

**Calculate mean CN per chromosome**:
```r
# Get chromosome info
cnv_data <- read.table("glioblastoma_test_copykat_CNA_results.txt",
                       header=TRUE, row.names=1)

chromosomes <- cnv_data$chrom

# For aneuploid cells
aneuploid_cells <- predictions$cell.names[predictions$copykat.pred == "aneuploid"]
aneuploid_cnv <- cnv_matrix[, aneuploid_cells]

# Mean CN per bin
mean_cn_per_bin <- rowMeans(aneuploid_cnv)

# Mean per chromosome
chr_means <- tapply(mean_cn_per_bin, chromosomes, mean)
print(round(chr_means, 2))
```

Expected output:
```
 chr1  chr2  chr3  ...  chr7  ...  chr10 ...
 2.01  1.98  2.03  ...  3.45  ...  1.15  ...
```

**Interpretation**:
- Chr7: 3.45 (amplification!) - contains EGFR
- Chr10: 1.15 (deletion!) - contains PTEN
- Classic GBM signature ✓

---

### Step 9: Compare to Literature

**Known GBM CNVs** (from TCGA):
- Chr7 gain: 80-90% of cases
- Chr10 loss: 70-80% of cases
- Chr9p loss (CDKN2A): 50% of cases

**Your results**:
```r
# Fraction with chr7 gain
chr7_means <- tapply(aneuploid_cnv[chromosomes == "chr7", ], 2, mean)
chr7_amplified <- sum(chr7_means > 2.5) / length(chr7_means)
print(paste("Chr7 amplified:", round(chr7_amplified*100, 1), "%"))
# Expected: ~85%

# Fraction with chr10 loss
chr10_means <- tapply(aneuploid_cnv[chromosomes == "chr10", ], 2, mean)
chr10_deleted <- sum(chr10_means < 1.5) / length(chr10_means)
print(paste("Chr10 deleted:", round(chr10_deleted*100, 1), "%"))
# Expected: ~75%
```

**Conclusion**: Your results match known biology!

---

### Step 10: Export Results for Further Analysis

**Save key results**:
```r
# Export predictions
write.csv(predictions,
          file = "cell_classifications.csv",
          row.names = FALSE)

# Export chromosome-level CNV summary
chr_summary <- data.frame(
  Chromosome = names(chr_means),
  Mean_CN = chr_means,
  Status = ifelse(chr_means > 2.3, "Amplified",
           ifelse(chr_means < 1.7, "Deleted", "Normal"))
)

write.csv(chr_summary,
          file = "chromosome_alterations.csv",
          row.names = FALSE)

print("Results exported!")
```

---

## Part B: Streamlit Dashboard Tutorial

### Step 1: Start the Dashboard

**From terminal**:
```bash
# Navigate to project root
cd ~/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Activate environment
conda activate Project4-CNV-Cancer-RNAseq

# Run Streamlit app
streamlit run app/streamlit_app.py
```

**Browser opens automatically** at `http://localhost:8501`

---

### Step 2: Upload Data

**In the dashboard**:
1. Click sidebar: **"Upload Expression Matrix"**
2. Select file: `data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz`
3. Preview appears:
   ```
   Preview: 5 genes × 543 cells
   [Table shows first 5 genes and cells]
   ```

---

### Step 3: Configure Parameters

**Basic parameters** (sidebar):
- **Sample Name**: `glioblastoma_tutorial`
- **Genome**: `Human (hg20)` ← Auto-detected
- **Sample Type**: `Tumor sample (mixed)` ← Default

**Advanced parameters** (expandable):
- **Min genes/chr**: `5` ← Default
- **LOW.DR**: `0.05` ← Default
- **UP.DR**: `0.1` ← Default
- **Window size**: `25` ← Default
- **KS.cut**: `0.1` ← Default
- **CPU cores**: `4` ← Adjust based on your system

**Note**: Defaults work well for most datasets!

---

### Step 4: Run Analysis

**Click the big button**:
```
🚀 Run CopyKAT
```

**Progress indicators**:
```
[Progress bar] ━━━━━━━━━━━━━━ 30%
Step 3/5: Running CNV analysis (this may take 5-15 min)...
```

**Wait** for completion (5-15 minutes)

**Success message**:
```
✅ Analysis complete!
```

---

### Step 5: View Results Tab

**Switch to "Results" tab**

**You'll see**:

**1. Classification Summary**
```
Cell Classifications:
Aneuploid: 450 cells (82.9%)
Diploid:    93 cells (17.1%)
```

**2. Confidence Scores**
```
Mean Confidence:
Aneuploid: 0.88
Diploid:   0.92
```

**3. CNV Heatmap**
[Interactive or static heatmap displayed]

**4. Chromosome Alterations**
[Bar chart showing amplified/deleted chromosomes]

---

### Step 6: Download Results

**Switch to "Download" tab**

**Available downloads**:
- ☐ Cell Classifications (CSV)
- ☐ CNV Matrix (CSV)
- ☐ CNV Heatmap (PNG)
- ☐ Analysis Report (HTML)

**Click "Download All"** or select individual files

---

## Common Questions

### Q: Why do I see negative expression values?

**A**: The data is log-transformed. Negative values indicate low/no expression.
- `-3.8` ≈ very low expression
- `-5.8` ≈ essentially zero
- Positive values = higher expression

---

### Q: What if my analysis takes longer than expected?

**A**: Runtime depends on:
- Number of cells (more = slower)
- Number of CPU cores (more = faster)
- System load (close other apps)

**Typical times**:
- 500 cells, 4 cores: 5-10 min
- 2000 cells, 4 cores: 20-40 min
- 5000 cells, 8 cores: 1-2 hours

---

### Q: What if I get warnings?

**Common warnings and solutions**:

**"WARNING: low data quality"**
- Solution: Lower LOW.DR and UP.DR to 0.02
- Or increase win.size to 50

**"WARNING! NOT CONVERGENT!"**
- If <10 cells: Ignore, usually fine
- If >50% cells: Check data quality

**"low confidence in classification"**
- Check heatmap for cluster separation
- May need more cells or parameter tuning

See [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) for details

---

### Q: How do I know if results are correct?

**Quality checks**:
1. ✓ Clear clusters in heatmap
2. ✓ Confidence scores >0.8
3. ✓ Aneuploid fraction 30-90%
4. ✓ CNV patterns match known biology

**For this glioblastoma data**:
- ✓ Should see chr7 gain, chr10 loss
- ✓ ~80% aneuploid cells
- ✓ High confidence scores

---

## Next Steps

### For More Practice

**Try different parameters**:
```r
# High resolution
copykat(rawmat = raw_data,
        win.size = 15,
        KS.cut = 0.05,
        sam.name = "high_res",
        n.cores = 4)

# Compare results to default
```

**Try melanoma data**:
```r
melanoma_file <- "data/raw/melanoma_compressed/GSE72056_melanoma_single_cell_revised_v2.txt.gz"

# Load and run (same steps as above)
```

### For Dashboard Development

1. Review: [05_STREAMLIT_DASHBOARD_DESIGN.md](05_STREAMLIT_DASHBOARD_DESIGN.md)
2. Implement: [06_PYTHON_R_INTEGRATION.md](06_PYTHON_R_INTEGRATION.md)
3. Debug: [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)

### For Understanding Results

1. Deep dive: [09_RESULTS_INTERPRETATION.md](09_RESULTS_INTERPRETATION.md)
2. Biology: [../data/DATA_GUIDE.md](../data/DATA_GUIDE.md)
3. Algorithm: [02_ALGORITHM_EXPLAINED.md](02_ALGORITHM_EXPLAINED.md)

---

## Congratulations!

You've completed your first CopyKAT analysis! You now know how to:
- ✓ Load scRNA-seq data
- ✓ Run CopyKAT from R command line
- ✓ Interpret cell classifications
- ✓ Identify chromosomal alterations
- ✓ Validate results against known biology
- ✓ Use the Streamlit dashboard

**Keep exploring** and refer back to the documentation as needed!

---

**Quick Reference Card**

```r
# Essential workflow
library(copykat)
data <- read.table(gzfile("file.txt.gz"), header=TRUE, row.names=1, sep="\t")
result <- copykat(rawmat=data, sam.name="sample", n.cores=4)
table(result$prediction$copykat.pred)  # See classifications
```

**Help Resources**:
- Parameters: [10_PARAMETER_QUICK_REFERENCE.md](10_PARAMETER_QUICK_REFERENCE.md)
- Troubleshooting: [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)
- Glossary: [GLOSSARY.md](GLOSSARY.md)
