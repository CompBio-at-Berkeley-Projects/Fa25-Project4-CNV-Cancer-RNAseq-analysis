# CNV-Cancer-RNAseq-analysis

A user-friendly, interactive web application for Copy Number Variation (CNV) analysis from single-cell RNA sequencing data using CopyKAT.

## Quick Start

**New Team Member?** Start here: [instructions.md](instructions.md)

**Frontend Developer?** Read: [frontend/frontend.md](frontend/frontend.md)

**Backend Developer?** Read: [backend/backend.md](backend/backend.md)

## Project Overview

This project provides an intuitive web application for analyzing copy number variations (CNVs) from single-cell RNA-seq data. It helps researchers distinguish malignant cells from non-malignant cells and visualize genomic instability in cancer datasets.

### Technology Stack

- **Frontend**: React + TypeScript + Tailwind CSS (modern web UI)
- **Backend API**: FastAPI (Python REST API)
- **Analysis Engine**: R with CopyKAT package
- **Integration**: Python subprocess bridge connecting API to R scripts
- **Architecture**: Decoupled 3-tier architecture (Frontend ↔ API ↔ R Engine)

## Project Structure

```
Fa25-Project4-CNV-Cancer-RNAseq-analysis/
├── instructions.md              # Main onboarding guide (START HERE!)
│
├── frontend/                    # React + TypeScript UI
│   ├── src/
│   │   ├── api/                # API client utilities
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── pages/              # Page components
│   │   ├── utils/              # Utility functions
│   │   └── types/              # TypeScript types
│   ├── package.json            # Node.js dependencies
│   └── vite.config.ts          # Vite configuration
│
├── frontend_legacy/             # Legacy Streamlit app (backup)
│
├── backend/                     # R analysis engine (Rajan & Jimmy)
│   ├── backend.md              # Backend development guide
│   ├── data/                   # Data files
│   ├── results/                # Analysis outputs
│   ├── r_scripts/              # R analysis scripts
│   │   ├── example_complete_workflow.R  # WORKING EXAMPLE
│   │   ├── copykat_analysis.R           # Main script (TODO)
│   │   ├── copykat_utils.R              # Utilities (TODO)
│   │   ├── data_preprocessing.R         # Preprocessing (TODO)
│   │   └── copykat_report.Rmd           # Report template (TODO)
│   ├── api/                    # Python-R bridge & FastAPI
│   │   ├── routes.py           # FastAPI endpoints
│   │   ├── models.py           # Pydantic models
│   │   ├── services.py         # Business logic layer
│   │   ├── r_executor.py       # Execute R scripts
│   │   ├── result_parser.py    # Parse outputs
│   │   └── status_monitor.py   # Monitor progress
│   ├── main.py                 # FastAPI application entry
│   └── requirements.txt        # Python dependencies
│
├── shared/                      # Shared utilities
│   ├── shared.md               # Shared documentation
│   ├── config.py               # Configuration management
│   ├── constants.py            # Project constants
│   ├── utils.py                # Common utilities
│   └── schemas/                # Data contracts
│       ├── input_schema.json   # Analysis input format
│       └── output_schema.json  # Analysis output format
│
├── tests/                       # Test suite
│   ├── test_frontend.py        # Frontend tests
│   ├── test_backend.py         # Backend tests
│   └── test_integration.py     # Integration tests
│
├── docs/                        # User documentation
│   ├── 01_COPYKAT_OVERVIEW.md through 11_AUTOMATED_PIPELINE_GUIDE.md
│   └── GLOSSARY.md
│
├── config/                      # Configuration files
│   └── analysis_config.yaml
│
└── Product Requirements Document (PRD)_*.md
```

## Team Assignments

### Baovi Nguyen - Frontend Lead
- **Role**: Streamlit UI development
- **Read**: [instructions.md](instructions.md) → [frontend/frontend.md](frontend/frontend.md)
- **Work in**: `frontend/` directory
- **Reference**: [docs/05_STREAMLIT_DASHBOARD_DESIGN.md](docs/05_STREAMLIT_DASHBOARD_DESIGN.md)

### Rajan Tavathia & Jimmy Liu - Backend Team
- **Role**: R script implementation and CopyKAT integration
- **Read**: [instructions.md](instructions.md) → [backend/backend.md](backend/backend.md)
- **Work in**: `backend/r_scripts/` directory
- **Reference**: `backend/r_scripts/example_complete_workflow.R` (complete working example)

### Allison Cheng
- **Current Assignment**: Project familiarization
- **Read**: [instructions.md](instructions.md) and project documentation

## Quick Setup

### Prerequisites

