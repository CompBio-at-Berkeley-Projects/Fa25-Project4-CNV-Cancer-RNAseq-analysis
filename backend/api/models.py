from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum

class Genome(str, Enum):
    hg20 = "hg20"
    mm10 = "mm10"

class DistanceMetric(str, Enum):
    euclidean = "euclidean"
    pearson = "pearson"
    spearman = "spearman"

class CellLine(str, Enum):
    yes = "yes"
    no = "no"

class AnalysisRequest(BaseModel):
    input_file: str = Field(..., description="Path to expression matrix file")
    sample_name: str = Field(..., pattern="^[a-zA-Z0-9_]+$", min_length=1, max_length=50)
    output_dir: str = Field(..., description="Base output directory path")
    genome: Genome = Field(..., description="Reference genome version")
    ngene_chr: int = Field(5, ge=1, le=20, description="Minimum genes per chromosome")
    LOW_DR: float = Field(0.05, ge=0.01, le=0.50, description="Detection rate for smoothing")
    UP_DR: float = Field(0.10, ge=0.01, le=0.50, description="Detection rate for segmentation")
    win_size: int = Field(25, ge=10, le=150, description="Window size in number of genes")
    KS_cut: float = Field(0.10, ge=0.05, le=0.40, description="KS test cutoff")
    distance: DistanceMetric = Field(DistanceMetric.euclidean, description="Distance metric")
    n_cores: int = Field(4, ge=1, le=64, description="Number of CPU cores")
    cell_line: CellLine = Field(CellLine.no, description="Is sample a pure cell line?")
    plot_genes: bool = Field(True, description="Show gene names in heatmap")
    norm_cell_names: List[str] = Field(default=[], description="Known normal cell names")

    @field_validator('UP_DR')
    @classmethod
    def validate_up_dr(cls, v, info):
        if info.data.get('LOW_DR') and v < info.data['LOW_DR']:
            raise ValueError('UP_DR must be >= LOW_DR')
        return v
