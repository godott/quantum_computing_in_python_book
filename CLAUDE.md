# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jupyter Book project titled "Build A Quantum Computing Stack in Python" that teaches quantum computing by building implementations from scratch without relying on external quantum libraries.

## Commands

### Build the book
```bash
jupyter-book build .
```

### Clean build artifacts
```bash
jupyter-book clean .
```

### Run local development server
```bash
cd _build/html && python -m http.server 8000
```

### Install the package
```bash
pip install -e .  # Install in development mode
```

### Run Python examples
```bash
python bloch_example.py  # Generates Bloch sphere visualizations in bloch_outputs/
```

### Run Jupyter notebooks
```bash
jupyter notebook  # Then open any .ipynb file
```

## Architecture

### Core Components

1. **qsip package**: Quantum Stack in Python
   - Pure Python implementation of quantum computing concepts
   - Modular structure with visualization, gates, algorithms, and utils
   - Main visualization component: `qsip.visualization.bloch`
   - Generates PNG outputs in `bloch_outputs/`

2. **Jupyter Notebooks**: Interactive tutorials
   - `chapter1.ipynb`: Introduction to quantum computing basics
   - `Quantum_Gates_Lecture.ipynb`: Quantum gate operations
   - `quantum_protocols_lecture.ipynb`: Advanced quantum protocols

3. **Book Structure** (defined in `_toc.yml`):
   - Linear progression from basics to advanced topics
   - Mix of markdown files for theory and notebooks for hands-on coding

### Key Directories

- `_build/`: Generated book output (git-ignored)
- `figures/`: Static images for the book
- `bloch_outputs/`: Generated visualizations from bloch.py
- `.github/workflows/`: GitHub Actions for automated deployment

### Deployment

The book automatically deploys to GitHub Pages via the `static.yml` workflow when changes are pushed to the main branch. The deployment process:
1. Builds the Jupyter Book
2. Adds a `.nojekyll` file to bypass Jekyll processing
3. Deploys to GitHub Pages at https://godott.github.io/quantum-book/

## Development Notes

- No formal testing framework is configured - examples serve as informal tests
- The project builds quantum computing concepts from first principles using only NumPy, SciPy, and Matplotlib
- When modifying notebooks, ensure they execute cleanly as they're run during the build process
- Generated outputs (bloch_outputs/*.png) should be committed as they're referenced in the book content