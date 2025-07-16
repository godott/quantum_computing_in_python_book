"""Final test showcasing all improvements to the Bloch sphere."""

import numpy as np
from bloch_refactored import Bloch, QuantumState

# Create a Bloch sphere with all improvements
b = Bloch()
b.show_axis_labels = False  # Clean look without overlapping labels

# Add states showcasing the enriched Morandi color palette
states_and_labels = [
    (QuantumState(state_vector=np.array([1, 0])), r'$|0\rangle$'),  # North pole
    (QuantumState(state_vector=np.array([0, 1])), r'$|1\rangle$'),  # South pole
    (QuantumState(state_vector=np.array([1, 1])/np.sqrt(2)), r'$|+\rangle$'),  # +x
    (QuantumState(state_vector=np.array([1, -1])/np.sqrt(2)), r'$|-\rangle$'),  # -x
    (QuantumState(state_vector=np.array([1, 1j])/np.sqrt(2)), r'$|+i\rangle$'),  # +y
    (QuantumState(state_vector=np.array([1, -1j])/np.sqrt(2)), r'$|-i\rangle$'),  # -y
]

# Add states as vectors with automatic color cycling
for i, (state, label) in enumerate(states_and_labels):
    b.add_states(state, kind='vector', alpha=0.95)
    # Get the vector position for smart annotation
    vec = [state.expectation(np.array([[0, 1], [1, 0]], dtype=complex)),  # X
           state.expectation(np.array([[0, -1j], [1j, 0]], dtype=complex)),  # Y
           state.expectation(np.array([[1, 0], [0, -1]], dtype=complex))]  # Z
    b.add_annotation_smart(vec, label, offset=0.3, fontsize=15, weight='bold')

# Add a circular trajectory to show smooth sphere
theta = np.linspace(0, 2*np.pi, 100)
trajectory = []
for t in theta:
    trajectory.append([np.cos(t) * 0.8, np.sin(t) * 0.8, 0])
trajectory = np.array(trajectory).T
b.add_points(trajectory, meth='l', colors='#7A8FA6', alpha=0.3)  # Steel blue with transparency

# Save with high DPI to show smooth sphere
b.save('test_final_improvements.png', dpin=300)

print("Final test image saved as 'test_final_improvements.png'")
print("\nImprovements demonstrated:")
print("1. Warmer creamy white sphere (#FFFEF5) - less grey")
print("2. Enriched Morandi color palette:")
print("   - #C89F83: Rich terracotta")
print("   - #6B9080: Forest sage")
print("   - #95859C: Soft purple-grey")
print("   - #B08291: Dusty rose")
print("   - #9B8F78: Golden ochre")
print("   - #7A8FA6: Steel blue")
print("3. Larger boundaries to prevent cropping")
print("4. Smoother sphere with 50x50 grid (vs 25x25)")
print("5. No axis labels for cleaner appearance")
print("6. Smart annotation positioning")