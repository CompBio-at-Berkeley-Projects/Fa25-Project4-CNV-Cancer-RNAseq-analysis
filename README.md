# Fa25-Project4-CNV-Cancer-RNAseq-analysis
Build a lightweight, reproducible pipeline + dashboard (using tools like inferCNV) to infer, compare, and visualize CNV patterns from public scRNA-seq cancer datasets, separating malignant from normal cells.
# Data Sources & References
- We will be looking at different types of tumors:
  - **Glioblastoma**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57872
  - **Melanoma**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056
- **Tools**
  - Python: scanpy (QC/CL), anndata, scrublet (doublets), bbknn/harmony (batch), plotting (matplotlib).
  - CNV callers: inferCNV (R), CopyKAT (R), optional: HoneyBADGER, CONICSmat (R). (Start with CopyKAT for auto tumor/normal calls; inferCNV for detailed chromosome heatmaps.)
  - Optional validation: bulk WES/WGS CNV if available; or author labels where provided.-
  -Dashboard: lightweight Streamlit (Python) or Quarto/R Shiny.
- **R Resources**
  - https://www.youtube.com/watch?v=_V8eKsto3Ug
  - Rstudio: https://posit.co/download/rstudio-desktop/
- **Python refresher**:
  - https://www.youtube.com/watch?v=VchuKL44s6E&t=94s
- Github basics:https://sp25.datastructur.es/labs/lab04/ and Google
- Feel Free to use LLMs to help you code as long as you are learning
  
# Suggested Structure
```
cnv-scRNA/
  data/ raw/ processed/
  notebooks/
  src/
  envs/  (environment.yml / renv.lock)
  results/ figures/
  app/   (streamlit or shiny)
```

# Environment Setup

## Prerequisites
- **Anaconda or Miniconda installed**
  - Download from: https://www.anaconda.com/download or https://docs.conda.io/en/latest/miniconda.html
  - Make sure to check "Add conda to PATH" during installation (Windows) or follow post-installation instructions (Mac/Linux)

## Installing CopyKAT (Expected time: 15-20 minutes)

### For Mac/Linux Users

#### Step 1: Install Conda
```
# For Apple Silicon (arm64)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh

# For Intel Macs (x86_64)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh`
```


#### Step 2: Create conda environment with R
Copy and paste this entire command:
```bash
conda create -n Project4-CNV-Cancer-RNAseq r-base -y
```

**If you get "conda: command not found"**, try one of these:
```bash
# For Anaconda users:
~/anaconda3/bin/conda create -n Project4-CNV-Cancer-RNAseq r-base -y

# For Miniconda users:
~/miniconda3/bin/conda create -n Project4-CNV-Cancer-RNAseq r-base -y
```

#### Step 3: Activate the environment
```bash
conda activate Project4-CNV-Cancer-RNAseq
```

**If activation fails**, use:
```bash
# For Anaconda:
source ~/anaconda3/bin/activate Project4-CNV-Cancer-RNAseq

# For Miniconda:
source ~/miniconda3/bin/activate Project4-CNV-Cancer-RNAseq
```

#### Step 4: Install remotes package
Copy and paste this command:
```bash
R -e 'install.packages("remotes", repos="http://cran.rstudio.com/")'
```
Wait for it to complete (5-10 minutes). You'll see many lines of output.

#### Step 5: Install CopyKAT
Copy and paste this command:
```bash
R -e 'remotes::install_github("navinlabcode/copykat")'
```
Wait for it to complete (5-10 minutes). You should see "DONE (copykat)" at the end.

#### Step 6: Install Additional R Packages (for automated pipeline)
Copy and paste this command:
```bash
R -e 'install.packages(c("yaml", "logger", "rmarkdown", "knitr", "ggplot2", "pheatmap", "RColorBrewer", "gridExtra"), repos="http://cran.rstudio.com/")'
```
Wait for it to complete (3-5 minutes). These packages are needed for the automated pipeline and HTML reports.

### For Windows Users

#### Step 1: Open Anaconda Prompt
- Press `Windows Key`, type "Anaconda Prompt", and press Enter
- **Important**: Use Anaconda Prompt, NOT regular Command Prompt

#### Step 2: Create conda environment with R
Copy and paste this entire command:
```bash
conda create -n Project4-CNV-Cancer-RNAseq r-base -y
```
Press Enter and wait for completion.

#### Step 3: Activate the environment
```bash
conda activate Project4-CNV-Cancer-RNAseq
```

#### Step 4: Install remotes package
Copy and paste this command:
```bash
R -e "install.packages('remotes', repos='http://cran.rstudio.com/')"
```
Wait for it to complete (5-10 minutes).

#### Step 5: Install CopyKAT
Copy and paste this command:
```bash
R -e "remotes::install_github('navinlabcode/copykat')"
```
Wait for it to complete (5-10 minutes). You should see "DONE (copykat)" at the end.

#### Step 6: Install Additional R Packages (for automated pipeline)
Copy and paste this command:
```bash
R -e "install.packages(c('yaml', 'logger', 'rmarkdown', 'knitr', 'ggplot2', 'pheatmap', 'RColorBrewer', 'gridExtra'), repos='http://cran.rstudio.com/')"
```
Wait for it to complete (3-5 minutes). These packages are needed for the automated pipeline and HTML reports.

### Verify Installation (All Platforms)

1. Make sure environment is activated:
```bash
conda activate Project4-CNV-Cancer-RNAseq
```

2. Start R:
```bash
R
```

3. In R, test all packages:
```r
# Test CopyKAT
library(copykat)

