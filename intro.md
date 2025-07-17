![Introduction Banner](figures/preface.png)
# Introduction
_Quantum computing_ has long been the province of physicists, a dreamy child of Feynman's lectures and Shor's revolution. But it’s 2025. We’re no longer dreaming—we’re prototyping. Quantum devices are humming in labs, cloud services offer qubit access with a few lines of Python, and researchers are scaling, optimizing, and debugging real systems.

And yet, learning quantum computing still often begins with Dirac notation and ends with a vague feeling of mystified awe. What if, instead, we rolled up our sleeves, cracked open a Jupyter notebook, and _built_ a quantum stack from scratch?

This book invites you to do just that.

**Build a Quantum Computing Stack in Python** is for the curious computer scientist—someone with an undergraduate background, a solid grasp of linear algebra (you know what a matrix is and you’re not afraid to use it), and an itch to build. If you're tired of pushing buttons on black-box libraries and want to know what’s really going on beneath the hood of a quantum circuit, you're in the right place.

We’ll begin our journey not at the top or bottom, but at the vibrant **center of the stack**—where quantum circuits come alive.

- **Meet the Qubits**: Vectors, gates, and the Bloch sphere—your new best friends.
- **Write a Circuit Simulator**: Build your own Python engine to evolve quantum states.
- **Invent a Quantum Language**: Design a mini language and parser to express your circuits elegantly.
- **Put It to Work**: Implement foundational protocols like **quantum teleportation**, **superdense coding**, and the **Deutsch-Jozsa algorithm** to show off your stack.
- **Descend to the Pulse Layer**: Learn matrix exponentiation, then design control pulses and build a basic pulse-level simulator.
- **Speak Native**: Understand hardware-native gates and pulse calibration.
- **Compile Like a Pro**: Write a compiler that maps high-level gates to low-level instructions.
- **Model the Machine**: From first principles, simulate a simplified superconducting qubit device—coherence, anharmonicity, and all.
- **Bridge the Classical-Quantum Divide**: Dive into hybrid algorithms and variational methods.
- **Face the Noise**: Introduce decoherence, density matrices, and upgrade your simulator to handle mixed states.
- **Patch the Holes**: Explore the beginnings of **quantum error correction** and the logic behind fault-tolerant computing.

Each layer you build peels back the abstraction of modern quantum software—until what once looked like magic becomes a set of (beautifully weird) engineering choices.


All in **pure Python**, without relying on pre-built quantum computing libraries like Qiskit or Cirq. This is quantum DIY. Along the way, we’ll reconstruct the core ideas of quantum computing, not as spectators, but as builders.

> “What I cannot create, I do not understand.” — Richard Feynman (probably)

Of course, we won’t do it all. Quantum computing in 2025 is vast—spanning physics, CS, electrical engineering, and mathematics. We won’t design superconducting qubit chips in this book. We won’t prove the threshold theorem from scratch. But we will get close enough to _touch_ the logic beneath them. You’ll finish with a deep understanding of the software stack, and a strong foundation to dive into more specialized research or development.

This book is opinionated, hands-on, and full of respect for the classics. We love Nielsen and Chuang. But we also believe the time has come for a new type of quantum book—one that feels less like a textbook and more like a project, a collaboration, a stack to build and own.

Let’s get started.

With curiosity and a compiler,

**The Author**

