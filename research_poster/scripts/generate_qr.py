import qrcode
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_qr():
    repo_url = "https://github.com/CBB-Fa25/Project4-CNV-Cancer-RNAseq-analysis"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(repo_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    output_path = OUTPUT_DIR / "repo_qr.png"
    img.save(output_path)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_qr()