# Test pipeline packages
library(yaml)
library(logger)
library(rmarkdown)
library(ggplot2)

# If no errors appear, all packages are installed correctly!
```

4. Type `q()` to exit R (type `n` when asked to save workspace).

5. **Test the automated pipeline** (optional but recommended):
```bash
# Make sure you're in the project directory
cd ~/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Run example analysis
Rscript r_scripts/automated_copykat_analysis.R \
  --input data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  --name test_run \
  --output results \
  --genome hg20 \
  --cores 4
```

If successful, you should see:
- Progress messages for each step
- "ANALYSIS COMPLETE" at the end
- Results in `results/test_run_*/`

### Common Issues

**Issue**: `devtools` installation fails with errors about systemfonts, textshaping, ragg, or pkgdown
- **Solution**: We use `remotes` instead, which is lighter and has fewer dependencies

**Issue**: CopyKAT not found on CRAN
- **Solution**: CopyKAT is only on GitHub, hence we use `remotes::install_github()`

**Issue**: Long compilation times or warnings during installation
- **Solution**: This is normal. Wait for "DONE (copykat)" message. Installation can take 15-20 minutes total.

**Issue**: Permission errors
- **Solution**: Don't use `sudo`. Install in user space via conda as shown above.

**Issue**: "conda: command not found" on Mac/Linux
- **Solution**: Use full path like shown in Step 2 alternatives above, or run `source ~/.bashrc` (Linux) or `source ~/.zshrc` (Mac)

---

# Quick Start: Running CopyKAT Analysis

## Option 1: Automated Pipeline (Recommended)

The automated pipeline handles everything: validation, preprocessing, analysis, and reporting.

```bash
# Activate environment
conda activate Project4-CNV-Cancer-RNAseq

# Navigate to project
cd ~/Fa25-Project4-CNV-Cancer-RNAseq-analysis

# Run analysis
Rscript r_scripts/automated_copykat_analysis.R \
  --input data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  --name my_sample \
  --output results \
  --genome hg20 \
  --cores 4
```

**What you get:**
- Automatic log-transform detection and conversion
- Quality control plots
- CNV heatmaps
- Cell classifications (aneuploid/diploid)
- Chromosome-level alterations
- Detailed logs and error handling

**Output location:** `results/my_sample_TIMESTAMP/`

See [AUTOMATED_PIPELINE_README.md](AUTOMATED_PIPELINE_README.md) for complete guide.

## Option 2: Configuration File (Advanced)

Edit `config/analysis_config.yaml` with your parameters:

```yaml
input:
  file: "data/raw/your_data.txt.gz"
output:
  sample_name: "my_analysis"
copykat:
  genome: "hg20"
  n_cores: 8
