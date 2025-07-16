"""Debug coordinate system to understand vector placement."""

import numpy as np
from bloch_refactored import Bloch, QuantumState

# Create Bloch sphere
b = Bloch()
b.show_axis_labels = True

# Add only the problematic vectors
states = [
    (QuantumState(state_vector=np.array([1, 1])/np.sqrt(2)), '|+⟩', 'x-axis'),
    (QuantumState(state_vector=np.array([1, 0])), '|0⟩', 'z-axis'),
]

for state, label, axis in states:
    # Calculate Bloch vector
    x = state.expectation(np.array([[0, 1], [1, 0]], dtype=complex))
    y = state.expectation(np.array([[0, -1j], [1j, 0]], dtype=complex))
    z = state.expectation(np.array([[1, 0], [0, -1]], dtype=complex))
    
    print(f"{label} ({axis}): Bloch vector = ({x:.3f}, {y:.3f}, {z:.3f})")
    print(f"  Length = {np.sqrt(x**2 + y**2 + z**2):.3f}")
    print(f"  Screen coords: xs={y:.3f}, ys={-x:.3f}, zs={z:.3f}")
    
    b.add_states(state, kind='vector', alpha=0.95)
    b.add_annotation_smart([x, y, z], label, offset=0.25, fontsize=14)

# Add coordinate axes for reference
b.add_vectors([[1, 0, 0]], colors='red', alpha=0.5)  # x-axis
b.add_vectors([[0, 1, 0]], colors='green', alpha=0.5)  # y-axis
b.add_vectors([[0, 0, 1]], colors='blue', alpha=0.5)  # z-axis

b.save('debug_coordinates.png', dpin=300)