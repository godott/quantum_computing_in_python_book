#!/usr/bin/env python3
"""Comprehensive test cases for print_tex function."""

import os
import tempfile
from qsip import print_tex

def test_basic_functionality():
    """Test basic circuit translation."""
    print("Test 1: Basic Bell State")
    bell = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
h q[0];
cx q[0], q[1];
"""
    latex = print_tex(bell, latex=True)
    print(latex)
    assert "\\gate{H}" in latex
    assert "\\ctrl{1}" in latex
    assert "\\targ{}" in latex
    print("✓ Basic translation works\n")


def test_spacing_options():
    """Test custom spacing options."""
    print("Test 2: Custom Spacing")
    circuit = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
cx q[0], q[1];
"""
    
    # Default spacing
    default = print_tex(circuit, latex=True)
    print("Default spacing:", default.split('\n')[0])
    
    # Custom spacing
    custom = print_tex(circuit, latex=True, options={"height": "3mm", "width": "5mm"})
    print("Custom spacing:", custom.split('\n')[0])
    
    assert "row sep={3mm}" in custom
    assert "column sep={5mm}" in custom
    assert "row sep" not in default
    print("✓ Spacing options work correctly\n")


def test_auto_filename():
    """Test automatic filename extraction."""
    print("Test 3: Auto Filename Extraction")
    
    test_circuit = """
OPENQASM 3.0;
include "stdgates.inc";
qubit q;
h q;
"""
    
    # Test with temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # This should save as test_circuit.pdf
            print_tex(test_circuit, save_fig=True, show=False)
            
            # Check if file exists
            expected_file = "test_circuit.pdf"
            if os.path.exists(expected_file):
                print(f"✓ Auto-generated filename: {expected_file}")
                os.remove(expected_file)
            else:
                print("✗ Auto filename generation failed")
        finally:
            os.chdir(old_cwd)
    
    print()


def test_classical_control():
    """Test classical control visualization."""
    print("Test 4: Classical Control")
    
    controlled = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit c;

h q[0];
c = measure q[0];
if (c) x q[1];
"""
    
    latex = print_tex(controlled, latex=True)
    print(latex)
    
    # Check that measurement and controlled gate are in same column
    lines = latex.split('\n')
    
    # Find the lines with meter and gate
    meter_line = None
    gate_line = None
    for i, line in enumerate(lines):
        if "\\meter{}" in line:
            meter_line = i
        if "\\gate{X}" in line and meter_line is not None:
            gate_line = i
            
    if meter_line is not None and gate_line is not None:
        # Count the number of & before meter and gate
        meter_pos = lines[meter_line].count('&', 0, lines[meter_line].find('\\meter{}'))
        gate_pos = lines[gate_line].count('&', 0, lines[gate_line].find('\\gate{X}'))
        
        if meter_pos == gate_pos:
            print("✓ Classical control gates appear at same time as measurement")
        else:
            print("✗ Classical control timing incorrect")
    
    # Check for classical wire
    assert "\\wire[d][1]{c}" in latex
    print("✓ Classical wire connection present\n")


def test_rotation_gates():
    """Test rotation gates with parameters."""
    print("Test 5: Rotation Gates")
    
    rotations = """
OPENQASM 3.0;
include "stdgates.inc";

qubit q;
rx(pi/2) q;
ry(pi/4) q;
rz(pi) q;
"""
    
    latex = print_tex(rotations, latex=True)
    print(latex)
    
    assert "R_x(\\frac{\\pi}{2})" in latex
    assert "R_y(\\frac{\\pi}{4})" in latex
    assert "R_z(\\pi)" in latex
    print("✓ Rotation gates with angle parameters work correctly\n")


def test_multi_qubit_registers():
    """Test multi-qubit registers."""
    print("Test 6: Multi-qubit Registers")
    
    multi_reg = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] alice;
qubit[2] bob;
bit[3] c;

h alice[0];
cx alice[0], bob[1];
c[0] = measure alice[0];
"""
    
    latex = print_tex(multi_reg, latex=True)
    print(latex)
    
    assert "alice[0]" in latex
    assert "bob[1]" in latex
    print("✓ Multi-qubit registers handled correctly\n")


def test_barriers():
    """Test barrier operations."""
    print("Test 7: Barriers")
    
    barrier_circuit = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
