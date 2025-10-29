# Team Onboarding Instructions

Welcome to the CNV-Cancer-RNAseq-analysis project. This document will guide you through understanding the project structure, your role, and how to get started.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Team Assignments](#team-assignments)
4. [Getting Started](#getting-started)
5. [Development Workflow](#development-workflow)
6. [Critical Rules](#critical-rules)
7. [Documentation Index](#documentation-index)
8. [Communication](#communication)

## Project Overview

This project builds a user-friendly, interactive web application for Copy Number Variation (CNV) analysis from single-cell RNA sequencing (scRNA-seq) data. The tool helps researchers distinguish malignant cells from non-malignant cells and visualize genomic instability in cancer datasets.

### Goals

- Provide an intuitive Streamlit dashboard for CNV analysis
- Automate the CopyKAT analysis pipeline
- Enable reproducible research with clear documentation
- Support multiple cancer datasets (glioblastoma, melanoma)

### Technology Stack

- Frontend: Python with Streamlit framework
- Backend: R with CopyKAT package
- Integration: Python subprocess calls to R scripts
- Data: Single-cell RNA-seq expression matrices

## Architecture

### Monorepo Structure

```
Fa25-Project4-CNV-Cancer-RNAseq-analysis/
├── frontend/              # Streamlit UI (Baovi's work)
├── backend/               # R scripts and API bridge (Rajan & Jimmy's work)
├── shared/                # Common utilities and configs
├── tests/                 # Testing suite
├── docs/                  # User-facing documentation
└── config/                # Configuration files
```

### Communication Flow

```
User interacts with Streamlit UI (frontend/)
    ↓
Frontend calls backend/api/ (Python layer)
    ↓
Python API executes backend/r_scripts/ (R scripts)
    ↓
R scripts run CopyKAT analysis
    ↓
Results written to backend/results/
    ↓
Python API parses results
    ↓
Frontend displays visualizations
```

### Key Integration Points

1. **File Upload**: Frontend saves uploaded files to temporary location, passes file path to backend API
2. **Parameter Configuration**: Frontend collects user parameters, sends as JSON to backend API
3. **Progress Monitoring**: Backend API monitors R process execution, sends status updates to frontend
4. **Results Handling**: Backend writes outputs to backend/results/, frontend reads via API layer
5. **Error Handling**: Backend catches R errors, returns structured error messages to frontend

## Team Assignments

### Baovi Nguyen - Frontend Lead

**Role**: Streamlit UI Development

**Your Documentation**:
- Start here: `instructions.md` (this file)
- Then read: `frontend/frontend.md` (your detailed guide)
- Reference: `docs/05_STREAMLIT_DASHBOARD_DESIGN.md`

**Your Responsibilities**:
- Develop all Streamlit pages and components
- Implement file upload functionality
- Create parameter configuration forms
- Build results visualization displays
- Integrate with backend API layer

**Your Primary Files**:
- `frontend/streamlit_app.py`
- `frontend/pages/*.py`
- `frontend/components/*.py`
- `frontend/utils/*.py`

### Rajan Tavathia & Jimmy Liu - Backend Team

**Role**: R Script Implementation and CopyKAT Integration

**Your Documentation**:
- Start here: `instructions.md` (this file)
- Then read: `backend/backend.md` (your detailed guide)
- Reference: `backend/data/DATA_GUIDE.md`, `docs/01-04`, `docs/08-11`

**Your Responsibilities**:
- Implement R analysis scripts
- Configure CopyKAT parameters
- Handle data preprocessing and validation
- Generate analysis outputs and reports
- Ensure proper error handling and logging

**Your Primary Files**:
- `backend/r_scripts/copykat_analysis.R`
- `backend/r_scripts/copykat_utils.R`
- `backend/r_scripts/data_preprocessing.R`
- `backend/r_scripts/copykat_report.Rmd`

**Reference Implementation**:
- See `backend/r_scripts/example_complete_workflow.R` for working example

### Allison Cheng

**Role**: To Be Determined

**Current Assignment**: 
- Read through this onboarding document
- Review the project documentation in `docs/`
- Familiarize yourself with the Product Requirements Document (PRD)
- Your specific tasks will be assigned soon

## Getting Started

### Prerequisites

All team members should have:

1. **Git and GitHub access**
   - Clone the repository
   - Ensure you have push access

2. **Development Environment**
   - For Frontend (Baovi): Python 3.8+, pip
   - For Backend (Rajan & Jimmy): R 4.0+, RStudio
   - Text editor or IDE (VS Code, RStudio, etc.)

3. **Conda Environment**
   ```bash
   conda activate Project4-CNV-Cancer-RNAseq
   ```

### Initial Setup Steps

1. **Read your role-specific documentation**
   - Frontend: `frontend/frontend.md`
   - Backend: `backend/backend.md`

2. **Install dependencies**
   - Frontend: `pip install -r frontend/requirements.txt`
   - Backend: R packages are already installed in conda environment

3. **Test your environment**
   - Frontend: Try running `streamlit hello`
   - Backend: Verify CopyKAT loads with `library(copykat)` in R

4. **Review the example code**
   - Frontend: Check `frontend/components/` for component templates
   - Backend: Review `backend/r_scripts/example_complete_workflow.R`

## Development Workflow

### Git Workflow

1. **Always work on feature branches**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Commit frequently with clear messages**
   ```bash
   git add .
   git commit -m "Add file upload component"
   ```

3. **Push your branch and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Code Review**
   - At least one team member must review
   - Address feedback before merging

5. **Merge to main**
   - Only merge after review approval
   - Delete feature branch after merge

### Daily Development Cycle

1. Pull latest changes: `git pull origin main`
2. Create/switch to your feature branch
3. Work on your assigned tasks
4. Test your changes locally
5. Commit and push your work
6. Create Pull Request when feature is complete

### Communication Workflow

- Daily standups: Share progress, blockers, plans
- Use GitHub Issues for bug reports and feature requests
- Use Pull Request comments for code discussions
- Tag team members when you need their input

## Critical Rules

### 1. File Organization

- Frontend code stays in `frontend/`
- Backend code stays in `backend/`
- Shared utilities go in `shared/`
- Never mix frontend and backend code

### 2. Backend-Frontend Communication

- All frontend-backend calls MUST go through `backend/api/`
- Never call R scripts directly from Streamlit
- Use the provided API layer for all integrations

### 3. Data Schemas

- Input/output contracts are defined in `shared/schemas/`
- Always validate data against schemas
- Update schemas if you change data structures

### 4. Configuration Management

- Use `shared/config.py` for Python configuration
- Use `config/analysis_config.yaml` for R configuration
- Never hardcode file paths or parameters

### 5. Results Storage

- Backend writes to `backend/results/`
- Frontend reads from `backend/results/` via API
- Never write results from frontend directly

### 6. Documentation

- Update relevant .md files when adding features
- Document all functions with docstrings
- Keep README updated with major changes

### 7. Code Quality

- Follow PEP 8 style for Python code
- Follow tidyverse style for R code
- Write descriptive variable and function names
- Add comments for complex logic

### 8. Testing

- Test your code before committing
- Don't break existing functionality
- Report bugs immediately

### 9. Dependencies

- Document any new dependencies
- Update requirements.txt (Python) or document R packages
- Don't use undocumented libraries

### 10. No Direct Coupling

- Frontend should work with mocked backend
- Backend should work standalone (command-line)
- Keep modules independent

## Documentation Index

### For All Team Members

- **This file**: `instructions.md` - Main onboarding
- **Project Overview**: `README.md` - Project introduction
- **Product Requirements**: `Product Requirements Document (PRD)_*.md`

### For Frontend Team (Baovi)

- **Your Guide**: `frontend/frontend.md`
- **Streamlit Design**: `docs/05_STREAMLIT_DASHBOARD_DESIGN.md`
- **Python-R Integration**: `docs/06_PYTHON_R_INTEGRATION.md`
- **Troubleshooting**: `docs/07_TROUBLESHOOTING.md`

### For Backend Team (Rajan & Jimmy)

- **Your Guide**: `backend/backend.md`
- **Data Guide**: `backend/data/DATA_GUIDE.md`
- **CopyKAT Overview**: `docs/01_COPYKAT_OVERVIEW.md`
- **Algorithm Explained**: `docs/02_ALGORITHM_EXPLAINED.md`
- **Parameters Reference**: `docs/03_PARAMETERS_REFERENCE.md`
- **CLI Usage**: `docs/04_CLI_USAGE_GUIDE.md`
- **Beginner Tutorial**: `docs/08_BEGINNER_TUTORIAL.md`
- **Results Interpretation**: `docs/09_RESULTS_INTERPRETATION.md`
- **Parameter Quick Reference**: `docs/10_PARAMETER_QUICK_REFERENCE.md`
- **Automated Pipeline Guide**: `docs/11_AUTOMATED_PIPELINE_GUIDE.md`
- **Troubleshooting**: `docs/07_TROUBLESHOOTING.md`

### For Shared Components

- **Shared Utilities**: `shared/shared.md`
- **Glossary**: `docs/GLOSSARY.md`

## Communication

### Asking for Help

1. **Check documentation first** - Most answers are documented
2. **Search existing issues** - Someone might have asked already
3. **Ask in team channel** - Share knowledge with everyone
4. **Tag the right person** - Frontend questions to Baovi, backend to Rajan/Jimmy
5. **Be specific** - Include error messages, code snippets, what you tried

### Reporting Issues

1. Check if issue already exists
2. Create GitHub Issue with:
   - Clear title
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if relevant
3. Tag with appropriate labels (bug, enhancement, question)

### Requesting Features

1. Discuss with team first
2. Create GitHub Issue with:
   - Feature description
   - Use case / why it's needed
   - Proposed implementation (if you have ideas)
3. Wait for discussion before implementing

## Next Steps

1. Read your role-specific documentation
2. Set up your development environment
3. Run the example code to verify setup
4. Review existing code in your area
5. Ask questions if anything is unclear
6. Start working on your first task

## Future Work

Items planned for future iterations:

- Docker containerization for easy deployment
- Continuous Integration/Continuous Deployment (CI/CD) pipeline
- Additional CNV analysis tools (inferCNV)
- Extended test coverage
- Performance optimizations
- Additional cancer dataset support

Welcome to the team! Let's build something great together.

