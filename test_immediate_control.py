#!/usr/bin/env python3
"""Test immediate classical control after measurements."""

from qsip import print_tex

# Test teleportation
teleport = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[2] c;

// Create entangled pair between Alice and Bob
h q[1];
cx q[1], q[2];

// Alice performs Bell measurement
cx q[0], q[1];
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];

// Bob's corrections based on measurement outcomes
if (c[1]) x q[2];
if (c[0]) z q[2];
"""

print("Quantum Teleportation (default spacing):")
print(print_tex(teleport, latex=True))

print("\n\nQuantum Teleportation (with custom spacing):")
print(print_tex(teleport, latex=True, options={"height": "3mm", "width": "5mm"}))

# Test filename extraction
print("\n\nTesting auto filename extraction:")
print_tex(teleport, save_fig=True)
print("Should have saved as 'teleport.pdf'")

# Let's also test with a simpler circuit
simple_test = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit c;

h q[0];
c = measure q[0];
if (c) x q[1];
"""

print("\n\nSimple Test (H, measure, controlled X):")
print(print_tex(simple_test, latex=True))

# Test with explicit filename
print_tex(simple_test, save_fig=True, filename="my_simple_circuit.pdf")
print("Should have saved as 'my_simple_circuit.pdf'")