# QSIP - Quantum Stack in Python

A pure Python implementation of quantum computing concepts for educational purposes, accompanying the book "Build a Quantum Stack in Python".

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/godott/quantum-book.git
cd quantum-book

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[notebook]"

# Install with OpenQASM3 translator support
pip install -e ".[translators]"
```

### Package Installation

```bash
pip install qsip
```

## Quick Start

```python
from qsip import Bloch, QuantumState
import numpy as np

# Create a Bloch sphere visualization
bloch = Bloch()

# Create a quantum state |+⟩ = (|0⟩ + |1⟩)/√2
plus_state = QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])

# Add the state to the Bloch sphere
bloch.add_states(plus_state.to_bloch_vector())

# Display the sphere
bloch.show()
```

### OpenQASM3 to Quantikz Translation

```python
from qsip import print_qtz

# Define a quantum circuit in OpenQASM3
qasm_circuit = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;
"""

# Get LaTeX code for quantikz
latex_code = print_qtz(qasm_circuit, latex=True)
print(latex_code)

# Or save directly to PDF (requires LaTeX)
# print_qtz(qasm_circuit, save_fig=True, filename="bell_state.pdf")
```

## Features

- **Pure Python Implementation**: No external quantum computing libraries required
- **Educational Focus**: Clear, understandable code for learning quantum concepts
- **Visualization Tools**: Bloch sphere visualization for single qubit states
- **Circuit Translation**: OpenQASM3 to quantikz LaTeX converter for circuit diagrams
- **Quantum Gates**: Implementation of basic quantum gates (coming soon)
- **Algorithms**: Classic quantum algorithms (coming soon)

## Project Structure

```
qsip/
├── __init__.py
├── visualization/      # Visualization tools
│   ├── __init__.py
│   └── bloch.py       # Bloch sphere implementation
├── translators/       # Circuit format translators
│   ├── __init__.py
│   ├── openqasm_to_quantikz.py  # OpenQASM3 to quantikz converter
│   └── README.md      # Translator documentation
├── gates/             # Quantum gates (coming soon)
│   └── __init__.py
├── algorithms/        # Quantum algorithms (coming soon)
│   └── __init__.py
└── utils/            # Utility functions
    └── __init__.py
```

## Documentation

Full documentation and the accompanying book are available at: https://godott.github.io/quantum-book/

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Yunong Shi

## Acknowledgments

This package is part of the "Build a Quantum Stack in Python" educational project.