# Product Requirements Document (PRD): CNV-Cancer-RNAseq-analysis

**Date**: October 1, 2025
**Version**: 1.0 (MVP)
**Author**: Hanson Wen (Only Hanson should edit this document)

## 1. Introduction

This document outlines the product requirements for the **CNV-Cancer-RNAseq-analysis** project. The goal is to create a user-friendly, locally-run application that automates the process of Copy Number Variation (CNV) analysis from single-cell RNA sequencing (scRNA-seq) data. This tool is intended for bioinformatics researchers who need a simple, reproducible way to distinguish malignant cells from non-malignant cells and visualize genomic instability in cancer datasets.

### 1.1. Problem Statement

Analyzing scRNA-seq data to identify CNVs is a powerful method for studying intratumoral heterogeneity and identifying cancer cells. However, the process often involves complex, multi-step bioinformatics pipelines that require significant command-line expertise. This creates a barrier for many wet-lab researchers and makes it difficult to perform simple, repetitive analyses quickly. There is a need for a lightweight, interactive tool that streamlines this workflow, from data upload to visualization, without requiring deep computational skills.

### 1.2. Project Goals

- **Build a reproducible pipeline**: Create a robust, automated pipeline for CNV inference from scRNA-seq data.
- **Develop an intuitive user interface**: Provide a simple, interactive dashboard that allows users to run the pipeline and visualize results with minimal effort.
- **Ensure scientific validity**: Validate the pipeline against well-annotated public datasets to ensure the results are accurate and reliable.
- **Enable extensibility**: Design the system to support the addition of new datasets and, in the future, alternative analysis tools.

## 2. Product Vision & MVP Scope

### 2.1. Product Vision

To become a standard, easy-to-use tool for cancer researchers to perform initial CNV analysis on scRNA-seq data, enabling rapid identification of malignant cell populations and exploration of intratumoral genomic heterogeneity.

### 2.2. MVP Scope

The Minimum Viable Product (MVP) will focus on delivering the core functionality of the pipeline and dashboard. The scope is designed to be achievable within an 8-week timeframe by a small team of students with basic-to-intermediate programming skills.

**The MVP will include:**

- A locally-running interactive web application.
- Support for uploading user-provided scRNA-seq expression data (in a specified format).
- A single-click button to execute the CNV analysis pipeline.
- A pipeline that uses **CopyKAT** for CNV inference and cell classification.
- Visualization of the results, including a CNV heatmap and a summary of cell classifications.
- The ability to download the results (plots and tables).
- Validation of the pipeline using the provided melanoma dataset (`GSE72056`).
- A comprehensive set of documentation, including a user guide and a `README` file.

**Out of scope for the MVP:**

- Integration of `inferCNV` or other CNV callers.
- Support for multiple input data formats.
- Advanced interactive plotting features (e.g., zooming, panning).
- User authentication or multi-user support.
- Deployment to a public web server.

## 3. User Personas

### 3.1. Primary User: Dr. Evelyn Reed, Bioinformatics Researcher

- **Background**: Evelyn is a postdoctoral researcher in a cancer biology lab. She has a strong background in biology but only basic programming skills in R and Python. She is comfortable running existing scripts but not developing new pipelines from scratch.
- **Goals**: Evelyn wants to quickly analyze new scRNA-seq datasets from her experiments to identify which cells are cancerous and get a general sense of the genomic instability in her samples. She needs to do this frequently and doesn't have the time to learn complex command-line tools.
- **Frustrations**: She finds it tedious to manage dependencies and run multi-step workflows in the terminal. She often has to ask for help from the bioinformatics core, which can be slow.
- **Needs**: A simple, all-in-one tool where she can upload her data, click a button, and get back publication-quality plots and tables.

## 4. Functional Requirements