h q[0];
barrier q;
cx q[0], q[1];
"""
    
    latex = print_tex(barrier_circuit, latex=True)
    print(latex)
    
    assert "\\barrier" in latex
    print("✓ Barriers rendered correctly\n")


def test_reset():
    """Test reset operations."""
    print("Test 8: Reset Operations")
    
    # Test simple reset
    simple_reset = """
OPENQASM 3.0;
include "stdgates.inc";

qubit q;
h q;
reset q;
x q;
"""
    
    latex = print_tex(simple_reset, latex=True)
    print("Simple reset:", latex.split('\n')[1])
    
    assert "\\meter{}" in latex  # Reset includes measurement
    assert "\\setwiretype{n}" in latex
    assert "\\lstick{$|0\\rangle$}" in latex
    assert "\\setwiretype{q}" in latex
    print("✓ Simple reset works")
    
    # Test reset after measurement
    reset_after_measure = """
OPENQASM 3.0;
include "stdgates.inc";

qubit q;
bit c;
h q;
c = measure q;
reset q;
h q;
"""
    
    latex2 = print_tex(reset_after_measure, latex=True)
    assert "\\meter{}" in latex2
    assert "\\setwiretype{n}" in latex2
    assert "\\lstick{$|0\\rangle$}" in latex2
    assert "\\setwiretype{c}" in latex2  # Check classical wire after measurement
    print("✓ Reset after measurement works correctly\n")


def test_complex_teleportation():
    """Test complex teleportation circuit."""
    print("Test 9: Quantum Teleportation")
    
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
    
    latex = print_tex(teleport, latex=True)
    print(latex)
    
    # Check structure
    assert latex.count("\\meter{}") == 2
    assert latex.count("\\gate{X}") == 1
    assert latex.count("\\gate{Z}") == 1
    assert latex.count("\\wire") >= 2  # Classical wires
    print("✓ Complex teleportation circuit rendered correctly\n")


def test_error_handling():
    """Test error handling."""
    print("Test 10: Error Handling")
    
    # Invalid QASM
    invalid = """
OPENQASM 3.0;
this is not valid qasm
"""
    
    try:
        print_tex(invalid, latex=True)
        print("✗ Should have raised an error")
    except ValueError as e:
        print(f"✓ Correctly raised error: {str(e)[:50]}...")
    
    print()


def test_backward_compatibility():
    """Test backward compatibility with print_qtz."""
    print("Test 11: Backward Compatibility")
    
    from qsip import print_qtz
    
    simple = """
OPENQASM 3.0;
include "stdgates.inc";
qubit q;
h q;
"""
    
    # Both should produce same output
    tex_output = print_tex(simple, latex=True)
    qtz_output = print_qtz(simple, latex=True)
    
    if tex_output == qtz_output:
        print("✓ print_qtz alias works correctly")
    else:
        print("✗ print_qtz alias produces different output")
    
    print()


def test_all_gates():
    """Test all supported gate types."""
    print("Test 12: All Gate Types")
    
    all_gates = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;

// Single-qubit gates
h q[0];
x q[0];
y q[0];
z q[0];
s q[0];
sdg q[0];
t q[0];
tdg q[0];
sx q[0];
sxdg q[0];

// Two-qubit gates
cx q[0], q[1];
cy q[0], q[1];
cz q[0], q[1];
swap q[0], q[1];

// Three-qubit gate
ccx q[0], q[1], q[2];
"""
    
    latex = print_tex(all_gates, latex=True)
    
    expected_gates = ["H", "X", "Y", "Z", "S", "S^\\dagger", "T", "T^\\dagger", 
                      "\\sqrt{X}", "\\sqrt{X}^\\dagger", "\\ctrl", "\\swap", "\\ctrl"]
    
    missing = []
    for gate in expected_gates:
        if gate not in latex:
            missing.append(gate)
    
    if not missing:
        print("✓ All standard gates supported")
    else:
        print(f"✗ Missing gates: {missing}")
    
    print(latex[:200] + "...")
    print()


if __name__ == "__main__":
    print("Running comprehensive tests for print_tex function\n")
    print("=" * 60)
    
    test_basic_functionality()
    test_spacing_options()
    test_auto_filename()
    test_classical_control()
    test_rotation_gates()
    test_multi_qubit_registers()
    test_barriers()
    test_reset()
    test_complex_teleportation()
    test_error_handling()
    test_backward_compatibility()
    test_all_gates()
    
    print("=" * 60)
    print("All tests completed!")