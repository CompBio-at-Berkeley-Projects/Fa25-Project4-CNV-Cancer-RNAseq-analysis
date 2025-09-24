# Fa25-Project4-CNV-Cancer-RNAseq-analysis
Build a lightweight, reproducible pipeline + dashboard (using tools like inferCNV) to infer, compare, and visualize CNV patterns from public scRNA-seq cancer datasets, separating malignant from normal cells.
# Data Sources & References
- We will be looking at different types of tumors:
  - **Glioblastoma**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57872
  - **Melanoma**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056
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
