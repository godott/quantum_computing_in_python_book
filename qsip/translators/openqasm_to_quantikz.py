"""OpenQASM3 to quantikz translator.

This module provides functionality to translate OpenQASM3 quantum circuits
to quantikz LaTeX format for visualization.

Features:
- Converts OpenQASM3 circuits to quantikz LaTeX format
- Supports immediate classical control visualization
- Automatic filename generation from variable names
- Customizable spacing options
- Full support for standard quantum gates
- Handles measurements, barriers, and resets

Example:
    >>> from qsip.translators import print_tex
    >>> circuit = '''OPENQASM 3.0;
    ... include "stdgates.inc";
    ... qubit[2] q;
    ... h q[0];
    ... cx q[0], q[1];
    ... '''
    >>> print_tex(circuit, latex=True)
    >>> print_tex(circuit, save_fig=True, options={"width": "3mm"})
"""

import os
import tempfile
import subprocess
import sys
import platform
from typing import List, Dict, Optional, Union, Tuple, Any
from dataclasses import dataclass, field

# Setup PATH for LaTeX on macOS
if platform.system() == 'Darwin':  # macOS
    # Common LaTeX installation paths on macOS
    latex_paths = [
        '/Library/TeX/texbin',
        '/usr/local/texlive/2025/bin/universal-darwin',
        '/usr/local/texlive/2024/bin/universal-darwin',
        '/usr/local/texlive/2023/bin/universal-darwin',
    ]
    
    # Add LaTeX paths to environment
    current_path = os.environ.get('PATH', '')
    for latex_path in latex_paths:
        if os.path.exists(latex_path) and latex_path not in current_path:
            os.environ['PATH'] = f"{latex_path}:{current_path}"
            current_path = os.environ['PATH']

# Try importing openqasm3 - provide clear error if not installed
try:
    import openqasm3
    from openqasm3 import ast
    OPENQASM_AVAILABLE = True
except ImportError:
    OPENQASM_AVAILABLE = False
    openqasm3 = None
    ast = None


@dataclass
class QubitMapping:
    """Maps qubit identifiers to wire indices."""
    name: str
    size: int
    start_index: int
    
    def get_index(self, offset: int = 0) -> int:
        """Get wire index for qubit at given offset."""
        if offset >= self.size:
            raise ValueError(f"Qubit index {offset} out of range for register {self.name}[{self.size}]")
        return self.start_index + offset


@dataclass 
class CircuitLayout:
    """Manages the layout of quantum and classical registers."""
    qubit_registers: Dict[str, QubitMapping] = field(default_factory=dict)
    classical_registers: Dict[str, Dict[str, int]] = field(default_factory=dict)
    total_qubits: int = 0
    total_cbits: int = 0
    
    def add_quantum_register(self, name: str, size: int):
        """Add a quantum register."""
        self.qubit_registers[name] = QubitMapping(name, size, self.total_qubits)
        self.total_qubits += size
    
    def add_classical_register(self, name: str, size: int):
        """Add a classical register."""
        self.classical_registers[name] = {"size": size, "start": self.total_cbits}
        self.total_cbits += size
    
    def get_qubit_index(self, qubit: Any) -> int:
        """Get the wire index for a qubit."""
        # Handle IndexedIdentifier (e.g., q[0])
        if hasattr(qubit, '__class__') and qubit.__class__.__name__ == 'IndexedIdentifier':
            # Get register name from qubit.name.name
            reg_name = qubit.name.name
                
            if reg_name in self.qubit_registers:
                # Extract index value from indices
                # indices is a list of lists (for multi-dimensional arrays)
                if hasattr(qubit, 'indices') and qubit.indices:
                    idx_expr = qubit.indices[0][0]  # First dimension, first index
                    
                    # Get numeric value
                    if hasattr(idx_expr, 'value'):
                        idx = idx_expr.value
                    elif isinstance(idx_expr, int):
                        idx = idx_expr
                    else:
                        raise ValueError(f"Cannot extract index from {idx_expr}")
                else:
                    idx = 0
                    
                return self.qubit_registers[reg_name].get_index(idx)
                
        # Handle simple Identifier (e.g., q for single qubit register)
        elif hasattr(qubit, 'name') and hasattr(qubit.name, 'name'):
            reg_name = qubit.name.name
            if reg_name in self.qubit_registers:
                return self.qubit_registers[reg_name].get_index(0)
        elif hasattr(qubit, 'name') and isinstance(qubit.name, str):
            reg_name = qubit.name
            if reg_name in self.qubit_registers:
                return self.qubit_registers[reg_name].get_index(0)
        
        raise ValueError(f"Unknown qubit: {qubit} (type: {type(qubit).__name__})")