| Feature ID | Feature Name | Description | Priority |
| :--- | :--- | :--- | :--- |
| F-01 | Data Upload | The user shall be able to upload a gene expression matrix file (e.g., as a `.txt` or `.csv` file) and an optional cell annotation file through the web interface. | Must-have |
| F-02 | Pipeline Execution | The user shall be able to start the CNV analysis pipeline by clicking a single "Run Analysis" button. | Must-have |
| F-03 | Status Updates | The application shall display the current status of the pipeline (e.g., "Preprocessing", "Running CopyKAT", "Generating plots", "Done"). | Must-have |
| F-04 | CNV Heatmap Visualization | The application shall display a heatmap of inferred CNVs across the genome for all cells, similar to the output of `CopyKAT`. | Must-have |
| F-05 | Cell Classification Summary | The application shall display a summary of the cell classifications (e.g., a table or bar chart showing the number of diploid, aneuploid, etc. cells). | Must-have |
| F-06 | Results Download | The user shall be able to download the generated plots (as PNG) and the cell classification table (as CSV). | Must-have |
| F-07 | Static Report Generation | The user shall be able to download a static HTML or PDF report containing all the results and visualizations. | Should-have |
| F-08 | Validation Mode | The pipeline shall have a mode to run on the melanoma dataset and compare its output to the author-provided classifications, reporting the concordance. | Must-have |

## 5. Technical Architecture

### 5.1. Hybrid Python/R Architecture

The system will use a hybrid architecture that leverages the strengths of both Python and R.

- **Python (Streamlit)**: Will be used for the frontend web application. Streamlit is an excellent choice for this project as it allows for the rapid development of interactive UIs with minimal code, making it ideal for the student team.
- **R (CopyKAT)**: Will be used for the core CNV analysis. `CopyKAT` is a robust and well-regarded R package specifically designed for this purpose. Since it is written in R, the pipeline will call an R script from the Python backend.

### 5.2. Data Flow

1.  **Upload**: The user uploads the expression matrix via the Streamlit frontend.
2.  **Preprocessing (Python)**: The Python backend receives the file and performs any necessary preprocessing (e.g., formatting the data into the required input for `CopyKAT`).
3.  **CNV Analysis (R)**: The Python backend uses the `subprocess` module to call a dedicated R script, passing the path to the preprocessed data. The R script runs `CopyKAT` and saves the output (plots and tables) to a results directory.
4.  **Visualization (Python)**: Once the R script is complete, the Streamlit frontend reads the output files from the results directory and displays them in the UI.
5.  **Download**: The user can download the output files directly from the Streamlit UI.

## 6. Validation & Quality Metrics

### 6.1. Validation Strategy

The pipeline's accuracy will be validated using the **melanoma dataset (GSE72056)**, which contains pre-existing CNV-based cell classifications. The pipeline will be run on this dataset, and the resulting cell classifications will be compared to the author-provided classifications.

### 6.2. Quality Metric

The primary quality metric will be **concordance**, defined as the percentage of cells that are classified the same way by both our pipeline and the original authors. 

`Concordance = (Number of cells with matching classification) / (Total number of cells)`

**Success Criterion**: The MVP will be considered successful if the pipeline achieves a concordance of **>90%** on the melanoma dataset.

## 7. 8-Week Implementation Roadmap

This roadmap breaks down the project into weekly milestones for the 8-week duration (October 1 - November 30).

| Week | Dates | Key Tasks & Milestones | Goals |
| :--- | :--- | :--- | :--- |
| 1 | Oct 1 - Oct 7 | **Setup & Initial Pipeline**: <br>- Set up Git repository and project structure. <br>- Create Conda/virtual environments for Python and R. <br>- Write a basic R script to run `CopyKAT` on the glioblastoma data. | Have a working, command-line version of the `CopyKAT` pipeline. |
| 2 | Oct 8 - Oct 14 | **Basic Streamlit UI**: <br>- Build a simple Streamlit app with a title and placeholder sections. <br>- Implement the file upload feature. <br>- Add the "Run Analysis" button. | A user can upload a file, but the button doesn't do anything yet. |
| 3 | Oct 15 - Oct 21 | **Integrate Pipeline & UI**: <br>- Connect the "Run Analysis" button to the R script using `subprocess`. <br>- Display the status of the pipeline in the UI. <br>- Ensure the pipeline runs successfully when triggered from the UI. | The core end-to-end flow is working: upload -> run -> complete. |
| 4 | Oct 22 - Oct 28 | **Display Results**: <br>- Read the output plots and tables from the results directory. <br>- Display the CNV heatmap and classification summary in the Streamlit app. | The user can see the results of the analysis in the web interface. |
| 5 | Oct 29 - Nov 4 | **Validation & Refinement**: <br>- Implement the validation mode for the melanoma dataset. <br>- Calculate and display the concordance score. <br>- Refine the pipeline parameters based on the validation results to meet the >90% goal. | The pipeline is scientifically validated and meets the quality standard. |
| 6 | Nov 5 - Nov 11 | **Downloads & Reporting**: <br>- Implement the download buttons for plots and tables. <br>- Develop the static HTML/PDF report generation feature. | The user can export all results from the application. |
| 7 | Nov 12 - Nov 18 | **Documentation**: <br>- Write the `README.md` file with detailed setup and usage instructions. <br>- Write a comprehensive User Guide for non-technical users. <br>- Add comments and docstrings to the code. | The project is well-documented and easy for new users to understand. |
| 8 | Nov 19 - Nov 25 | **Final Polish & Testing**: <br>- Thoroughly test the application for bugs. <br>- Improve the UI/UX based on feedback. <br>- Prepare the final presentation/deliverable. | A polished, robust, and well-documented MVP is complete. |

