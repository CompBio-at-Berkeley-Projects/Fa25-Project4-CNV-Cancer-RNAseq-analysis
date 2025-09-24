# Fa25-Project4-CNV-Cancer-RNAseq-analysis
Build a lightweight, reproducible pipeline + dashboard (using tools like inferCNV) to infer, compare, and visualize CNV patterns from public scRNA-seq cancer datasets, separating malignant from normal cells.
# Data Sources & References
-We wil be looking at diffrent types of tumors:
  -glioblastoma:https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57872
  -melanoma:https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056


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
