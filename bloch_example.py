"""
Example usage of the refactored Bloch sphere visualization.
"""

import numpy as np
import os
from qsip.visualization.bloch import Bloch, QuantumState, pauli_x, pauli_y, pauli_z

# Create output directory
output_dir = "bloch_outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Example 1: Create and plot a simple qubit state
def example_basic():
    """Basic example with a single qubit state."""
    # Create a Bloch sphere
    b = Bloch()
    
    # Create a quantum state |+⟩ = (|0⟩ + |1⟩)/√2
    plus_state = QuantumState(state_vector=np.array([1, 1])/np.sqrt(2))
    
    # Add the state as a vector
    b.add_states(plus_state, kind='vector')
    
    # Save the Bloch sphere
    b.save(name=os.path.join(output_dir, 'example_basic.png'), dpin=300)
    print(f"Saved: {output_dir}/example_basic.png")


# Example 2: Multiple states with custom colors
def example_multiple_states():
    """Example with multiple quantum states."""
    b = Bloch()
    
    # Create several quantum states
    states = [
        QuantumState(state_vector=np.array([1, 0])),  # |0⟩
        QuantumState(state_vector=np.array([0, 1])),  # |1⟩
        QuantumState(state_vector=np.array([1, 1])/np.sqrt(2)),  # |+⟩
        QuantumState(state_vector=np.array([1, -1])/np.sqrt(2)),  # |−⟩
        QuantumState(state_vector=np.array([1, 1j])/np.sqrt(2)),  # |i⟩
        QuantumState(state_vector=np.array([1, -1j])/np.sqrt(2)),  # |−i⟩
    ]
    
    # Hide axis labels since we have custom annotations
    b.show_axis_labels = False
    
    # Add states with default Morandi colors (automatically cycles through palette)
    for state in states:
        b.add_states(state, kind='vector', alpha=0.9)
    
    # Add labels using smart positioning with Unicode ket notation
    b.add_annotation_smart([0, 0, 1], r'$|0⟩$', offset=0.25, fontsize=14)
    b.add_annotation_smart([0, 0, -1], r'$|1⟩$', offset=0.25, fontsize=14)
    b.add_annotation_smart([1, 0, 0], r'$|+⟩$', offset=0.25, fontsize=14)
    b.add_annotation_smart([-1, 0, 0], r'$|-⟩$', offset=0.25, fontsize=14)
    b.add_annotation_smart([0, 1, 0], r'$|+i⟩$', offset=0.25, fontsize=14)
    b.add_annotation_smart([0, -1, 0], r'$|-i⟩$', offset=0.25, fontsize=14)
    
    b.save(name=os.path.join(output_dir, 'example_multiple_states.png'), dpin=300)
    print(f"Saved: {output_dir}/example_multiple_states.png")


# Example 3: Trajectory on the Bloch sphere
def example_trajectory():
    """Example showing a trajectory on the Bloch sphere."""
    b = Bloch()
    
    # Create a trajectory of states
    t = np.linspace(0, 2*np.pi, 50)
    points = []
    
    for theta in t:
        # Rotate around the equator
        state_vector = np.array([np.cos(theta/2), np.sin(theta/2) * np.exp(1j * 0)])
        state = QuantumState(state_vector=state_vector)
        vec = [state.expectation(pauli_x()), 
               state.expectation(pauli_y()), 
               state.expectation(pauli_z())]
        points.append(vec)
    
    # Add as connected points
    points = np.array(points).T
    b.add_points(points, meth='l', colors='#95859C', alpha=0.8)  # Soft purple-grey
    
    # Add start and end points
    b.add_points(points[:, 0:1], meth='s', colors='#B08291')  # Dusty rose
    b.add_points(points[:, -1:], meth='s', colors='#6B9080')  # Forest sage
    
    b.save(name=os.path.join(output_dir, 'example_trajectory.png'), dpin=300)
    print(f"Saved: {output_dir}/example_trajectory.png")


# Example 4: Mixed states
def example_mixed_states():
    """Example with mixed quantum states."""
    b = Bloch()
    
    # Pure state at the north pole
    pure_state = QuantumState(state_vector=np.array([1, 0]))
    b.add_states(pure_state, kind='vector', colors='#95859C')  # Soft purple-grey
    
    # Maximally mixed state (center of sphere)
    mixed_state = QuantumState(density_matrix=np.eye(2)/2)
    b.add_states(mixed_state, kind='point', colors='#B08291')  # Dusty rose
    
    # Partially mixed states
    for p in [0.7, 0.5, 0.3]:
        rho = p * np.outer([1, 0], [1, 0]) + (1-p) * np.eye(2)/2
        partial_mixed = QuantumState(density_matrix=rho)
        b.add_states(partial_mixed, kind='point', colors='#C89F83', alpha=0.8)  # Rich terracotta
    
    b.add_annotation([0, 0, 0.1], r'$\rho = \frac{\mathbb{I}}{2}$', fontsize=12, 
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFEF5', 
                              edgecolor='#8B7355', alpha=0.9))
    
    b.save(name=os.path.join(output_dir, 'example_mixed_states.png'), dpin=300)
    print(f"Saved: {output_dir}/example_mixed_states.png")


if __name__ == "__main__":
    print("Running Bloch sphere examples...")
    print(f"Output directory: {output_dir}")
    print("-" * 40)
    
    print("\n1. Basic example:")
    example_basic()
    
    print("\n2. Multiple states:")
    example_multiple_states()
    
    print("\n3. Trajectory:")
    example_trajectory()
    
    print("\n4. Mixed states:")
    example_mixed_states()
    
    print("\n" + "-" * 40)
    print(f"All examples saved to '{output_dir}/' directory")