## 8. Documentation Requirements

- **`README.md`**: A detailed file in the root of the repository that includes:
    - Project overview.
    - Step-by-step installation instructions for all dependencies (Python, R, and packages).
    - Instructions on how to run the application.
- **User Guide**: A separate document (e.g., a PDF or a dedicated page in the app) that explains how to use the application from a non-technical user's perspective. It should include screenshots and explain what each part of the output means.
- **Code Documentation**: All code should be well-commented, and functions should have clear docstrings explaining their purpose, arguments, and return values.

## 9. Future Work (Post-MVP)

- **`inferCNV` Integration**: Add `inferCNV` as an alternative analysis option, allowing users to generate more detailed chromosomal heatmaps.
- **Expanded Data Support**: Add support for more input formats, such as `AnnData` objects or data from 10x Genomics.
- **Interactive Visualizations**: Replace static plots with interactive versions using libraries like `Plotly`.
- **Comparative Analysis**: Allow users to compare CNV patterns across multiple samples or datasets within the application.


# 1) Architecture split (replace “Technical Architecture” header)

## Runtime Topology

* **Realtime (Edge, in-browser only):**

  * Inputs: webcam frames; optional screen frames (via `getDisplayMedia`).
  * Ops: image-only inference for posture, activity, and screen-content classification. No LLM/VLM calls. No cloud I/O.
  * Outputs: timestamped event stream (focus/distract, posture state, active app class), in-memory + IndexedDB ring buffer; optional low-freq thumbnails for local audit only.
* **Post-Processing (End-of-session, cloud):**

  * Inputs: two MP4s saved locally—`cam.mp4` (user) and `screen.mp4` (display)—default 480p, configurable bitrate.
  * Upload targets: **Memories.ai** (primary) + **Hume AI** (expression timeline).
  * Ops: Memories Chat API runs LLM/VLM over the two videos to extract structured session summaries; Hume produces expression tracks.
  * Outputs: normalized JSON report (schema below) persisted in backend DB; links to Memories objects; expression timeline merged.

## Data Flow Summary

1. **Session start:** user grants camera; optional screen share; choose quality profile.
2. **Realtime loop:** CV-only metrics at 1–5 Hz; UI nudges; ring buffer retention; zero network.
3. **Session end:** stop capture; finalize two MP4s; upload; trigger post-processing jobs; generate report; sync to dashboard.

# 2) Realtime module (new subsection under “Functional Requirements”)

## FR1a. Realtime CV Pipeline (Edge)

* **Frame cadence:** 1–5 Hz webcam; 0.2–1 Hz screen snapshot; both downscaled to target (default 480p, min 256p).
* **Posture:** MediaPipe BlazeFace/FaceMesh + head-pose; optional BlazePose upper-body. States: {neutral, slouch, head-down, head-away, out-of-frame, micro-sleep}.
* **Activity:** heuristics on motion vectors + face/eye features; classify {focused, reading, typing-like, phone-likely, talking, absent}.
* **Screen content (image classification, not OCR):** window archetypes via lightweight CNN (e.g., ONNX Runtime Web): {IDE/docs/terminal/slides/video/short-video/social/feed/chat/games/unknown}.
* **Fusion:** hysteresis state machine with debounce (≥5 s) to reduce false positives; emits `focus_event` and `distract_event` with reason codes.
* **Edge budgets:** CPU avg <30%; memory <300 MB; auto-throttle frame rate on perf drop.

