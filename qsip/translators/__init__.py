"""Quantum circuit translators for qsip."""

from .openqasm_to_quantikz import print_tex
from .utils import setup_latex_path, check_latex_installation

# Keep print_qtz as alias for backward compatibility
print_qtz = print_tex

__all__ = ['print_tex', 'print_qtz', 'setup_latex_path', 'check_latex_installation']