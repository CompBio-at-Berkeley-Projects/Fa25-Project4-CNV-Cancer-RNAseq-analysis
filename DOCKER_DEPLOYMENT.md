# Docker Deployment Guide for CopyKAT CNV Analysis

This guide provides step-by-step instructions for deploying the CopyKAT single-cell RNA-seq CNV analysis pipeline using Docker. No prior programming experience is required.

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installing Docker](#installing-docker)
4. [Quick Start (5 minutes)](#quick-start-5-minutes)
5. [Detailed Setup Guide](#detailed-setup-guide)
6. [Using the Application](#using-the-application)
7. [Working with Your Data](#working-with-your-data)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)
10. [FAQ](#faq)

---

## Overview

### What is this tool?

This application provides a web-based interface for running **CopyKAT** (Copynumber Karyotyping of Tumors), an R package that infers genomic copy number alterations from single-cell RNA-seq data. It can identify:

- **Aneuploid cells** (tumor cells with abnormal chromosome numbers)
- **Diploid cells** (normal cells with expected chromosome numbers)

### What is Docker?

Docker is a platform that packages applications and their dependencies into "containers" - self-contained units that run consistently on any computer. Think of it as a complete, pre-configured computer inside your computer.

**Benefits for scientists:**
- ✅ No need to install R, Python, or CopyKAT manually
- ✅ Works identically on Windows, Mac, and Linux
- ✅ Guaranteed reproducibility
- ✅ Easy to share with collaborators

---

## System Requirements

### Minimum Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8 GB | 16 GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Disk Space** | 10 GB free | 20 GB+ free |
| **OS** | Windows 10/11, macOS 10.15+, Linux | Any modern OS |

### Dataset Considerations
| Dataset Size | Expected RAM | Expected Runtime |
|--------------|--------------|------------------|
| ~500 cells | 4 GB | 2-5 minutes |
| ~2,000 cells | 8 GB | 10-20 minutes |
| ~5,000 cells | 12 GB | 30-60 minutes |
| ~10,000+ cells | 16 GB+ | 1-3 hours |

---

## Installing Docker

### Windows

1. **Download Docker Desktop**
   - Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
   - Click "Download for Windows"

2. **Install Docker Desktop**
   - Run the downloaded installer (`.exe` file)
   - Follow the installation wizard
   - **Important**: When prompted, ensure "Use WSL 2" is selected

3. **Start Docker**
   - Launch Docker Desktop from your Start menu
   - Wait for the Docker icon in the system tray to show "Docker Desktop is running"

4. **Verify Installation**
   - Open PowerShell or Command Prompt
   - Run:
     ```cmd
     docker --version
     ```
   - You should see something like: `Docker version 24.x.x`

### macOS

1. **Download Docker Desktop**
   - Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
   - Click "Download for Mac"
   - Choose **Apple Silicon** (M1/M2/M3) or **Intel** based on your Mac

2. **Install Docker Desktop**
   - Open the downloaded `.dmg` file
   - Drag Docker to your Applications folder
   - Launch Docker from Applications

3. **Grant Permissions**
   - You may be prompted to allow Docker to access your filesystem
   - Click "Allow" or "OK" when prompted

4. **Verify Installation**
   - Open Terminal (Applications → Utilities → Terminal)
   - Run:
     ```bash
     docker --version
     ```

### Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io docker-compose-plugin

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
```

---

## Quick Start (5 minutes)

Once Docker is installed, follow these steps:

### Step 1: Download the Project

**Option A: Download ZIP (easiest)**
1. Go to the project repository on GitHub
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file to a folder (e.g., `C:\CopyKAT` or `~/CopyKAT`)

**Option B: Using Git**
```bash
git clone https://github.com/YOUR_REPO/Fa25-Project4-CNV-Cancer-RNAseq-analysis.git
cd Fa25-Project4-CNV-Cancer-RNAseq-analysis
```

### Step 2: Start the Application

**Windows (PowerShell or Command Prompt):**
```cmd
cd C:\path\to\Fa25-Project4-CNV-Cancer-RNAseq-analysis
docker compose up --build
```

**macOS/Linux (Terminal):**
```bash
cd ~/path/to/Fa25-Project4-CNV-Cancer-RNAseq-analysis
docker compose up --build
```

> **Note**: The first time you run this, Docker will download and build the required images. This can take **15-30 minutes** depending on your internet speed. Subsequent starts will be much faster.

### Step 3: Access the Application

1. Wait until you see logs indicating the services are ready:
   ```
   copykat-backend   | INFO:     Uvicorn running on http://0.0.0.0:8000
   copykat-frontend  | nginx: started
   ```

2. Open your web browser and go to:
   ```
   http://localhost:3000
   ```

3. You should see the CopyKAT Analysis Dashboard!

### Step 4: Stop the Application

Press `Ctrl+C` in the terminal, or run:
```bash
docker compose down
```

---

## Detailed Setup Guide

### Project Structure

After downloading, your folder should look like this:

```
Fa25-Project4-CNV-Cancer-RNAseq-analysis/
├── backend/                    # Python + R analysis server
│   ├── data/
│   │   ├── raw/               # Sample datasets included
│   │   └── uploads/           # Your uploaded data goes here
│   ├── results/               # Analysis results stored here
│   └── r_scripts/             # CopyKAT analysis scripts
├── frontend/                  # Web interface
├── docker-compose.yml         # Docker orchestration
└── DOCKER_DEPLOYMENT.md       # This guide
```

### Running in Background Mode

To run the application in the background (detached mode):

```bash
# Start in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Checking Service Status

```bash
# See running containers
docker compose ps

# Check if healthy
docker compose ps --format "table {{.Name}}\t{{.Status}}"
```

Expected output:
```
NAME              STATUS
copykat-backend   Up (healthy)
copykat-frontend  Up (healthy)
```

---

## Using the Application

### 1. Upload Page

1. Navigate to the **Upload** page
2. Choose your input file:
   - **Format**: Tab-separated text file (`.txt` or `.txt.gz`)
   - **Structure**: Genes as rows, cells as columns
   - **First row**: Cell IDs/barcodes
   - **First column**: Gene names

Example data format:
```
GENE    Cell_1    Cell_2    Cell_3    ...
TP53    2.45      0.00      1.23      ...
EGFR    5.67      3.21      0.45      ...
...
```

3. Click **Upload** and wait for confirmation

### 2. Configure Page

Set analysis parameters:

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| **Sample Name** | Identifier for your analysis | Your sample ID |
| **Genome** | Reference genome | `hg20` (human) or `mm10` (mouse) |
| **Cores** | Number of CPU cores | 2-4 |
| **ngene.chr** | Min genes per chromosome | 5 (default) |
| **Window Size** | Smoothing window | 25 (default) |

Click **Run Analysis** to start.

### 3. Results Page

After analysis completes (~5-30 minutes), you'll see:

- **Summary Statistics**: Cell counts and classifications
- **CNV Heatmap**: Visual representation of copy number changes
- **Downloadable Files**: 
  - Prediction file (cell classifications)
  - CNA results (detailed copy number data)

### 4. Download Results

Click the **Download** button to get your results as a ZIP file containing:
- `{sample}_copykat_prediction.txt` - Cell classifications
- `{sample}_copykat_CNA_results.txt` - Copy number segments
- `{sample}_copykat_heatmap.jpeg` - Visualization

---

## Working with Your Data

### Adding Your Own Data Files

**Method 1: Using the Web Interface**
1. Use the Upload page in the application
2. Your file will be saved to `backend/data/uploads/`

**Method 2: Direct File Copy**
1. Copy your data file to `backend/data/raw/`
2. It will appear in the file list when you refresh

**Method 3: Mount Additional Folders**

Edit `docker-compose.yml` to add your data folder:

```yaml
services:
  backend:
    volumes:
      - results_data:/app/results
      - ./backend/data:/app/data:ro
      - /path/to/your/data:/app/external_data:ro  # Add this line
```

### Data Format Requirements

Your input file must:
- Be a gene expression matrix (genes × cells)
- Have gene names in the first column
- Have cell IDs in the first row
- Be tab-separated (`.txt`) or gzipped (`.txt.gz`)
- Contain at least **50 cells** (CopyKAT minimum)
- Have at least **5,000 genes** for reliable results

### Exporting Results

Results are stored in a Docker volume by default. To copy results to your local machine:

```bash
# Copy all results to current directory
docker cp copykat-backend:/app/results ./my_results

# Or access them directly at:
# backend/results/ (if you mounted the volume)
```

---

## Troubleshooting

### Common Issues and Solutions

#### "Docker daemon is not running"

**Windows**: Start Docker Desktop from the Start menu
**Mac**: Launch Docker from Applications
**Linux**: Run `sudo systemctl start docker`

#### "Port 3000 is already in use"

Another application is using port 3000. Either:
1. Stop the other application, or
2. Change the port in `docker-compose.yml`:
   ```yaml
   frontend:
     ports:
       - "8080:80"  # Change 3000 to 8080
   ```

#### "Out of memory" during analysis

Increase Docker's memory allocation:

**Docker Desktop (Windows/Mac):**
1. Click Docker icon → Settings → Resources
2. Increase Memory to 8-16 GB
3. Click "Apply & Restart"

#### Build fails with R package errors

This usually means a network issue during package installation. Try:
```bash
# Clean rebuild
docker compose down
docker system prune -f
docker compose up --build
```

#### Analysis runs but produces no results

Check the logs for errors:
```bash
docker compose logs backend
```

Common causes:
- Input file format incorrect
- Not enough cells (minimum 50)
- Data is already heavily filtered

#### Cannot access http://localhost:3000

1. Make sure both containers are running: `docker compose ps`
2. Check if frontend started: `docker compose logs frontend`
3. Try using `http://127.0.0.1:3000` instead

### Viewing Detailed Logs

```bash
# All logs
docker compose logs

# Backend only (R analysis)
docker compose logs backend

# Follow logs in real-time
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100
```

---

## Advanced Configuration

### Adjusting Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '8'        # Increase CPU cores
          memory: 16G      # Increase memory
        reservations:
          cpus: '4'
          memory: 8G
```

### Running on a Remote Server

1. Start the application with specific host binding:
   ```bash
   docker compose up -d
   ```

2. Access from other computers using the server's IP:
   ```
   http://SERVER_IP:3000
   ```

3. For secure access, consider using a reverse proxy (nginx/traefik) with HTTPS.

### Environment Variables

Create a `.env` file in the project root:

```bash
# .env
BACKEND_PORT=8000
FRONTEND_PORT=3000
MAX_UPLOAD_SIZE=500M
```

### Persistent Data Storage

Results are stored in a Docker volume by default. To use a local folder instead:

```yaml
services:
  backend:
    volumes:
      - ./my_results:/app/results  # Local folder
```

---

## FAQ

### Q: Do I need to install R or Python?
**A**: No! Docker containers include all required software. You only need Docker installed.

### Q: Can I run multiple analyses simultaneously?
**A**: Yes, but each analysis uses significant memory. Monitor your system resources.

### Q: How do I update to a newer version?
**A**: 
```bash
git pull  # or download new ZIP
docker compose down
docker compose up --build
```

### Q: Can I use this on a cluster/HPC?
**A**: Yes, if your cluster supports Docker or Singularity. Convert the image:
```bash
singularity pull copykat.sif docker://your-registry/copykat-backend
```

### Q: How do I cite this tool?
**A**: Please cite:
- CopyKAT: Gao R, et al. Nature Biotechnology (2021)
- This pipeline: [Your citation here]

### Q: Where can I get help?
**A**: 
1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on GitHub
3. Contact the development team

---

## Quick Reference Commands

```bash
# Start application
docker compose up -d --build

# Stop application
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps

# Restart backend only
docker compose restart backend

# Full cleanup (removes all data!)
docker compose down -v
docker system prune -af
```

---

## Version Information

- **Application Version**: 1.0.0
- **CopyKAT Version**: Latest from Bioconductor
- **Docker Compose Version**: 3.8

---

*Last Updated: November 2024*