## FR1b. Realtime Storage & Privacy

* No raw frames leave device.
* Ring buffer: last N thumbnails (default N=0; off by default).
* IndexedDB: transient event stream; auto-purge after upload.
* Controls: Pause, Sensitivity slider, Screen-capture toggle.

# 3) Post-processing pipeline (new subsection under “Functional Requirements”)

## FR7. End-of-Session Upload & Jobs

* **Recording:** two local files—`cam.mp4`, `screen.mp4`; container MP4/H.264; default 480p@15fps; VBR target 300–800 kbps (config: Low/Std/High).
* **Upload order:** (1) Memories.ai objects `{cam, screen}`; (2) Hume video expression analysis on `cam`.
* **Jobs:**

  * **Memories Chat API Prompt:** “Given `cam` and `screen`, segment the work session; infer task phases, app classes, distraction intervals, triggers, break taxonomy; extract step-level actions; output in schema v1.2.”
  * **Hume Expressions:** derive time-series for valence, arousal, stress, frustration; resample to 1 Hz; align to segments.
  * **Merger:** join on timestamps; compute per-segment KPIs; persist `session_report.json`.

## FR7a. Structured Output Schema (v1.2)

```json
{
  "session_id": "uuid",
  "meta": { "started_at": "iso", "ended_at": "iso", "profile": "Low|Std|High" },
  "segments": [
    {
      "t0":"s","t1":"s","label":"Focus|Break|Admin|Setup",
      "task_hypothesis":"string",
      "apps":[{"class":"IDE|Docs|Browser|Video|Social|Chat|Slides|Terminal|Unknown","share":0.0}],
      "distractions":[{"t0":"s","t1":"s","type":"LookAway|Phone|Video|Social|Chat|Noise","evidence":"string"}],
      "posture":{"mode":"Neutral|Slouch|HeadAway|Down|Absent","pct":0.0},
      "expressions":{"frustration_mean":0.0,"valence_mean":0.0,"arousal_mean":0.0}
    }
  ],
  "kpis":{
    "focus_ratio":0.0,"avg_focus_bout_min":0.0,"num_alerts":0,
    "top_triggers":["Video","Phone","HeadAway"],"peak_distraction_hour":"15:00-16:00"
  },
  "recommendations":[{"type":"BreakSchedule|AppBlock|TaskSplit|Ergonomics","msg":"string"}],
  "artifacts":{"memories_urls":{"cam":"url","screen":"url"},"hume_job_id":"string"}
}
```

# 4) UX changes (append to “Minimal Setup & Web-Based UX”)

* **Quality presets:** Low (256p/10fps/200 kbps), Standard (480p/15fps/500 kbps), High (720p/15fps/1000 kbps).
* **Screen capture scope:** full screen or single window; default: single window.
* **Session end modal:** show file sizes estimate; toggle “Upload now / Defer”; show privacy note (“raw video stored locally until upload; deleted after successful processing if ‘Auto-delete’ is on”).
* **Reports tab:** render `session_report.json` timeline; filters by segment, trigger, posture; export CSV/JSON.

# 5) Tech stack deltas (append to “Tech Stack Considerations”)

* **Recording:** `MediaRecorder` for MP4/H.264; mux webcam and display into separate streams; fallback WebM/VP9 in Safari → transcode client-side via FFmpeg.wasm if needed (batch, post-session).
* **Realtime CV:** MediaPipe FaceMesh/BlazePose via TF.js or ONNX Runtime Web; head-pose (PnP on landmarks) via OpenCV.js; small CNN for screen archetypes (~3–5M params, int8).
* **Post-proc calls:**

  * **Memories.ai:** Upload two assets; invoke Chat API with schema prompt; poll job; fetch JSON.
  * **Hume:** Video expression endpoint; poll; fetch 1 Hz tracks.
* **Backend:** thin Node/Express proxy for API keys + webhook receivers; Postgres for `session_report` storage; signed URLs to artifacts; no raw media retention after confirm.
* **Workers:** Web Workers for realtime CV; background `fetch()` with `keepalive` for uploads.

