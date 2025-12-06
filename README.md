# CNV-Cancer-RNAseq-analysis

A user-friendly, interactive web application for Copy Number Variation (CNV) analysis from single-cell RNA sequencing data using CopyKAT.

## Quick Start

### Docker Deployment (Recommended)

The easiest way to run the application is using Docker:

```bash
# Build and start all services
docker compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

See the [Docker Deployment](#docker-deployment) section below for detailed instructions.

### Local Development

**Getting Started?** Start here: [docs/project-docs/instructions.md](docs/project-docs/instructions.md)

**Frontend Development?** Read: [frontend/frontend.md](frontend/frontend.md)

**Backend Development?** Read: [backend/backend.md](backend/backend.md)

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
├── docs/
│   └── project-docs/
│       ├── instructions.md      # Main onboarding guide
│       ├── prd.md               # Product requirements
│       └── API_DOCS.md          # API documentation
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
├── backend/                     # R analysis engine
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

### Getting Started
- [docs/project-docs/instructions.md](docs/project-docs/instructions.md) - Main onboarding guide
- [docs/project-docs/prd.md](docs/project-docs/prd.md) - Product requirements

### Frontend Development
- [frontend_legacy/frontend.md](frontend_legacy/frontend.md) - Legacy Streamlit guide
- [docs/project-docs/API_DOCS.md](docs/project-docs/API_DOCS.md) - FastAPI endpoint documentation
- [docs/06_PYTHON_R_INTEGRATION.md](docs/06_PYTHON_R_INTEGRATION.md)

### Backend Development
- [backend/backend.md](backend/backend.md) - Backend development guide
- [backend/data/DATA_GUIDE.md](backend/data/DATA_GUIDE.md)
- [docs/01_COPYKAT_OVERVIEW.md](docs/01_COPYKAT_OVERVIEW.md) through [docs/11_AUTOMATED_PIPELINE_GUIDE.md](docs/11_AUTOMATED_PIPELINE_GUIDE.md)

### Additional Resources
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

## Critical Rules

1. **File Organization**: Frontend code in `frontend/`, backend code in `backend/`, shared in `shared/`
2. **Communication**: All frontend-backend calls through `backend/api/` (never direct R calls)
3. **Data Schemas**: Use `shared/schemas/` for input/output contracts
4. **Configuration**: Use `shared/config.py` and `config/analysis_config.yaml`
5. **Documentation**: Update relevant .md files when adding features

## Getting Help

- Check [docs/project-docs/instructions.md](docs/project-docs/instructions.md) first
- Read development guides ([frontend.md](frontend/frontend.md) or [backend.md](backend/backend.md))
- Review [docs/07_TROUBLESHOOTING.md](docs/07_TROUBLESHOOTING.md)
- Create GitHub issue for bugs

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_frontend.py
```

## Docker Deployment

### Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **8GB+ RAM** (16GB+ recommended for large datasets)
- **10GB+ free disk space**

### Installing Docker

**Windows/Mac**: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER  # Add user to docker group
```

### Quick Start with Docker

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd Fa25-Project4-CNV-Cancer-RNAseq-analysis
   ```

2. **Start the application**
   ```bash
   docker compose up --build
   ```
   
   > First run takes 15-30 minutes to build. Subsequent starts are faster.

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Stop the application**
   ```bash
   # Press Ctrl+C, or run:
   docker compose down
   ```

### Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
│  ┌──────────────────┐      ┌──────────────────────────────┐│
│  │    Frontend      │      │         Backend              ││
│  │   (Nginx)        │─────▶│   (Python + R + CopyKAT)    ││
│  │   Port 3000      │ /api │       Port 8000             ││
│  └──────────────────┘      └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Running in Background

```bash
# Start in background (detached mode)
docker compose up -d --build

# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop services
docker compose down
```

### Working with Your Data

**Upload via Web Interface**: Use the Upload page to add your data files

**Direct File Copy**: Copy data to `backend/data/uploads/`

**Export Results**:
```bash
# Copy results from container to local machine
docker cp copykat-backend:/app/results ./my_results
```

### System Requirements by Dataset Size

| Dataset Size | RAM Required | Expected Runtime |
|--------------|--------------|------------------|
| ~500 cells | 4 GB | 2-5 minutes |
| ~2,000 cells | 8 GB | 10-20 minutes |
| ~5,000 cells | 12 GB | 30-60 minutes |
| ~10,000+ cells | 16 GB+ | 1-3 hours |

### Docker Resource Configuration

Increase Docker's memory allocation in Docker Desktop:
1. Click Docker icon → Settings → Resources
2. Increase Memory to 8-16 GB
3. Click "Apply & Restart"

### Troubleshooting Docker

**"Port already in use"**: Change port in `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "8080:80"  # Change from 3000 to 8080
```

**"Out of memory"**: Increase Docker memory allocation (see above)

**Build errors**: Clean and rebuild:
```bash
docker compose down
docker system prune -f
docker compose up --build
```

**View logs**:
```bash
# All logs
docker compose logs

# Backend only
docker compose logs backend

# Follow in real-time
docker compose logs -f
```

### Environment Variables

Create a `.env` file in the project root to customize:
```bash
# .env
DOCKER_MODE=true
R_EXECUTABLE=Rscript
VITE_API_BASE_URL=/api
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Advanced: Running on Remote Server

```bash
# Start services
docker compose up -d

# Access from other computers
# http://SERVER_IP:3000
```

For production deployments, configure a reverse proxy (nginx/traefik) with HTTPS.

### Cleanup

```bash
# Stop and remove containers
docker compose down

# Full cleanup (removes all data!)
docker compose down -v
docker system prune -af
```

## Future Work

- CI/CD pipeline
- Additional CNV analysis tools (inferCNV)
- Extended test coverage
- Performance optimizations

## Contributing

See [docs/project-docs/instructions.md](docs/project-docs/instructions.md) for detailed contribution guidelines.

## License

This project is for educational purposes as part of Fa25-Project4.

## References

- CopyKAT: Gao et al. (2021) Nature Biotechnology
- CopyKAT GitHub: https://github.com/navinlabcode/copykat
- Streamlit Documentation: https://docs.streamlit.io/

---

**Built with React, FastAPI, and CopyKAT**
