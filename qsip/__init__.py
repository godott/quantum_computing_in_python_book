"""
QSIP - Quantum Stack in Python
A pure Python implementation of quantum computing concepts for educational purposes.
"""

__version__ = "0.1.0"
__author__ = "Yunong Shi"
__email__ = "your.email@example.com"

# Import key components for easy access
from qsip.visualization.bloch import Bloch, QuantumState

# Import translator (with graceful fallback if openqasm3 not installed)
try:
    from qsip.translators import print_tex, print_qtz
    _TRANSLATOR_AVAILABLE = True
except ImportError:
    _TRANSLATOR_AVAILABLE = False
    print_tex = None
    print_qtz = None

__all__ = [
    "Bloch",
    "QuantumState", 
    "__version__",
]

# Add translator functions to __all__ only if available
if _TRANSLATOR_AVAILABLE:
    __all__.extend(["print_tex", "print_qtz"])