- **Node.js 18+** and **npm** (for React frontend)
- **Python 3.8+** (for FastAPI backend)
- **R 4.0+** (for CopyKAT analysis)
- **Conda environment** (recommended for R)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Fa25-Project4-CNV-Cancer-RNAseq-analysis
   ```

2. **Setup Conda environment** (if not already done)
   ```bash
   conda create -n Project4-CNV-Cancer-RNAseq r-base -y
   conda activate Project4-CNV-Cancer-RNAseq
   ```

3. **Install R packages** (if not already done)
   ```bash
   R -e 'install.packages("remotes", repos="http://cran.rstudio.com/")'
   R -e 'remotes::install_github("navinlabcode/copykat")'
   R -e 'install.packages(c("yaml", "logger", "rmarkdown", "ggplot2"), repos="http://cran.rstudio.com/")'
   ```

4. **Install Python packages** (backend API)
   ```bash
   pip install -r backend/requirements.txt
   ```

5. **Install Node.js packages** (frontend)
   ```bash
   cd frontend
   npm install
   ```

6. **Verify installation**
   ```bash
   # Test R
   R -e 'library(copykat); library(yaml); library(logger)'
   
   # Test Python/FastAPI
   python -c "import fastapi; print('FastAPI installed')"
   
   # Test Node.js
   npm --version
   ```

## Running the Application

### Quick Start (Both Servers)

**Terminal 1 - Backend API:**
```bash
# From project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# From project root
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173 (React app)
- **Backend API**: http://localhost:8000 (FastAPI)
- **API Docs**: http://localhost:8000/docs (Swagger UI)

### Backend (R Analysis - Standalone)

```bash
# Test the complete working example
Rscript backend/r_scripts/example_complete_workflow.R \
  --input backend/data/raw/glioblastomas_compressed/GSE57872_GBM_data_matrix.txt.gz \
  --name test_sample \
  --output backend/results \
  --genome hg20 \
  --cores 4
```

Results will be in `backend/results/test_sample_*/`

## Development Workflow

1. **Always start from main branch**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**
   ```bash
   git add .
   git commit -m "Add feature description"
   ```

4. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Code review and merge**
   - Get review from team member
   - Merge to main after approval

## Key Documentation

### For All Team Members
- [instructions.md](instructions.md) - Main onboarding and team guide
- [Product Requirements Document](Product%20Requirements%20Document%20(PRD)_%20CNV-Cancer-RNAseq-analysis.md)

### For Frontend Team
- [frontend_legacy/frontend.md](frontend_legacy/frontend.md) - Legacy Streamlit guide
- [API_DOCS.md](API_DOCS.md) - FastAPI endpoint documentation
- [docs/06_PYTHON_R_INTEGRATION.md](docs/06_PYTHON_R_INTEGRATION.md)

### For Backend Team
- [backend/backend.md](backend/backend.md) - Backend development guide
- [backend/data/DATA_GUIDE.md](backend/data/DATA_GUIDE.md)
- [docs/01_COPYKAT_OVERVIEW.md](docs/01_COPYKAT_OVERVIEW.md) through [docs/11_AUTOMATED_PIPELINE_GUIDE.md](docs/11_AUTOMATED_PIPELINE_GUIDE.md)

### For Everyone
- [docs/07_TROUBLESHOOTING.md](docs/07_TROUBLESHOOTING.md)
- [docs/GLOSSARY.md](docs/GLOSSARY.md)

## Data Sources

### Included Datasets

1. **Glioblastoma (GSE57872)**
   - Location: `backend/data/raw/glioblastomas_compressed/`
   - Cells: ~400
   - Genes: ~20,000
   - Source: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57872

2. **Melanoma (GSE72056)**
   - Location: `backend/data/raw/melanoma_compressed/`
   - Cells: ~4,000
   - Genes: ~23,000
   - Source: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056

## Project Goals

- Provide modern, responsive web interface for CNV analysis
- RESTful API architecture for easy integration
- Automate CopyKAT analysis pipeline
- Enable reproducible research
- Support multiple cancer datasets
- Clear team collaboration structure

## Critical Rules

1. **File Organization**: Frontend code in `frontend/`, backend code in `backend/`, shared in `shared/`
2. **Communication**: All frontend-backend calls through `backend/api/` (never direct R calls)
3. **Data Schemas**: Use `shared/schemas/` for input/output contracts
4. **Configuration**: Use `shared/config.py` and `config/analysis_config.yaml`
5. **Documentation**: Update relevant .md files when adding features

## Getting Help

- Check [instructions.md](instructions.md) first
- Read role-specific guides ([frontend.md](frontend/frontend.md) or [backend.md](backend/backend.md))
- Review [docs/07_TROUBLESHOOTING.md](docs/07_TROUBLESHOOTING.md)
- Ask in team channel
- Create GitHub issue for bugs

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_frontend.py
```

## Future Work

- Docker containerization
- CI/CD pipeline
- Additional CNV analysis tools (inferCNV)
- Extended test coverage
- Performance optimizations

## Contributing

See [instructions.md](instructions.md) for detailed contribution guidelines.

## License

This project is for educational purposes as part of Fa25-Project4.

## Authors

- **Baovi Nguyen** - Frontend Lead
- **Rajan Tavathia** - Backend Team
- **Jimmy Liu** - Backend Team
- **Allison Cheng** - Team Member

## References

- CopyKAT: Gao et al. (2021) Nature Biotechnology
- CopyKAT GitHub: https://github.com/navinlabcode/copykat
- Streamlit Documentation: https://docs.streamlit.io/

---

**Built with React, FastAPI, and CopyKAT**