# 6) Privacy, retention, and bandwidth (new subsection under “Non-Functional Requirements”)

* **Default retention:** raw `cam.mp4` and `screen.mp4` deleted after successful upload + report merge; retention window configurable (0, 24h, 7d).
* **Local-only mode:** skip uploads; produce local report using cached embeddings/thumbnails only; disables Hume and Memories features.
* **Bandwidth caps:** hard cap per session (e.g., 300 MB) with adaptive transcode before upload; warn user if projected size exceeds cap.
* **Auditability:** user can preview clips tied to flagged distraction intervals before upload.

# 7) Evals and ablations (map to rubric; add under “Objectives & Success Metrics” or separate “Evals”)

* **Latency eval:** alert time (event→nudge) p95 < 1.5 s.
* **Accuracy eval:** posture confusion matrix; screen archetype F1 ≥ 0.85 on held-out clip set.
* **Ablation:** disable posture; measure Δfocus_ratio; disable screen archetype; measure Δfalse-positives; show charts in README.
* **Load test:** 2-hour session on mid-tier laptop; CPU mean <30%, dropped-frame rate <10%.
* **Cost awareness:** per session API cost target <$0.05 at Std profile (Memories + Hume), with sampling gates.

# 8) Agentic behavior hooks (append under “Goal Management and Agentic Assistance”)

* **Realtime hooks:** if `distract_event` count ≥ N in 20 min, auto-suggest micro-break; if `screen:video` appears during focus, prompt to switch back; if posture “Slouch/HeadDown” >60% of last 10 min and frustration↑, suggest posture reset + 2-min reset.
* **Post-proc hooks:** recommendations generated from `session_report.kpis` + rules; offer one-click plan (Pomodoro length, blocklist suggestion, break slots).

# 9) API contracts (new appendix)

### POST /api/session/start

* Body: `{ quality:"Low|Std|High", screen:true|false }`
* Resp: `{ session_id }`

### POST /api/session/end

* Body: `{ session_id, metrics:{…} }`
* Side effects: initiate uploads; return job ids.

### POST /api/upload

* Multipart: `cam.mp4`, `screen.mp4`, `session_id`
* Resp: `{ memories_ids:{cam,screen} }`

### POST /api/process

* Body: `{ session_id, memories_ids, hume_job_id? }`
* Resp: `{ report_url, status }`

### GET /api/report/:session_id

* Resp: `session_report.json`

# 10) Sequence diagrams (textual; add as appendix)

**Realtime**

```
User -> WebApp: Start session
WebApp -> Camera/Screen: getUserMedia/getDisplayMedia
WebApp (Worker): CV loop (posture/activity/screen-class) @ 1–5 Hz
Worker -> UI: events (focus/distract) with reasons
UI -> User: nudges (debounced)
```

**Post-processing**

```
User -> WebApp: End session
WebApp: finalize cam.mp4 + screen.mp4
WebApp -> Backend: upload(cam, screen)
Backend -> Memories.ai: store assets
Backend -> Hume: submit cam.mp4 for expressions
Backend: poll jobs, merge outputs -> session_report.json
Backend -> WebApp: report ready
```

# 11) Risks deltas (append to “Risks & Open Issues”)

* **Recording compatibility:** MP4/H.264 availability varies by browser; include WebM fallback + optional client-side transcode.
* **Upload size/time:** long sessions produce large files; enforce caps, chunked uploads, resumable transport; expose ETA.
* **Memories/Hume quotas:** enforce sampling and profile presets; backoff on 429; queue jobs.
* **LLM hallucination in post-proc:** constrain with strict schema; add validation; surface “confidence” per field.

# 12) README/demo checklist (for “Completeness & Reliability”)

* One-command setup (pnpm + env template).
* Demo script: 10-min session; end; show report.
* Evals notebook: latency, CPU, F1, ablations.
* Privacy doc: data paths, toggles, retention table.

This integration preserves your original privacy stance, meets hackathon rubric criteria (architecture clarity, autonomy, memory, affect, evals), and bounds complexity by pushing LLM/VLM to post-processing while keeping realtime edge CV lightweight.
