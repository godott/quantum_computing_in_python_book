# QSIP Circuit Translators

This module provides translators for converting between different quantum circuit representations.

## OpenQASM3 to Quantikz Translator

Convert OpenQASM3 quantum circuits to quantikz LaTeX format for beautiful circuit visualizations.

### Installation

To use the OpenQASM3 translator, install qsip with the translators extra:

```bash
pip install -e ".[translators]"
```

Or install OpenQASM3 separately:

```bash
pip install openqasm3
```

### Quick Start

```python
from qsip import print_tex  # or print_qtz for backward compatibility

# Define a circuit in OpenQASM3
qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;
"""

# Get LaTeX code
latex_code = print_tex(qasm_code, latex=True)
print(latex_code)

# Or save directly to PDF (auto-names file as 'qasm_code.pdf')
print_tex(qasm_code, save_fig=True)

# With custom spacing
print_tex(qasm_code, latex=True, options={"height": "3mm", "width": "5mm"})
```

### Function Reference

#### `print_tex(openqasm_string, latex=False, save_fig=False, filename=None, show=True, border="2pt", options=None)`

Convert OpenQASM3 string to quantikz visualization.

**Parameters:**
- `openqasm_string` (str): OpenQASM3 circuit description
- `latex` (bool): If True, return LaTeX code instead of rendering
- `save_fig` (bool): If True, save the figure to a file
- `filename` (str, optional): Filename for saving the figure. If None and save_fig=True, uses the variable name of openqasm_string
- `show` (bool): If True, display the figure in Jupyter
- `border` (str): Border size around the circuit (e.g., "0pt", "2pt", "1mm")
- `options` (dict, optional): Dictionary of quantikz options:
  - `"height"`: Row separation (e.g., "2mm", "10pt")
  - `"width"`: Column separation (e.g., "2mm", "10pt")

**Returns:**
- `str` or `None`: LaTeX code if latex=True, otherwise None

**Note:** `print_qtz` is maintained as an alias for backward compatibility.

### Supported Features

#### Gates
- **Single-qubit gates**: `h`, `x`, `y`, `z`, `s`, `sdg`, `t`, `tdg`, `sx`, `sxdg`
- **Rotation gates**: `rx(θ)`, `ry(θ)`, `rz(θ)`
- **Universal gate**: `u(θ, φ, λ)`
- **Two-qubit gates**: `cx`/`cnot`, `cy`, `cz`, `swap`
- **Three-qubit gates**: `ccx`/`toffoli`
- **Custom gates**: Displayed as labeled boxes

#### Circuit Elements
- Qubit declarations: `qubit[n] name;`
- Classical bit declarations: `bit[n] name;`
- Measurements: `c = measure q;`
- Reset: `reset q;` (wire terminates and restarts with |0⟩)
- Barriers: `barrier q;`

#### Expressions
- Numeric literals: `0.5`, `1.2`
- Pi constant: `pi` → `\pi`
- Greek letters: `theta` → `\theta`, `phi` → `\phi`
- Fractions: `pi/2` → `\frac{\pi}{2}`

### Example Circuits

#### Bell State
```python
bell = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
h q[0];
cx q[0], q[1];
"""
print_tex(bell, latex=True)
```

Output:
```latex
\begin{quantikz}
    \lstick{$|q[0]\rangle$} & \gate{H} & \ctrl{1} & \qw \\
    \lstick{$|q[1]\rangle$} & \qw & \targ{} & \qw
\end{quantikz}
```

#### GHZ State with Custom Spacing
```python
ghz = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
h q[0];
cx q[0], q[1];
cx q[1], q[2];
"""
# Add more space between elements
print_tex(ghz, latex=True, options={"width": "4mm"})
```

#### Quantum Teleportation with Classical Control
```python
teleport = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[2] c;

// Create entangled pair
h q[1];
cx q[1], q[2];

// Bell measurement
cx q[0], q[1];
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];

// Classical corrections
if (c[1]) x q[2];
if (c[0]) z q[2];
"""
print_tex(teleport, save_fig=True)  # Auto-saves as 'teleport.pdf'
```

#### Circuit with Reset
```python
reset_circuit = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit c;

// Use first qubit
h q[0];
cx q[0], q[1];
c = measure q[0];

// Reset and reuse
reset q[0];
h q[0];
cx q[0], q[1];
"""
print_tex(reset_circuit, latex=True)
```

The reset operation is visualized with a measurement (showing the current state is discarded), followed by wire termination with `\setwiretype{n}`, then restarting with `\lstick{|0⟩}`, and finally `\setwiretype{q}` to continue as a quantum wire. This clearly shows the qubit being measured and reset to the ground state.

### LaTeX Requirements

To render circuits (when `latex=False`), you need:
- A LaTeX distribution (TeX Live, MiKTeX, etc.)
- TikZ package
- quantikz package (the translator uses quantikz2 library)

For Jupyter notebook display:
- IPython
- ImageMagick (`convert` command)

### Classical Control Support

The translator now supports immediate classical control, where gates controlled by measurement outcomes appear in the same time slice as the measurements:

```python
teleport = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[2] c;

// Bell pair
h q[1];
cx q[1], q[2];

// Bell measurement
cx q[0], q[1];
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];

// Corrections based on measurements
if (c[1]) x q[2];  // Applied immediately
if (c[0]) z q[2];  // Applied immediately
"""

print_tex(teleport, latex=True)
```

### Advanced Features

#### Automatic Filename Generation

When saving figures, the filename can be automatically derived from the variable name:

```python
bell_circuit = """OPENQASM 3.0; ..."""
print_tex(bell_circuit, save_fig=True)  # Saves as 'bell_circuit.pdf'
```

#### Custom Spacing

Control the spacing between circuit elements:

```python
# Increase spacing for clarity
print_tex(circuit, options={"height": "4mm", "width": "6mm"})

# Compact spacing
print_tex(circuit, options={"height": "1mm", "width": "2mm"})
```

### Limitations

1. **Complex classical control** (`while` loops, nested conditions) is not fully supported
2. **Gate definitions** are not expanded
3. **Complex expressions** may not be fully supported
4. **Classical operations** other than measurements are not shown

### Error Handling

The translator provides clear error messages:

```python
try:
    print_qtz(invalid_qasm, latex=True)
except ValueError as e:
    print(f"Error: {e}")
```

### Tips

1. Use `latex=True` to get raw LaTeX code for inclusion in papers
2. Check warnings for partially supported features
3. Custom gates are shown as boxes with the gate name
4. Install openqasm3 separately if you don't need other translator features
5. Use the `options` parameter to adjust spacing for complex circuits
6. Variable names are automatically used as filenames when `save_fig=True`
7. Classical control shows gates in the same time slice as their controlling measurements