export interface AnalysisRequest {
  input_file: string;
  sample_name: string;
  output_dir: string;
  genome: "hg20" | "mm10";
  ngene_chr?: number;
  LOW_DR?: number;
  UP_DR?: number;
  win_size?: number;
  KS_cut?: number;
  distance?: "euclidean" | "pearson" | "spearman";
  n_cores?: number;
  cell_line?: "yes" | "no";
  plot_genes?: boolean;
  norm_cell_names?: string[];
}

export interface SummaryStats {
  n_cells: number;
  n_aneuploid?: number;
  n_diploid?: number;
  n_not_defined?: number;
  aneuploid_fraction?: number;
  mean_confidence?: number;
}

export interface FilePaths {
  predictions?: string;
  cna_results?: string;
  cna_raw?: string;
  heatmap?: string;
  heatmap_genes?: string;
  clustering?: string;
  report?: string;
  log?: string;
}

export interface AnalysisResponse {
  success: boolean;
  timestamp?: string;
  output_dir?: string;
  sample_name?: string;
  files: FilePaths;
  summary: SummaryStats;
  runtime_minutes: number;
  error?: string;
  warnings: string[];
  stdout?: string;
  stderr?: string;
}

export interface UploadResponse {
  filename: string;
  path: string;
  message: string;
}

