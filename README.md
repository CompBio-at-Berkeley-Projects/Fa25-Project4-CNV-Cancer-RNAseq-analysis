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

#### Step 1: Open Terminal
- Press `Command + Space`, type "Terminal", and press Enter

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

### Verify Installation (All Platforms)

1. Make sure environment is activated:
```bash
conda activate Project4-CNV-Cancer-RNAseq
```

2. Start R:
```bash
R
```

3. In R, test CopyKAT:
```r
library(copykat)
```

4. If no errors appear, installation succeeded! Type `q()` to exit R (type `n` when asked to save workspace).

### Common Issues

**Issue**: `devtools` installation fails with errors about systemfonts, textshaping, ragg, or pkgdown
- **Solution**: We use `remotes` instead, which is lighter and has fewer dependencies

**Issue**: CopyKAT not found on CRAN
- **Solution**: CopyKAT is only on GitHub, hence we use `remotes::install_github()`

**Issue**: Long compilation times or warnings during installation
- **Solution**: This is normal. Wait for "DONE (copykat)" message. Installation can take 15-20 minutes total.

**Issue**: Permission errors
- **Solution**: Don't use `sudo`. Install in user space via conda as shown above.

# File Structure
The raw files are contained `data/raw`, where it is saved as a raw compressed file (`data/raw/melanoma_compressed` or `data/raw/glioblastomas_compressed`).

The files that end in `.soft`/`.xml` contain metadata which I believe are not useful to our project. The main target files are the `.txt` files (such as `..._series_matrix.txt`) which contain the complete processed expression matrix or expression matrix with samples as columns, genes as rows. 