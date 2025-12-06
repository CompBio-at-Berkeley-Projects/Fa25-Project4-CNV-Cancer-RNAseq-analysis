# API Documentation

## Base URL
`http://localhost:8000/api`

## Endpoints

### 1. Upload File
**POST** `/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (File object)
- **Response**:
  ```json
  {
    "filename": "sample.txt.gz",
    "path": "backend/data/uploads/sample.txt.gz"
  }
  ```

### 2. List Files
**GET** `/files`
- **Response**:
  ```json
  [
    {
      "name": "sample.txt.gz",
      "path": "backend/data/uploads/sample.txt.gz",
      "type": "uploaded"
    }
  ]
  ```

### 3. Run Analysis
**POST** `/run`
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "input_file": "path/to/file",
    "sample_name": "sample_001",
    "output_dir": "backend/results",
    "genome": "hg20",
    "n_cores": 4,
    ...
  }
  ```
- **Response**: Analysis Result Object

## Static Files
Results are served at `http://localhost:8000/results/{path}`.

