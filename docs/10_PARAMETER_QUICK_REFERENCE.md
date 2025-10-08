# CopyKAT Parameters Quick Reference

## At-a-Glance Parameter Table

| Parameter | Default | Range | Purpose | Change When |
|-----------|---------|-------|---------|-------------|
| **rawmat** | (required) | - | Expression matrix | Always provide |
| **id.type** | "S" | "S", "E" | Gene ID type | Using Ensembl IDs |
| **cell.line** | "no" | "yes", "no" | Sample type | Pure cell line |
| **ngene.chr** | 5 | 1-20 | Min genes/chr | Low quality data |
| **LOW.DR** | 0.05 | 0.01-0.3 | Gene detection (smoothing) | Sparse/dense data |
| **UP.DR** | 0.1 | 0.01-0.3 | Gene detection (segmentation) | Sparse/dense data |
| **win.size** | 25 | 10-150 | Window size (genes) | Need focal/broad CNVs |
| **norm.cell.names** | "" | cell IDs | Known normal cells | Have reference cells |
| **KS.cut** | 0.1 | 0-1 | Segmentation threshold | Too many/few breakpoints |
| **sam.name** | "" | string | Sample name | For output files |
| **distance** | "euclidean" | "euclidean", "pearson", "spearman" | Distance metric | Batch effects |
| **output.seg** | "FALSE" | "TRUE", "FALSE" | IGV .seg file | Need IGV visualization |
| **plot.genes** | "TRUE" | "TRUE", "FALSE" | Gene labels | Large datasets |
| **genome** | "hg20" | "hg20", "mm10" | Reference genome | Mouse samples |
| **n.cores** | 1 | 1-max | CPU cores | Speed up analysis |

---

## Decision Trees

### 1. Data Quality Issues

```
Do you see "low data quality" warning?
├─ YES → Decrease LOW.DR and UP.DR
│         Try: LOW.DR=0.02, UP.DR=0.02
│
└─ NO → Keep defaults
          LOW.DR=0.05, UP.DR=0.1
```

### 2. Cell Retention

```
Too many cells filtered out?
├─ YES → Decrease ngene.chr
│         Try: ngene.chr=2 or 3
│
└─ NO → Keep default
          ngene.chr=5
```

### 3. CNV Resolution

```
What CNV scale are you interested in?
├─ Focal amplifications (e.g., EGFR)
│   → win.size=10-15, KS.cut=0.05
│
├─ Arm-level events
│   → win.size=25-50, KS.cut=0.1 (default)
│
└─ Chromosome-level only
    → win.size=100, KS.cut=0.2
```

### 4. Sample Type

```
What is your sample?
├─ Patient tumor biopsy
│   → cell.line="no"
│
├─ Tumor organoid
│   → cell.line="no"
│
└─ Pure cell line (HeLa, MCF7)
    → cell.line="yes"
```

---

## Common Scenarios

### Scenario 1: Standard Tumor Analysis

```r
copykat(
  rawmat = tumor_data,
  id.type = "S",
  cell.line = "no",
  ngene.chr = 5,
  LOW.DR = 0.05,
  UP.DR = 0.1,
  win.size = 25,
  KS.cut = 0.1,
  sam.name = "patient_001",
  distance = "euclidean",
  genome = "hg20",
  n.cores = 4
)
```

**When to use**: Default for most patient tumor samples

---

### Scenario 2: Low-Quality/Sparse Data

```r
copykat(
  rawmat = sparse_data,
  id.type = "S",
  cell.line = "no",
  ngene.chr = 2,        # More permissive
  LOW.DR = 0.02,        # Lower threshold
  UP.DR = 0.02,         # Set equal to LOW.DR
  win.size = 50,        # Larger windows
  KS.cut = 0.15,        # Looser segmentation
  sam.name = "low_qual_sample",
  n.cores = 4
)
```

**When to use**:
- 10x v2 data with <2000 UMI/cell
- Degraded samples
- "low data quality" warning appears

---

### Scenario 3: High-Resolution Analysis

```r
copykat(
  rawmat = deep_data,
  id.type = "S",
  cell.line = "no",
  ngene.chr = 10,       # Stricter quality
  LOW.DR = 0.1,         # Higher threshold
  UP.DR = 0.15,
  win.size = 15,        # Smaller windows
  KS.cut = 0.05,        # Stricter segmentation
  sam.name = "high_res_sample",
  n.cores = 8
)
```

**When to use**:
- High-depth sequencing (>5000 UMI/cell)
- Looking for focal amplifications
- Need detailed breakpoint mapping

---

### Scenario 4: Pure Cell Line

```r
copykat(
  rawmat = cell_line_data,
  id.type = "S",
  cell.line = "yes",   # Key difference
  ngene.chr = 5,
  LOW.DR = 0.05,
  UP.DR = 0.1,
  win.size = 25,
  sam.name = "HeLa_cells",
  n.cores = 4
)
```

**When to use**:
- HeLa, MCF7, U87, A375, etc.
- 100% cancer cells, no normal contamination

---

### Scenario 5: With Known Normal Cells

```r
# Identify normal cells from markers
normal_cells <- colnames(data)[which(data["CD45",] > 5)]

copykat(
  rawmat = data,
  id.type = "S",
  cell.line = "no",
  norm.cell.names = normal_cells,  # Provide reference
  ngene.chr = 5,
  LOW.DR = 0.05,
  UP.DR = 0.1,
  win.size = 25,
  sam.name = "sample_with_ref",
  n.cores = 4
)
```

**When to use**:
- You've identified immune/stromal cells by markers
- Want to improve baseline accuracy

