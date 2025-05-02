# OBJ to GLB Converter (PyQt5 GUI)

This project provides a user-friendly PyQt5-based desktop application for converting `.obj` 3D model files (along with optional `.mtl` and texture files) into the `.glb` (GLTF Binary) format. It supports vertex colors if present in the OBJ file and handles associated material and texture files by maintaining relative paths during conversion.

## Features

- **Drag-and-Drop Interface**: Easily drop `.obj`, `.mtl`, and texture files into the GUI.
- **GLB Conversion**: Converts to `.glb` using the `trimesh` library.
- **Vertex Color Support**: Preserves vertex colors if available in the input.
- **Standalone GUI**: No command-line knowledge required.
- **Cross-Platform**: Runs on Windows, macOS, and Linux.

## Screenshots

![App Screenshot](screenshot.png)

## Installation

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install PyQt5 trimesh pygltflib
```

## Usage

Run the application:

```bash
python obj_to_glb_converter.py
```

Then drag your OBJ, MTL, and texture files into the window and click "Convert to GLB".

## License

This project is licensed under the MIT License.

## Acknowledgments

- [PyQt5](https://pypi.org/project/PyQt5/)
- [Trimesh](https://trimsh.org/)
- [glTF](https://www.khronos.org/gltf/)
