#!/usr/bin/env python

"""
OBJ-to-GLB/GLTF Converter Tool (via obj2gltf)

Uses the `obj2gltf` CLI to ensure proper MTL and texture embedding
during conversion from OBJ to GLB or GLTF+BIN.

Author: Your Name
Version: 1.1 (with batch conversion)
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from shutil import which

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OBJConverter")

def find_obj2gltf() -> str:
    """
    Finds the obj2gltf executable on the system PATH.

    Returns:
        str: Full path to obj2gltf executable.

    Raises:
        RuntimeError: If obj2gltf is not found.
    """
    path = which("obj2gltf")
    if not path:
        raise RuntimeError(
            "The 'obj2gltf' tool was not found in your PATH.\n"
            "Please install it via npm:\n\n"
            "    npm install -g obj2gltf\n"
        )
    return path

def convert_obj_with_obj2gltf(input_path: Path, output_path: Path, output_format: str) -> None:
    """
    Converts OBJ to GLB or GLTF using the `obj2gltf` tool.

    Args:
        input_path (Path): Path to input .obj file
        output_path (Path): Desired output file (.glb or .gltf)
        output_format (str): Either 'glb' or 'gltf'

    Raises:
        RuntimeError: If obj2gltf fails or is not installed
    """
    obj2gltf_exe = find_obj2gltf()

    if output_format not in {"glb", "gltf"}:
        raise ValueError("Format must be 'glb' or 'gltf'.")

    cmd = [obj2gltf_exe, "-i", str(input_path), "-o", str(output_path)]
    cmd.append("--binary" if output_format == "glb" else "--embed")

    logger.info(f"Running: {' '.join(cmd)}")

    env = os.environ.copy()
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
        logger.info(f"Converted: {input_path.name} → {output_path.name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Conversion failed for {input_path.name}: {e.stderr.strip()}")

def batch_convert(input_dir: Path, output_dir: Path, output_format: str):
    """
    Converts all .obj files in a directory.

    Args:
        input_dir (Path): Directory containing .obj files
        output_dir (Path): Directory to save converted files
        output_format (str): 'glb' or 'gltf'
    """
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error("Input directory does not exist or is not a directory.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    obj_files = list(input_dir.glob("*.obj"))
    if not obj_files:
        logger.warning("No .obj files found in input directory.")
        return

    logger.info(f"Found {len(obj_files)} OBJ files. Starting batch conversion...")
    for obj_file in obj_files:
        out_file = output_dir / obj_file.with_suffix(".glb" if output_format == "glb" else ".gltf").name
        try:
            convert_obj_with_obj2gltf(obj_file, out_file, output_format)
        except Exception as e:
            logger.error(f"Failed to convert {obj_file.name}: {e}")

def run_cli():
    """
    Parses command-line arguments and triggers the conversion.
    """
    parser = argparse.ArgumentParser(description="Convert OBJ files to GLB or GLTF+BIN using obj2gltf")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input', '-i', type=Path, help='Path to input .obj file')
    group.add_argument('--input-dir', type=Path, help='Path to directory of .obj files')

    parser.add_argument('--output', '-o', type=Path, help='Path to output .glb or .gltf file (for single file)')
    parser.add_argument('--output-dir', type=Path, help='Output directory for batch mode')
    parser.add_argument('--format', '-f', required=True, choices=['glb', 'gltf'], help='Output format: glb or gltf')

    args = parser.parse_args()

    if args.input:
        if not args.output:
            logger.error("--output is required when using --input")
            sys.exit(1)
        try:
            convert_obj_with_obj2gltf(args.input, args.output, args.format)
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            sys.exit(1)
    else:
        output_dir = args.output_dir or args.input_dir
        batch_convert(args.input_dir, output_dir, args.format)

class DragDropConverter(QWidget):
    """
    PyQt5 GUI for drag-and-drop conversion of OBJ to GLB/GLTF using obj2gltf.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBJ to GLB/GLTF Converter (obj2gltf)")
        self.setAcceptDrops(True)
        self.resize(400, 250)

        layout = QVBoxLayout()

        self.label = QLabel("Drag and drop an .obj file here")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.button_glb = QPushButton("Convert to GLB")
        self.button_glb.clicked.connect(lambda: self.convert("glb"))
        layout.addWidget(self.button_glb)

        self.button_gltf = QPushButton("Convert to GLTF + BIN")
        self.button_gltf.clicked.connect(lambda: self.convert("gltf"))
        layout.addWidget(self.button_gltf)

        self.button_batch = QPushButton("Batch Folder Conversion")
        self.button_batch.clicked.connect(self.batch_convert_dialog)
        layout.addWidget(self.button_batch)

        self.setLayout(layout)
        self.file_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith('.obj'):
                event.acceptProposedAction()

    def dropEvent(self, event):
        self.file_path = Path(event.mimeData().urls()[0].toLocalFile())
        self.label.setText(f"Selected: {self.file_path.name}")

    def convert(self, fmt: str):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "No file selected.")
            return

        ext = ".glb" if fmt == "glb" else ".gltf"
        out_path_str, _ = QFileDialog.getSaveFileName(self, f"Save {fmt.upper()}", str(self.file_path.with_suffix(ext)), f"{fmt.upper()} files (*{ext})")
        if out_path_str:
            try:
                convert_obj_with_obj2gltf(self.file_path, Path(out_path_str), fmt)
                QMessageBox.information(self, "Success", f"Saved {fmt.upper()} to:\n{out_path_str}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def batch_convert_dialog(self):
        input_dir = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if not input_dir:
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory (optional)") or input_dir

        format_choice = QMessageBox.question(self, "Output Format", "Convert to GLB? (No = GLTF)", QMessageBox.Yes | QMessageBox.No)
        fmt = "glb" if format_choice == QMessageBox.Yes else "gltf"

        batch_convert(Path(input_dir), Path(output_dir), fmt)
        QMessageBox.information(self, "Done", "Batch conversion completed.")

def main():
    """
    Launch CLI or GUI based on whether arguments were passed.
    """
    if len(sys.argv) > 1:
        run_cli()
    else:
        app = QApplication(sys.argv)
        window = DragDropConverter()
        window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