---

### Scenario 6: Mouse Samples

```r
copykat(
  rawmat = mouse_tumor,
  id.type = "S",
  cell.line = "no",
  genome = "mm10",     # Mouse genome
  ngene.chr = 5,
  LOW.DR = 0.05,
  UP.DR = 0.1,
  win.size = 25,
  sam.name = "mouse_sample",
  n.cores = 4
)
```

**When to use**: Any mouse scRNA-seq data

---

## Parameter Combinations

### For Different Sequencing Depths

| Depth | UMI/cell | ngene.chr | LOW.DR | UP.DR | win.size |
|-------|----------|-----------|--------|-------|----------|
| Low | <2000 | 2-3 | 0.02 | 0.02 | 50 |
| Medium | 2000-5000 | 5 | 0.05 | 0.1 | 25 |
| High | 5000-10000 | 8-10 | 0.08 | 0.15 | 20 |
| Very High | >10000 | 10-15 | 0.1 | 0.2 | 15 |

### For Different CNV Types

| CNV Type | win.size | KS.cut | Use Case |
|----------|----------|--------|----------|
| Focal (<5Mb) | 10-15 | 0.05 | EGFR, MYC amplifications |
| Regional (5-50Mb) | 20-30 | 0.1 | Partial chromosome arms |
| Arm-level (>50Mb) | 40-60 | 0.15 | Full chromosome arms |
| Whole chromosome | 80-150 | 0.2 | Monosomy/trisomy |

---

## Troubleshooting Quick Fixes

### Problem: All cells filtered out

**Solution**:
```r
# Decrease ngene.chr
ngene.chr = 1  # Very permissive
LOW.DR = 0.01
UP.DR = 0.01
```

---

### Problem: "low data quality" warning

**Solution**:
```r
LOW.DR = 0.02
UP.DR = 0.02  # Set equal
win.size = 50  # Increase window
```

---

### Problem: No aneuploid cells detected

**Check**:
1. Is this really a tumor sample?
2. Try decreasing KS.cut to detect subtle CNVs
3. Check if cells were pre-filtered (only normal cells left)

**Solution**:
```r
KS.cut = 0.05  # More sensitive
win.size = 20  # Higher resolution
```

---

### Problem: Too many breakpoints (noisy)

**Solution**:
```r
KS.cut = 0.2   # Increase threshold
win.size = 50  # Larger windows
```

---

### Problem: Analysis too slow

**Solution**:
```r
n.cores = 8            # Use more cores
plot.genes = "FALSE"   # Disable gene labels
output.seg = "FALSE"   # Skip .seg file
```

---

## Streamlit Widget Recommendations

```python
import streamlit as st

# Basic Parameters (always visible)
st.subheader("Basic Parameters")

sam_name = st.text_input("Sample Name", "my_sample")

genome = st.selectbox(
    "Genome",
    ["hg20", "mm10"],
    format_func=lambda x: "Human (hg20)" if x == "hg20" else "Mouse (mm10)"
)

cell_line = st.radio(
    "Sample Type",
    ["no", "yes"],
    format_func=lambda x: "Tumor sample (mixed)" if x == "no" else "Pure cell line"
)

# Advanced Parameters (collapsible)
with st.expander("Advanced Parameters"):

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Quality Filtering")
        ngene_chr = st.slider("Min genes/chr", 1, 20, 5)
        low_dr = st.slider("LOW.DR", 0.01, 0.3, 0.05, 0.01)
        up_dr = st.slider("UP.DR", low_dr, 0.3, 0.1, 0.01)

    with col2:
        st.caption("Algorithm Tuning")
        win_size = st.slider("Window size", 10, 150, 25, 5)
        ks_cut = st.slider("KS.cut", 0.0, 1.0, 0.1, 0.05)
        distance = st.selectbox("Distance", ["euclidean", "pearson", "spearman"])

    st.caption("Performance")
    n_cores = st.slider("CPU cores", 1, os.cpu_count(), 4)

    st.caption("Output Options")
    col3, col4 = st.columns(2)
    with col3:
        output_seg = st.checkbox("Generate .seg file", value=False)
    with col4:
        plot_genes = st.checkbox("Show gene labels", value=True)
```

---

## Parameter Impact Summary

| To Increase... | Adjust These Parameters |
|----------------|------------------------|
| **Cell retention** | ↓ ngene.chr, ↓ LOW.DR, ↓ UP.DR |
| **CNV resolution** | ↓ win.size, ↓ KS.cut |
| **Smoothness** | ↑ win.size, ↑ KS.cut |
| **Speed** | ↑ n.cores, set plot.genes=FALSE |
| **Sensitivity** | ↓ KS.cut, ↓ win.size |
| **Specificity** | ↑ KS.cut, ↑ ngene.chr, ↑ LOW.DR |

---

## Validation Checklist

Before running CopyKAT, verify:

- [ ] Expression matrix: genes in rows, cells in columns
- [ ] Gene names match id.type (Symbol vs Ensembl)
- [ ] No negative values in matrix
- [ ] At least 100 cells (preferably 500+)
- [ ] At least 5000 genes detected
- [ ] Genome matches species (hg20 for human, mm10 for mouse)
- [ ] If cell.line="yes", confirm 100% cancer cells
- [ ] Sample name doesn't contain spaces or special characters

---

**See Full Documentation**:
- [03_PARAMETERS_REFERENCE.md](03_PARAMETERS_REFERENCE.md) - Detailed parameter explanations
- [04_CLI_USAGE_GUIDE.md](04_CLI_USAGE_GUIDE.md) - Complete usage examples
- [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) - Problem solving guide