class QuantikzTranslator:
    """Translates OpenQASM3 AST to quantikz LaTeX.
    
    This class handles the conversion of OpenQASM3 abstract syntax trees
    into quantikz LaTeX format. It supports:
    - Standard quantum gates (H, X, Y, Z, CNOT, etc.)
    - Rotation gates with angle parameters
    - Measurements and classical bit storage
    - Immediate classical control (if statements)
    - Barriers and reset operations
    - Multi-qubit registers
    
    Attributes:
        layout (CircuitLayout): Manages qubit and classical bit registers
        circuit_rows (List[List[str]]): LaTeX commands for each qubit wire
        errors (List[str]): Collection of error messages
        warnings (List[str]): Collection of warning messages
        measurement_map (Dict[str, List[Tuple[int, int]]]): Maps classical bits to measurements
        pending_classical_ops (List[Tuple[str, Any]]): Stores classically controlled gates
    """
    
    def __init__(self):
        self.layout = CircuitLayout()
        self.circuit_rows: List[List[str]] = []
        self.classical_rows: List[List[str]] = []  # Track classical wire rows
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.has_classical_control = False  # Flag to track if we need classical wires
        self.measurement_map: Dict[str, List[Tuple[int, int]]] = {}  # Maps cbit name to (qubit_idx, column) where measured
        self.current_column = 0  # Track current column position
        self.pending_classical_ops: List[Tuple[str, Any]] = []  # Store (cbit_key, gate) pairs
        
        # Standard gate mappings
        self.standard_gates = {
            'h': 'H', 'x': 'X', 'y': 'Y', 'z': 'Z',
            'cx': 'CNOT', 'cnot': 'CNOT', 'cy': 'CY', 'cz': 'CZ',
            's': 'S', 'sdg': 'S^\\dagger', 't': 'T', 'tdg': 'T^\\dagger',
            'sx': '\\sqrt{X}', 'sxdg': '\\sqrt{X}^\\dagger',
            'swap': 'SWAP', 'ccx': 'Toffoli', 'toffoli': 'Toffoli'
        }
    
    def translate(self, qasm_ast: Any) -> str:
        """Translate OpenQASM3 AST to quantikz LaTeX."""
        # Process declarations first
        for statement in qasm_ast.statements:
            if hasattr(statement, '__class__'):
                stmt_type = statement.__class__.__name__
                if stmt_type == 'QubitDeclaration':
                    self._process_qubit_declaration(statement)
                elif stmt_type == 'ClassicalDeclaration':
                    self._process_classical_declaration(statement)
        
        # Initialize circuit rows
        self.circuit_rows = [[] for _ in range(self.layout.total_qubits)]
        # Initialize classical rows if needed
        if self.layout.total_cbits > 0:
            self.classical_rows = [[] for _ in range(self.layout.total_cbits)]
        
        # First pass: collect all if statements
        for statement in qasm_ast.statements:
            if hasattr(statement, '__class__'):
                stmt_type = statement.__class__.__name__
                if stmt_type == 'BranchingStatement':
                    self._process_branching(statement)
        
        # Second pass: process gates and operations
        for i, statement in enumerate(qasm_ast.statements):
            if hasattr(statement, '__class__'):
                stmt_type = statement.__class__.__name__
                if stmt_type == 'QuantumGate':
                    self._process_gate(statement)
                elif stmt_type == 'QuantumMeasurement':
                    self._process_measurement(statement)
                elif stmt_type == 'QuantumMeasurementStatement':
                    # Unwrap the measurement
                    self._process_measurement(statement.measure, statement.target)
                elif stmt_type == 'QuantumBarrier':
                    self._process_barrier(statement)
                elif stmt_type == 'QuantumReset':
                    self._process_reset(statement)
                # BranchingStatement already processed in first pass
        
        # Process any remaining classical operations
        self._flush_pending_classical_ops()
        
        return self._generate_latex()
    
    def _process_qubit_declaration(self, decl: Any):
        """Process qubit declaration."""
        # Get qubit name
        if hasattr(decl.qubit, 'name'):
            name = decl.qubit.name
        elif hasattr(decl, 'identifier'):
            name = decl.identifier.name
        else:
            raise ValueError(f"Cannot extract name from qubit declaration: {decl}")
        
        # Get size
        if hasattr(decl, 'size') and decl.size is not None:
            if hasattr(decl.size, 'value'):
                size = decl.size.value
            else:
                size = int(decl.size)
        else:
            size = 1
            
        self.layout.add_quantum_register(name, size)
    
    def _process_classical_declaration(self, decl: Any):
        """Process classical bit declaration."""
        # Check if this is a BitType declaration
        if hasattr(decl, 'type') and decl.type.__class__.__name__ == 'BitType':
            name = decl.identifier.name
            
            # Get size from type
            if hasattr(decl.type, 'size') and decl.type.size is not None:
                if hasattr(decl.type.size, 'value'):
                    size = decl.type.size.value
                else:
                    size = int(decl.type.size)
            else:
                size = 1
                
            self.layout.add_classical_register(name, size)
    
    def _advance_circuit(self):
        """Ensure all rows have the same number of elements."""
        if not self.circuit_rows:
            return
            
        max_len = max(len(row) for row in self.circuit_rows)
        for row in self.circuit_rows:
            while len(row) < max_len:
                row.append("\\qw")
        
        # Update current column position
        self.current_column = max_len
    
    def _process_gate(self, gate: Any):
        """Process a quantum gate."""
        gate_name = gate.name.name.lower()
        
        # Get qubit indices
        try:
            qubit_indices = [self.layout.get_qubit_index(q) for q in gate.qubits]
        except ValueError as e:
            self.errors.append(str(e))
            return
        
        # Advance circuit
        self._advance_circuit()
        
        # Apply gate based on type
        if gate_name in self.standard_gates:
            self._apply_standard_gate(gate_name, qubit_indices, gate)
        elif gate_name.startswith('r'):
            self._apply_rotation_gate(gate_name, qubit_indices, gate)
        elif gate_name == 'u':
            self._apply_u_gate(qubit_indices, gate)
        else:
            self._apply_custom_gate(gate_name, qubit_indices, gate)
    
    def _apply_standard_gate(self, gate_name: str, qubits: List[int], gate: Any):
        """Apply a standard gate."""
        if len(qubits) == 1:
            # Single-qubit gate
            self.circuit_rows[qubits[0]].append(f"\\gate{{{self.standard_gates[gate_name]}}}")
            
        elif len(qubits) == 2:
            if gate_name in ['cx', 'cnot']:
                # CNOT gate
                ctrl, targ = qubits
                self.circuit_rows[ctrl].append(f"\\ctrl{{{targ - ctrl}}}")
                self.circuit_rows[targ].append("\\targ{}")
            elif gate_name in ['cy', 'cz']:
                # Controlled Y/Z
                ctrl, targ = qubits
                self.circuit_rows[ctrl].append(f"\\ctrl{{{targ - ctrl}}}")
                self.circuit_rows[targ].append(f"\\gate{{{gate_name[1].upper()}}}")
            elif gate_name == 'swap':
                # SWAP gate
                q0, q1 = qubits
                self.circuit_rows[q0].append(f"\\swap{{{q1 - q0}}}")
                self.circuit_rows[q1].append("\\targX{}")
                
        elif len(qubits) == 3 and gate_name in ['ccx', 'toffoli']:
            # Toffoli gate
            ctrl1, ctrl2, targ = qubits
            self.circuit_rows[ctrl1].append(f"\\ctrl{{{ctrl2 - ctrl1}}}")
            self.circuit_rows[ctrl2].append(f"\\ctrl{{{targ - ctrl2}}}")
            self.circuit_rows[targ].append("\\targ{}")
    
    def _apply_rotation_gate(self, gate_name: str, qubits: List[int], gate: Any):
        """Apply a rotation gate."""
        if len(qubits) != 1:
            self.errors.append(f"Rotation gate {gate_name} requires exactly 1 qubit")
            return
        
        # Get angle parameter
        angle_str = self._format_angle(gate.arguments[0] if gate.arguments else None)
        
        # Format gate string
        if gate_name == 'rx':
            gate_str = f"R_x({angle_str})"
        elif gate_name == 'ry':
            gate_str = f"R_y({angle_str})"
        elif gate_name == 'rz':
            gate_str = f"R_z({angle_str})"
        else:
            gate_str = f"{gate_name.upper()}({angle_str})"
        
        self.circuit_rows[qubits[0]].append(f"\\gate{{{gate_str}}}")
    
    def _apply_u_gate(self, qubits: List[int], gate: Any):
        """Apply a U gate."""
        if len(qubits) != 1:
            self.errors.append("U gate requires exactly 1 qubit")
            return
        
        # Format angles
        angles = []
        for arg in gate.arguments[:3]:  # U gate has 3 parameters
            angles.append(self._format_angle(arg))
        
        gate_str = f"U({','.join(angles)})"
        self.circuit_rows[qubits[0]].append(f"\\gate{{{gate_str}}}")
    
    def _apply_custom_gate(self, gate_name: str, qubits: List[int], gate: Any):
        """Apply a custom gate."""
        gate_str = gate_name.upper()
        
        # Add parameters if any
        if hasattr(gate, 'arguments') and gate.arguments:
            params = [self._format_angle(arg) for arg in gate.arguments]
            gate_str += f"({','.join(params)})"
        
        if len(qubits) == 1:
            self.circuit_rows[qubits[0]].append(f"\\gate{{{gate_str}}}")
        else:
            # Multi-qubit custom gate
            min_q = min(qubits)
            max_q = max(qubits)
            span = max_q - min_q + 1
            self.circuit_rows[min_q].append(f"\\gate[{span}]{{{gate_str}}}")
            # Other qubits just continue
            for q in qubits[1:]:
                self.circuit_rows[q].append("\\qw")
    
    def _format_angle(self, expr: Any) -> str:
        """Format an angle expression."""
        if expr is None:
            return "?"
        
        # Handle different expression types
        if hasattr(expr, 'value'):
            return str(expr.value)
        elif hasattr(expr, 'name'):
            # Variable reference - convert common names
            name = expr.name
            if name == 'pi':
                return '\\pi'
            elif name in ['theta', 'phi', 'lambda', 'alpha', 'beta', 'gamma']:
                return f'\\{name}'
            return name
        elif hasattr(expr, '__class__') and expr.__class__.__name__ == 'BinaryExpression':
            # Binary expression - handle properly
            if hasattr(expr, 'lhs') and hasattr(expr, 'rhs') and hasattr(expr, 'op'):
                left = self._format_angle(expr.lhs)
                right = self._format_angle(expr.rhs)
                
                # Check operation type
                if hasattr(expr.op, 'name'):
                    if expr.op.name == 'SLASH' or expr.op.name == '/':
                        return f"\\frac{{{left}}}{{{right}}}"
                    elif expr.op.name == 'STAR' or expr.op.name == '*':
                        return f"{left} \\cdot {right}"
                    elif expr.op.name == 'PLUS' or expr.op.name == '+':
                        return f"{left} + {right}"
                    elif expr.op.name == 'MINUS' or expr.op.name == '-':
                        return f"{left} - {right}"
                elif hasattr(expr.op, 'value'):
                    if expr.op.value == '/':
                        return f"\\frac{{{left}}}{{{right}}}"
                    else:
                        return f"{left}{expr.op.value}{right}"
                
            # Fallback
            return str(expr)
        else:
            # Try to extract numeric value
            if hasattr(expr, '__str__'):
                s = str(expr)
                # Simple pattern matching for common cases
                if 'pi/2' in s:
                    return '\\frac{\\pi}{2}'
                elif 'pi/4' in s:
                    return '\\frac{\\pi}{4}'
            return str(expr)
    
    def _process_measurement(self, meas: Any, target: Any = None):
        """Process measurement operation.
        
        Handles measurement operations and places any classically controlled gates
        that depend on this measurement in the same time slice, creating immediate
        classical control visualization.
        
        Args:
            meas: The measurement AST node
            target: Optional target classical bit for the measurement result
        """
        try:
            qubit_idx = self.layout.get_qubit_index(meas.qubit)
        except ValueError as e:
            self.errors.append(str(e))
            return
        
        self._advance_circuit()
        
        # Track measurement location BEFORE adding it
        actual_target = target if target is not None else (meas.target if hasattr(meas, 'target') else None)
        cbit_key = None
        if actual_target is not None:
            # Extract classical bit name and index
            if hasattr(actual_target, '__class__') and actual_target.__class__.__name__ == 'IndexedIdentifier':
                cbit_name = actual_target.name.name
                if hasattr(actual_target, 'indices') and actual_target.indices:
                    idx_expr = actual_target.indices[0][0]
                    if hasattr(idx_expr, 'value'):
                        cbit_idx = idx_expr.value
                        cbit_key = f"{cbit_name}[{cbit_idx}]"
                    else:
                        cbit_key = cbit_name
                else:
                    cbit_key = cbit_name
            elif hasattr(actual_target, 'name'):
                cbit_key = actual_target.name if isinstance(actual_target.name, str) else actual_target.name.name
            else:
                cbit_key = str(actual_target)
            
            # Store measurement location
            if cbit_key not in self.measurement_map:
                self.measurement_map[cbit_key] = []
            self.measurement_map[cbit_key].append((qubit_idx, self.current_column))
        
        # Now place measurement and any gates controlled by this bit in the SAME column
        # First, find gates controlled by this measurement
        gates_to_place = []
        if cbit_key and self.pending_classical_ops:
            remaining_ops = []
            for key, gate in self.pending_classical_ops:
                if key == cbit_key:
                    gates_to_place.append(gate)
                else:
                    remaining_ops.append((key, gate))
            self.pending_classical_ops = remaining_ops
        
        # Track which qubits have operations in this column
        placed_on_qubits = {qubit_idx}  # Measurement qubit
        
        # Place controlled gates FIRST (so we can modify the measurement if needed)
        for gate in gates_to_place:
            try:
                gate_qubits = [self.layout.get_qubit_index(q) for q in gate.qubits]
            except ValueError:
                continue
                
            target_qubit = gate_qubits[0]
            gate_name = gate.name.name.lower()
            
            # Place the gate
            if len(gate_qubits) == 1:
                if gate_name in self.standard_gates:
                    gate_str = self.standard_gates[gate_name]
                else:
                    gate_str = gate_name.upper()
                self.circuit_rows[target_qubit].append(f"\\gate{{{gate_str}}}")
                placed_on_qubits.add(target_qubit)
            elif len(gate_qubits) == 2 and gate_name in ['cx', 'cnot']:
                ctrl_idx, targ_idx = gate_qubits
                self.circuit_rows[ctrl_idx].append(f"\\ctrl{{{targ_idx - ctrl_idx}}}")
                self.circuit_rows[targ_idx].append("\\targ{}")
                placed_on_qubits.add(ctrl_idx)
                placed_on_qubits.add(targ_idx)
        
        # Now place measurement with wire if needed
        if gates_to_place:
            # Check if we need a wire from measurement to controlled gates
            wire_needed = False
            wire_targets = []
            for gate in gates_to_place:
                try:
                    gate_qubits = [self.layout.get_qubit_index(q) for q in gate.qubits]
                    if gate_qubits[0] != qubit_idx:
                        wire_needed = True
                        wire_targets.append(gate_qubits[0])
                except ValueError:
                    continue
            
            if wire_needed and wire_targets:
                # Find the furthest target for the wire
                distances = [abs(t - qubit_idx) for t in wire_targets]
                max_dist_idx = distances.index(max(distances))
                target = wire_targets[max_dist_idx]
                distance = abs(target - qubit_idx)
                direction = 'd' if target > qubit_idx else 'u'
                self.circuit_rows[qubit_idx].append(f"\\meter{{}}\\wire[{direction}][{distance}]{{c}}")
            else:
                self.circuit_rows[qubit_idx].append("\\meter{}")
        else:
            # No controlled gates, just place measurement
            self.circuit_rows[qubit_idx].append("\\meter{}")
        
        # Fill \qw for qubits that don't have operations in this column
        for i in range(self.layout.total_qubits):
            if i not in placed_on_qubits:
                self.circuit_rows[i].append("\\qw")
        
        # Add classical wire type after the measurement column
        # But check if a reset is coming next - if so, skip the wire type change
        if cbit_key:
            # Look ahead to see if reset is next for this qubit
            # For now, always add the classical wire type - we'll handle it in reset
            self._advance_circuit()
            self.circuit_rows[qubit_idx].append("\\setwiretype{c}")
            # Fill other qubits
            for i in range(self.layout.total_qubits):
                if i != qubit_idx:
                    self.circuit_rows[i].append("\\qw")
    
    def _process_barrier(self, barrier: Any):
        """Process barrier operation."""
        if hasattr(barrier, 'qubits') and barrier.qubits:
            try:
                qubit_indices = [self.layout.get_qubit_index(q) for q in barrier.qubits]
            except ValueError as e:
                self.errors.append(str(e))
                return
        else:
            # Barrier on all qubits
            qubit_indices = list(range(self.layout.total_qubits))
        
        self._advance_circuit()
        
        # Add barrier
        for i, row in enumerate(self.circuit_rows):
            if i in qubit_indices:
                if i == min(qubit_indices):
                    row.append(f"\\barrier{{{len(qubit_indices)}}}")
                else:
                    row.append("\\qw")
            else:
                row.append("\\qw")
    
    def _process_reset(self, reset: Any):
        """Process reset operation.
        
        Reset is visualized as a measurement followed by wire termination and restart with |0⟩.
        This properly shows the re-initialization of the qubit.
        """
        try:
            qubit_idx = self.layout.get_qubit_index(reset.qubits)
        except ValueError as e:
            self.errors.append(str(e))
            return
        
        # Move to next column for reset
        self._advance_circuit()
        
        # First, add a measurement (to show we're discarding the current state)
        self.circuit_rows[qubit_idx].append("\\meter{}")
        
        # Advance to next column
        self._advance_circuit()
        
        # Cut the wire with setwiretype{n}
        self.circuit_rows[qubit_idx].append("\\setwiretype{n}")
        
        # Advance to next column
        self._advance_circuit()
        
        # Restart the wire with |0⟩
        self.circuit_rows[qubit_idx].append("\\lstick{$|0\\rangle$}")
        
        # Advance to next column
        self._advance_circuit()
        
        # Set back to quantum wire
        self.circuit_rows[qubit_idx].append("\\setwiretype{q}\\qw")
        
        # Continue with quantum wire after reset
        # No need to fill other qubits as _advance_circuit handles that
    
    def _process_branching(self, branch: Any):
        """Process if statement with classical control."""
        # Only handle simple if statements with single classical bit conditions
        if not hasattr(branch, 'condition') or not hasattr(branch, 'if_block'):
            self.warnings.append("Complex branching statements not fully supported")
            return
        
        # Get the classical bit condition
        condition = branch.condition
        cbit_key = None
        
        if hasattr(condition, 'name'):
            # Simple identifier (e.g., if (c))
            cbit_name = condition.name
            cbit_indices = self._get_classical_bit_indices(cbit_name)
            if len(cbit_indices) == 0:
                self.errors.append(f"Classical bit {cbit_name} not found")
                return
            elif len(cbit_indices) > 1:
                self.warnings.append(f"Classical control on register {cbit_name} with {len(cbit_indices)} bits - using first bit")
                cbit_key = f"{cbit_name}[0]"
            else:
                cbit_key = cbit_name
                
        elif hasattr(condition, '__class__') and condition.__class__.__name__ == 'IndexExpression':
            # Index expression (e.g., if (c[1]))
            if hasattr(condition, 'collection') and hasattr(condition.collection, 'name'):
                cbit_name = condition.collection.name
            elif hasattr(condition, 'name') and hasattr(condition.name, 'name'):
                cbit_name = condition.name.name
            else:
                self.errors.append(f"Cannot extract collection name from IndexExpression")
                return
                
            if hasattr(condition, 'index') and condition.index:
                idx_expr = condition.index[0]  # First index
                if hasattr(idx_expr, 'value'):
                    bit_offset = idx_expr.value
                    cbit_key = f"{cbit_name}[{bit_offset}]"
                else:
                    self.errors.append("Non-literal classical bit indices not supported")
                    return
            else:
                self.warnings.append("Cannot extract classical bit index")
                return
        else:
            self.warnings.append(f"Classical control condition type {type(condition).__name__} not supported")
            return
        
        # Collect the gates in the if block for later processing
        for stmt in branch.if_block:
            if hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'QuantumGate':
                # Store this classically controlled gate for later processing
                self.pending_classical_ops.append((cbit_key, stmt))
            else:
                self.warnings.append(f"Classical control of {type(stmt).__name__} not supported")
    
    def _flush_pending_classical_ops(self, up_to_column=None):
        """Process pending classical operations that should be placed now."""
        # Since we now handle classically controlled gates directly in _process_measurement,
        # this method should only handle any remaining operations that weren't matched
        # to measurements (which would be an error case)
        if self.pending_classical_ops:
            for cbit_key, gate in self.pending_classical_ops:
                self.warnings.append(f"Classical control on {cbit_key} has no corresponding measurement")
    
    def _is_next_statement_measurement(self, statements: List[Any], current_index: int) -> bool:
        """Check if the next statement is a measurement."""
        if current_index + 1 >= len(statements):
            return False
        
        next_stmt = statements[current_index + 1]
        if hasattr(next_stmt, '__class__'):
            stmt_type = next_stmt.__class__.__name__
            return stmt_type in ['QuantumMeasurement', 'QuantumMeasurementStatement']
        return False
    
    def _get_classical_bit_indices(self, name: str) -> List[int]:
        """Get indices for classical bits."""
        if name in self.layout.classical_registers:
            reg = self.layout.classical_registers[name]
            return list(range(reg["start"], reg["start"] + reg["size"]))
        return []
    
    def _process_classical_controlled_gate(self, gate: Any, cbit_key: str):
        """Process a classically controlled gate with explicit wire routing."""
        gate_name = gate.name.name.lower()
        
        # Get qubit indices
        try:
            qubit_indices = [self.layout.get_qubit_index(q) for q in gate.qubits]
        except ValueError as e:
            self.errors.append(str(e))
            return
        
        # Find the measurement source for this classical bit
        measure_info = None
        if cbit_key in self.measurement_map:
            # Get the most recent measurement for this bit
            measure_qubit, measure_col = self.measurement_map[cbit_key][-1]
            measure_info = (measure_qubit, measure_col)
            target_qubit = qubit_indices[0]  # Primary target for single-qubit gates
            
            # Track that we need classical control
            self.has_classical_control = True
        
        # Advance circuit
        self._advance_circuit()
        
        # Apply the gate first
        if len(qubit_indices) == 1:
            qubit_idx = qubit_indices[0]
            
            # Add the classically controlled gate
            if gate_name in self.standard_gates:
                gate_str = self.standard_gates[gate_name]
            else:
                gate_str = gate_name.upper()
            
            # Add gate with classical input
            self.circuit_rows[qubit_idx].append(f"\\gate{{{gate_str}}}")
            
        elif len(qubit_indices) == 2 and gate_name in ['cx', 'cnot']:
            # Classically controlled CNOT
            ctrl_idx, targ_idx = qubit_indices
            self.circuit_rows[ctrl_idx].append(f"\\ctrl{{{targ_idx - ctrl_idx}}}")
            self.circuit_rows[targ_idx].append("\\targ{}")
        else:
            # General multi-qubit gate with classical control
            min_q = min(qubit_indices)
            max_q = max(qubit_indices)
            span = max_q - min_q + 1
            self.circuit_rows[min_q].append(f"\\gate[{span}]{{{gate_name.upper()}}}")
            for q in qubit_indices[1:]:
                self.circuit_rows[q].append("\\qw")
        
        # Now handle classical wire routing after gate is placed
        if measure_info:
            measure_qubit, measure_col = measure_info
            target_qubit = qubit_indices[0]
            
            if measure_qubit != target_qubit:
                # We need to add a vertical wire connection
                distance = abs(target_qubit - measure_qubit)
                direction = 'd' if target_qubit > measure_qubit else 'u'
                
                # The gate is now placed on the target row
                # We need to place the wire one column before the gate
                target_length = len(self.circuit_rows[target_qubit])
                current_length = len(self.circuit_rows[measure_qubit])
                
                # Fill gaps to align with one column before the gate
                while current_length < target_length - 1:
                    self.circuit_rows[measure_qubit].append("\\qw")
                    current_length += 1
                
                # Now add the wire
                self.circuit_rows[measure_qubit].append(f"\\wire[{direction}][{distance}]{{c}}")
    
    def _generate_latex(self) -> str:
        """Generate the final quantikz LaTeX code."""
        if self.errors:
            raise ValueError(f"Translation errors:\\n" + "\\n".join(self.errors))
        
        # Ensure all rows are same length and add final wire
        self._advance_circuit()
        for row in self.circuit_rows:
            row.append("\\qw")
        
        # Build LaTeX
        lines = ["\\begin{quantikz}"]
        
        # Add rows with labels
        for i in range(self.layout.total_qubits):
            # Find register and index
            label = None
            for reg_name, reg_map in self.layout.qubit_registers.items():
                if reg_map.start_index <= i < reg_map.start_index + reg_map.size:
                    idx = i - reg_map.start_index
                    if reg_map.size > 1:
                        label = f"{reg_name}[{idx}]"
                    else:
                        label = reg_name
                    break
            
            # Build row
            if label:
                row_str = f"\\lstick{{$|{label}\\rangle$}} & " + " & ".join(self.circuit_rows[i])
            else:
                row_str = " & ".join(self.circuit_rows[i])
            
            # Add line terminator
            if i < self.layout.total_qubits - 1:
                row_str += " \\\\"
            
            lines.append("    " + row_str)
        
        lines.append("\\end{quantikz}")
        
        return "\n".join(lines)