```

Then run:
```bash
Rscript r_scripts/automated_copykat_analysis.R config/analysis_config.yaml
```

## Option 3: Manual R Script

See `docs/08_BEGINNER_TUTORIAL.md` for step-by-step manual analysis in R.

---

# Project Structure

```
Fa25-Project4-CNV-Cancer-RNAseq-analysis/
├── data/
│   └── raw/
│       ├── glioblastomas_compressed/     # Glioblastoma datasets
│       └── melanoma_compressed/          # Melanoma datasets
├── r_scripts/
│   ├── automated_copykat_analysis.R     # Main automated pipeline
│   ├── copykat_utils.R                  # Utility functions
│   └── copykat_report.Rmd               # HTML report template
├── config/
│   └── analysis_config.yaml             # Configuration template
├── docs/                                 # Comprehensive documentation
│   ├── 01_COPYKAT_OVERVIEW.md
│   ├── 02_ALGORITHM_EXPLAINED.md
│   ├── 03_PARAMETERS_REFERENCE.md
│   ├── 04_CLI_USAGE_GUIDE.md
│   ├── 05_STREAMLIT_DASHBOARD_DESIGN.md
│   ├── 06_PYTHON_R_INTEGRATION.md
│   ├── 07_TROUBLESHOOTING.md
│   ├── 08_BEGINNER_TUTORIAL.md
│   ├── 09_RESULTS_INTERPRETATION.md
│   ├── 10_PARAMETER_QUICK_REFERENCE.md
│   ├── 11_AUTOMATED_PIPELINE_GUIDE.md
│   └── GLOSSARY.md
├── results/                             # Analysis outputs
│   └── sample_TIMESTAMP/
│       ├── logs/                        # Detailed logs
│       ├── plots/                       # QC and summary plots
│       ├── *_copykat_prediction.txt     # Cell classifications
│       ├── *_copykat_heatmap.jpeg       # CNV heatmap
│       └── *_report.html               # Comprehensive report
├── AUTOMATED_PIPELINE_README.md         # Quick start guide
└── README.md                           # This file
```

---

# Documentation

## For Beginners
- **[AUTOMATED_PIPELINE_README.md](AUTOMATED_PIPELINE_README.md)** - Quick start guide (start here!)
- **[docs/08_BEGINNER_TUTORIAL.md](docs/08_BEGINNER_TUTORIAL.md)** - Hands-on walkthrough
- **[docs/GLOSSARY.md](docs/GLOSSARY.md)** - 70+ technical terms explained

## For Understanding CopyKAT
- **[docs/01_COPYKAT_OVERVIEW.md](docs/01_COPYKAT_OVERVIEW.md)** - What is CopyKAT and why use it?
- **[docs/02_ALGORITHM_EXPLAINED.md](docs/02_ALGORITHM_EXPLAINED.md)** - How the algorithm works
- **[docs/09_RESULTS_INTERPRETATION.md](docs/09_RESULTS_INTERPRETATION.md)** - Understanding outputs

## For Using CopyKAT
- **[docs/04_CLI_USAGE_GUIDE.md](docs/04_CLI_USAGE_GUIDE.md)** - Command-line reference
- **[docs/03_PARAMETERS_REFERENCE.md](docs/03_PARAMETERS_REFERENCE.md)** - All 16 parameters explained
- **[docs/10_PARAMETER_QUICK_REFERENCE.md](docs/10_PARAMETER_QUICK_REFERENCE.md)** - Quick lookup & scenarios
- **[docs/11_AUTOMATED_PIPELINE_GUIDE.md](docs/11_AUTOMATED_PIPELINE_GUIDE.md)** - Complete pipeline guide

## For Development
- **[docs/05_STREAMLIT_DASHBOARD_DESIGN.md](docs/05_STREAMLIT_DASHBOARD_DESIGN.md)** - Dashboard UI/UX design
- **[docs/06_PYTHON_R_INTEGRATION.md](docs/06_PYTHON_R_INTEGRATION.md)** - Python-R integration code

## Troubleshooting
- **[docs/07_TROUBLESHOOTING.md](docs/07_TROUBLESHOOTING.md)** - Common issues and solutions

---

# File Structure
The raw files are contained `data/raw`, where it is saved as a raw compressed file (`data/raw/melanoma_compressed` or `data/raw/glioblastomas_compressed`).

The files that end in `.soft`/`.xml` contain metadata which I believe are not useful to our project. The main target files are the `.txt` files (such as `..._series_matrix.txt`) which contain the complete processed expression matrix or expression matrix with samples as columns, genes as rows. 
