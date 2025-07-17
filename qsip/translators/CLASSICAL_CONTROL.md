# Classical Control in OpenQASM3 to Quantikz Translation

## Overview

The OpenQASM3 to Quantikz translator now supports immediate classical control using `if` statements. This allows for quantum circuits with classical feedback, where measurement outcomes control subsequent quantum operations in the same time slice, accurately representing real-time classical control in quantum circuits.

## Supported Features

### Basic Classical Control
```qasm
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit c;

h q[0];
c = measure q[0];
if (c) x q[1];  // Apply X gate to q[1] if c is 1
```

### Indexed Classical Bits
```qasm
qubit[3] q;
bit[2] c;

c[0] = measure q[0];
c[1] = measure q[1];

if (c[1]) x q[2];  // Control based on specific bit
```

### Multiple Controlled Gates
```qasm
bit c;
c = measure q[0];

if (c) x q[1];
if (c) z q[2];  // Multiple gates controlled by same bit
```

### Classically Controlled Multi-Qubit Gates
```qasm
bit c;
c = measure q[0];

if (c) cx q[1], q[2];  // Classically controlled CNOT
```

## Visual Representation

In the generated Quantikz circuits, classically controlled gates now appear in the SAME time slice as their controlling measurements:

1. **Measurements** are shown with the standard meter symbol: `\meter{}`
2. **Classical wires** connect measurements to controlled gates using `\wire[d][n]{c}` or `\wire[u][n]{c}` commands
3. **Classically controlled gates** appear in the same column as the measurement, showing immediate control
4. **Wire type** changes to classical after measurement using `\setwiretype{c}`

### Example Output

#### Simple Classical Control
```latex
\begin{quantikz}
    \lstick{$|q[0]\rangle$} & \gate{H} & \meter{}\wire[d][1]{c} & \setwiretype{c} & \qw \\
    \lstick{$|q[1]\rangle$} & \qw & \gate{X} & \qw & \qw
\end{quantikz}
```

In this example, the X gate on q[1] appears in the same column as the measurement on q[0], showing that it's immediately controlled by the measurement outcome.

#### Quantum Teleportation
```latex
\begin{quantikz}
    \lstick{$|q[0]\rangle$} & \qw & \qw & \ctrl{1} & \gate{H} & \meter{}\wire[d][2]{c} & \setwiretype{c} & \qw & \qw & \qw \\
    \lstick{$|q[1]\rangle$} & \gate{H} & \ctrl{1} & \targ{} & \qw & \qw & \qw & \meter{}\wire[d][1]{c} & \setwiretype{c} & \qw \\
    \lstick{$|q[2]\rangle$} & \qw & \targ{} & \qw & \qw & \gate{Z} & \qw & \gate{X} & \qw & \qw
\end{quantikz}
```

Here, the Z gate (controlled by c[0]) appears with the first measurement, and the X gate (controlled by c[1]) appears with the second measurement, accurately representing the immediate classical feedback in quantum teleportation.

## Limitations

1. **Complex conditions**: Only simple bit conditions are supported (e.g., `if (c)` or `if (c[1])`). Boolean expressions like `if (c[0] && c[1])` are not yet supported.

2. **Else blocks**: `if-else` statements are not yet supported.

3. **Multiple control targets**: When a single classical bit controls multiple gates on different qubits, the wire routing may become complex and could overlap with other circuit elements.

## Using the Translator

The translator is accessed through the `print_tex` function (formerly `print_qtz`):

```python
from qsip import print_tex

# Basic usage
circuit = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit c;
h q[0];
c = measure q[0];
if (c) x q[1];
"""

# Get LaTeX code
latex = print_tex(circuit, latex=True)

# Save to PDF (auto-names as 'circuit.pdf')
print_tex(circuit, save_fig=True)

# Customize spacing for clarity
print_tex(circuit, latex=True, options={"height": "3mm", "width": "5mm"})
```

## Implementation Notes

- Classical bit registers must be declared before use
- Single-bit declarations (`bit c;`) create a register of size 1
- Multi-bit declarations (`bit[n] c;`) create registers that can be indexed
- The translator pre-processes if statements to associate them with measurements
- Classical controlled gates are placed in the same time slice as their controlling measurements
- Warning messages are generated for unsupported features

## Future Enhancements

Potential improvements include:
- Explicit classical wire routing using `\wire` commands
- Support for complex boolean conditions
- If-else statement support
- Classical arithmetic operations
- Mid-circuit measurements with reset