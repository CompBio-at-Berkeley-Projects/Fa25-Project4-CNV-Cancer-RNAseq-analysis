import os
import sys
import subprocess
import graphviz
from pathlib import Path
from PIL import ImageFont, Image
import PIL

# Patch Pillow < 10 compatibility for seqdiag
if not hasattr(ImageFont.FreeTypeFont, 'getsize'):
    def getsize(self, text, direction=None, features=None):
        bbox = self.getbbox(text, direction, features)
        if bbox is None:
            return 0, 0
        left, top, right, bottom = bbox
        return right - left, bottom - top
    ImageFont.FreeTypeFont.getsize = getsize

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS


from seqdiag.command import SeqdiagApp

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_bio_context():
    """Generates the Biological Context diagram using Graphviz."""
    dot = graphviz.Digraph(comment='Biological Context', format='png')
    dot.attr(rankdir='TB', splines='ortho', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='white', fontname='Helvetica')
    
    # Nodes
    dot.node('A', 'Single Cell\nRNA-seq Data', shape='cylinder', fillcolor='#ecf0f1')
    dot.node('B', 'Analyze Genome\n(CopyKAT)', shape='diamond', fillcolor='#f1c40f')
    
    dot.node('C', 'Normal Cells\n(Diploid)', fillcolor='#3498db', fontcolor='white')
    dot.node('D', 'Cancer Cells\n(Aneuploid)', fillcolor='#e74c3c', fontcolor='white')
    
    dot.node('E', 'Immune /\nStromal Cells', style='dashed')
    dot.node('F', 'Tumor\nSubclones', style='bold')

    # Edges
    dot.edge('A', 'B')
    dot.edge('B', 'C', label=' 2n (Stable)')
    dot.edge('B', 'D', label=' CNVs (Unstable)')
    dot.edge('C', 'E')
    dot.edge('D', 'F')

    output_path = OUTPUT_DIR / 'bio_context'
    dot.render(output_path, cleanup=True)
    print(f"Generated {output_path}.png")

def generate_architecture():
    """Generates the System Architecture diagram using Graphviz."""
    dot = graphviz.Digraph(comment='System Architecture', format='png')
    dot.attr(rankdir='LR', splines='ortho', dpi='300')
    dot.attr('node', shape='box', style='filled', fontname='Helvetica')

    # User
    dot.node('User', 'User\n(Browser)', shape='ellipse', fillcolor='#ecf0f1')

    # Docker Container Subgraph
    with dot.subgraph(name='cluster_docker') as c:
        c.attr(label='Docker Environment', style='rounded,dashed', color='#7f8c8d', bgcolor='#f9f9f9')
        
        # Frontend
        with c.subgraph(name='cluster_fe') as fe:
            fe.attr(label='Frontend Container', color='#3498db', bgcolor='white')
            fe.node('React', 'React App\n(UI)', fillcolor='#e1f5fe')
            fe.node('Nginx', 'Nginx\n(Server)', fillcolor='#e1f5fe')
            fe.edge('Nginx', 'React')

        # Backend
        with c.subgraph(name='cluster_be') as be:
            be.attr(label='Backend Container', color='#2ecc71', bgcolor='white')
            be.node('FastAPI', 'FastAPI\n(Python)', fillcolor='#e8f5e9')
            be.node('R', 'R Engine\n(CopyKAT)', fillcolor='#e8f5e9')
            be.node('FS', 'File System\n(Results)', shape='folder', fillcolor='#fff3e0')
            
            be.edge('FastAPI', 'R', label=' subprocess')
            be.edge('R', 'FS', label=' I/O')
            be.edge('FastAPI', 'FS', label=' Read')

    # Edges between clusters
    dot.edge('User', 'Nginx', label=' HTTP :3000')
    dot.edge('Nginx', 'FastAPI', label=' /api (Proxy)')

    output_path = OUTPUT_DIR / 'architecture'
    dot.render(output_path, cleanup=True)
    print(f"Generated {output_path}.png")

def generate_data_flow():
    """Generates the Data Flow diagram using seqdiag."""
    diag_content = """
    seqdiag {
        activation = none;
        node_width = 120;
        node_height = 40;
        span_width = 60;
        span_height = 20;
        default_fontsize = 14;
        edge_length = 250;

        User; UI [label="React UI", color="#3498db", textcolor="white"]; API [label="FastAPI", color="#2ecc71"]; R [label="R Script", color="#f1c40f"]; FS [label="File System", shape="box"];

        User -> UI [label = "Upload Data"];
        UI -> API [label = "POST /analyze"];
        API -> R [label = "Spawn Process"];
        R -> FS [label = "Read Input"];
        R -> R [label = "Run CopyKAT"];
        R -> FS [label = "Save Results"];
        R --> API [label = "Exit Code 0"];
        API -> FS [label = "Parse Output"];
        API --> UI [label = "JSON Response"];
        UI -> User [label = "Display Heatmap"];
    }
    """
    
    diag_path = OUTPUT_DIR / 'data_flow.diag'
    png_path = OUTPUT_DIR / 'data_flow.png'
    
    with open(diag_path, 'w') as f:
        f.write(diag_content)
        
    try:
        # Run seqdiag via Python API to use the patched PIL
        args = ['-a', '-Tpng', str(diag_path), '-o', str(png_path)]
        app = SeqdiagApp()
        # capture stdout/stderr to avoid noise if needed, but simple run is fine
        ret = app.run(args)
        if ret == 0:
            print(f"Generated {png_path}")
        else:
            print(f"seqdiag failed with exit code {ret}")
    except Exception as e:
        print(f"Error generating data flow diagram: {e}")
    finally:
        if diag_path.exists():
            os.remove(diag_path)

if __name__ == "__main__":
    print("Generating diagrams...")
    try:
        generate_bio_context()
        generate_architecture()
        generate_data_flow()
        print("Done.")
    except Exception as e:
        print(f"Failed to generate diagrams: {e}")

