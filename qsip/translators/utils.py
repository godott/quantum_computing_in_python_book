"""Utility functions for the translators module."""

import os
import platform


def setup_latex_path():
    """
    Setup PATH environment variable to include LaTeX binaries.
    
    This function should be called before using print_qtz with latex=False
    if you're having trouble with pdflatex not being found.
    """
    if platform.system() == 'Darwin':  # macOS
        # Common LaTeX installation paths on macOS
        latex_paths = [
            '/Library/TeX/texbin',
            '/usr/local/texlive/2025/bin/universal-darwin',
            '/usr/local/texlive/2024/bin/universal-darwin',
            '/usr/local/texlive/2023/bin/universal-darwin',
            '/opt/local/bin',  # MacPorts
            '/usr/local/bin',  # Homebrew
        ]
        
        current_path = os.environ.get('PATH', '')
        for latex_path in latex_paths:
            if os.path.exists(latex_path) and latex_path not in current_path:
                os.environ['PATH'] = f"{latex_path}:{current_path}"
                break
    elif platform.system() == 'Linux':
        # Common LaTeX paths on Linux
        latex_paths = [
            '/usr/local/texlive/2025/bin/x86_64-linux',
            '/usr/local/texlive/2024/bin/x86_64-linux',
            '/usr/bin',
        ]
        
        current_path = os.environ.get('PATH', '')
        for latex_path in latex_paths:
            if os.path.exists(latex_path) and latex_path not in current_path:
                os.environ['PATH'] = f"{latex_path}:{current_path}"
                break


def check_latex_installation():
    """Check if LaTeX is properly installed and accessible."""
    import subprocess
    
    checks = {
        'pdflatex': False,
        'quantikz': False,
        'tikz': False,
    }
    
    # Check pdflatex
    try:
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            checks['pdflatex'] = True
            print(f"✓ pdflatex found: {result.stdout.split()[1]}")
    except FileNotFoundError:
        # Try with full path
        for path in ['/Library/TeX/texbin/pdflatex']:
            if os.path.exists(path):
                checks['pdflatex'] = True
                print(f"✓ pdflatex found at: {path}")
                break
    
    if not checks['pdflatex']:
        print("✗ pdflatex not found")
        print("  Install with: brew install --cask mactex")
    
    # Check for packages
    if checks['pdflatex']:
        try:
            result = subprocess.run(['kpsewhich', 'quantikz.sty'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                checks['quantikz'] = True
                print("✓ quantikz package found")
        except:
            pass
        
        if not checks['quantikz']:
            print("✗ quantikz package not found")
            print("  Install with: sudo tlmgr install quantikz")
    
    return all(checks.values())