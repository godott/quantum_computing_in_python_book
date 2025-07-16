"""Test mathematical notation and expressions on the Bloch sphere."""

import numpy as np
from bloch_refactored import Bloch, QuantumState

# Example 1: Basic quantum states with mathematical expressions
b1 = Bloch()
b1.show_axis_labels = True  # Show axis labels with unit vector notation

# Add some basic states
states = [
    QuantumState(state_vector=np.array([1, 0])),  # |0⟩
    QuantumState(state_vector=np.array([1, 1])/np.sqrt(2)),  # |+⟩
    QuantumState(state_vector=np.array([1, 1j])/np.sqrt(2)),  # |+i⟩
]

for state in states:
    b1.add_states(state, kind='vector', alpha=0.95)

# Add mathematical annotations
b1.add_annotation_smart([0, 0, 1], r'$|0⟩$', offset=0.3, fontsize=16)
b1.add_annotation_smart([1, 0, 0], r'$|+⟩ = \frac{|0⟩ + |1⟩}{\sqrt{2}}$', 
                        offset=0.4, fontsize=13)
b1.add_annotation_smart([0, 1, 0], r'$|+i⟩ = \frac{|0⟩ + i|1⟩}{\sqrt{2}}$', 
                        offset=0.4, fontsize=13)

b1.save('test_math_basic.png', dpin=300)

# Example 2: Bloch vector representation
b2 = Bloch()
b2.show_axis_labels = False
b2.set_label_convention("sx sy sz")  # Use Pauli operator notation

# Add a general state
theta = np.pi/3
phi = np.pi/4
state = QuantumState(state_vector=np.array([np.cos(theta/2), 
                                           np.sin(theta/2)*np.exp(1j*phi)]))
b2.add_states(state, kind='vector', colors='#95859C')

# Add Bloch vector components
vec = [state.expectation(np.array([[0, 1], [1, 0]], dtype=complex)),
       state.expectation(np.array([[0, -1j], [1j, 0]], dtype=complex)),
       state.expectation(np.array([[1, 0], [0, -1]], dtype=complex))]

# Add mathematical expression for the state
b2.add_annotation_smart(vec, 
    r'$|\psi⟩ = \cos\left(\frac{\theta}{2}\right)|0⟩ + e^{i\phi}\sin\left(\frac{\theta}{2}\right)|1⟩$',
    offset=0.5, fontsize=12)

# Add axis labels manually
b2.add_annotation([1.3, 0, 0], r'$\langle\hat{\sigma}_x\rangle$', fontsize=14)
b2.add_annotation([0, 1.3, 0], r'$\langle\hat{\sigma}_y\rangle$', fontsize=14)
b2.add_annotation([0, 0, 1.3], r'$\langle\hat{\sigma}_z\rangle$', fontsize=14)

b2.save('test_math_bloch_vector.png', dpin=300)

# Example 3: Density matrix representation
b3 = Bloch()
b3.show_axis_labels = False

# Pure state
pure = QuantumState(state_vector=np.array([np.sqrt(0.8), np.sqrt(0.2)*np.exp(1j*np.pi/6)]))
b3.add_states(pure, kind='vector', colors='#6B9080', alpha=0.9)

# Mixed state with purity
purity = 0.7
mixed_state = QuantumState(density_matrix=purity*pure.density_matrix + (1-purity)*np.eye(2)/2)
b3.add_states(mixed_state, kind='point', colors='#B08291', alpha=0.9)

# Add annotations
b3.add_annotation_smart([pure.expectation(np.array([[0, 1], [1, 0]], dtype=complex)),
                         pure.expectation(np.array([[0, -1j], [1j, 0]], dtype=complex)),
                         pure.expectation(np.array([[1, 0], [0, -1]], dtype=complex))],
                        r'$|\psi⟩⟨\psi|$', 
                        offset=0.3, fontsize=14)

b3.add_annotation_smart([mixed_state.expectation(np.array([[0, 1], [1, 0]], dtype=complex)),
                         mixed_state.expectation(np.array([[0, -1j], [1j, 0]], dtype=complex)),
                         mixed_state.expectation(np.array([[1, 0], [0, -1]], dtype=complex))],
                        r'$\rho = 0.7|\psi⟩⟨\psi| + 0.3\frac{\mathbb{I}}{2}$',
                        offset=0.3, fontsize=12)

# Add purity label
b3.add_annotation([0, 0, -1.3], r'$\mathcal{P} = \mathrm{Tr}(\rho^2) = ' + f'{purity**2 + (1-purity)**2/2:.2f}$', 
                  fontsize=12, horizontalalignment='center')

b3.save('test_math_density_matrix.png', dpin=300)

print("Mathematical notation examples saved:")
print("1. test_math_basic.png - Basic quantum states with expressions")
print("2. test_math_bloch_vector.png - Bloch vector representation")
print("3. test_math_density_matrix.png - Density matrix and purity")