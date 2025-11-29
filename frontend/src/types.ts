export enum Genome {
    hg20 = "hg20",
    mm10 = "mm10"
}

export enum DistanceMetric {
    euclidean = "euclidean",
    pearson = "pearson",
    spearman = "spearman"
}

export enum CellLine {
    yes = "yes",
    no = "no"
}

export interface AnalysisRequest {
    input_file: string;
    sample_name: string;
    output_dir: string;
    genome: Genome;
    ngene_chr: number;
    LOW_DR: number;
    UP_DR: number;
    win_size: number;
    KS_cut: number;
    distance: DistanceMetric;
    n_cores: number;
    cell_line: CellLine;
    plot_genes: boolean;
    norm_cell_names: string[];
}

export interface AnalysisResult {
    success: boolean;
    output_dir: string | null;
    files: {
        predictions?: string;
        cna_results?: string;
        heatmap?: string;
        log?: string;
        report?: string;
    };
    summary: {
        n_cells: number;
        n_aneuploid: number;
        n_diploid: number;
        n_not_defined: number;
        aneuploid_fraction: number;
    };
    runtime_minutes: number;
    error: string | null;
    timestamp?: string;
}

export interface FileItemData {
    name: string;
    path: string;
    type: 'raw' | 'uploaded';
}