def print_tex(openqasm_string: str, latex: bool = False, save_fig: bool = False,
              filename: Optional[str] = None, show: bool = True, 
              border: str = "2pt", options: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Convert OpenQASM3 string to quantikz visualization.
    
    Parameters:
    -----------
    openqasm_string : str
        OpenQASM3 circuit description
    latex : bool, default=False
        If True, return LaTeX code instead of rendering
    save_fig : bool, default=False
        If True, save the figure to a file
    filename : str, optional
        Filename for saving the figure. If None and save_fig=True, 
        attempts to extract variable name from calling frame
    show : bool, default=True
        If True, display the figure (when not in latex mode)
    border : str, default="2pt"
        Border size around the circuit (e.g., "0pt", "2pt", "1mm")
    options : dict, optional
        Dictionary of quantikz options. Supported keys:
        - "height": row separation (e.g., "2mm", "10pt")
        - "width": column separation (e.g., "2mm", "10pt")
    
    Returns:
    --------
    str or None
        LaTeX code if latex=True, otherwise None
    """
    if not OPENQASM_AVAILABLE:
        raise ImportError(
            "OpenQASM3 is not installed. Install it with:\\n"
            "pip install openqasm3"
        )
    
    # Parse OpenQASM
    try:
        qasm_ast = openqasm3.parse(openqasm_string)
    except Exception as e:
        raise ValueError(f"Failed to parse OpenQASM3: {e}")
    
    # Translate to quantikz
    translator = QuantikzTranslator()
    quantikz_code = translator.translate(qasm_ast)
    
    # Show warnings if any
    if translator.warnings:
        print("Warnings:")
        for warning in translator.warnings:
            print(f"  - {warning}")
    
    # Apply options if provided
    if options:
        # Extract options
        row_sep = options.get("height", "")
        col_sep = options.get("width", "")
        
        # Build options string
        option_parts = []
        if row_sep:
            option_parts.append(f"row sep={{{row_sep}}}")
        if col_sep:
            option_parts.append(f"column sep={{{col_sep}}}")
        
        if option_parts:
            # Modify quantikz code to include options
            quantikz_code = quantikz_code.replace(
                "\\begin{quantikz}",
                f"\\begin{{quantikz}}[{', '.join(option_parts)}]"
            )
    
    if latex:
        return quantikz_code
    
    # Handle filename for save_fig
    if save_fig and filename is None:
        # Try to extract variable name from calling frame
        import inspect
        frame = inspect.currentframe()
        try:
            # Get caller's frame
            caller_frame = frame.f_back
            # Get local variables
            caller_locals = caller_frame.f_locals
            
            # Find variable name that matches our openqasm_string
            var_name = None
            for name, value in caller_locals.items():
                if isinstance(value, str) and value == openqasm_string:
                    var_name = name
                    break
            
            if var_name:
                filename = f"{var_name}.pdf"
            else:
                filename = "quantum_circuit.pdf"
        finally:
            del frame
    
    # Create full LaTeX document
    latex_doc = f"""\\documentclass[tikz,border={border}]{{standalone}}
\\usepackage{{tikz}}
\\usetikzlibrary{{quantikz2}}

\\begin{{document}}
{quantikz_code}
\\end{{document}}"""
    
    # Compile and display/save
    if save_fig or show:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write LaTeX file
            tex_file = os.path.join(tmpdir, "circuit.tex")
            with open(tex_file, 'w') as f:
                f.write(latex_doc)
            
            # Compile to PDF
            try:
                # Try to find pdflatex
                pdflatex_cmd = 'pdflatex'
                
                # Check if pdflatex is available
                try:
                    subprocess.run(['which', pdflatex_cmd], capture_output=True, check=True)
                except:
                    # Try common paths
                    for path in ['/Library/TeX/texbin/pdflatex', '/usr/local/bin/pdflatex']:
                        if os.path.exists(path):
                            pdflatex_cmd = path
                            break
                
                result = subprocess.run(
                    [pdflatex_cmd, '-interaction=nonstopmode', tex_file],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print("LaTeX compilation failed:")
                    print(result.stdout[-1000:])  # Last 1000 chars
                    raise RuntimeError("Failed to compile LaTeX")
                
                pdf_file = os.path.join(tmpdir, "circuit.pdf")
                
                if save_fig:
                    import shutil
                    shutil.copy(pdf_file, filename)
                    print(f"Circuit saved to {filename}")
                
                if show:
                    # Try to display in Jupyter
                    try:
                        from IPython.display import Image, display
                        # Convert to PNG for display
                        png_file = os.path.join(tmpdir, "circuit.png")
                        
                        # Try magick first (ImageMagick 7+), then convert (ImageMagick 6)
                        convert_cmds = [
                            ['magick', 'convert', '-density', '150', pdf_file, png_file],
                            ['magick', '-density', '150', pdf_file, png_file],
                            ['convert', '-density', '150', pdf_file, png_file]
                        ]
                        
                        for cmd in convert_cmds:
                            try:
                                result = subprocess.run(cmd, capture_output=True)
                                if result.returncode == 0:
                                    break
                            except FileNotFoundError:
                                continue
                        else:
                            raise RuntimeError("ImageMagick not found")
                        
                        display(Image(png_file))
                    except Exception as e:
                        print(f"Could not display image: {e}")
                        print("Circuit PDF generated successfully.")
                        
            except FileNotFoundError as e:
                print(f"Required tool not found: {e}")
                print("\\nGenerated LaTeX code:")
                print(quantikz_code)