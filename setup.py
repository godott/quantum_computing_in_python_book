"""Setup configuration for QSIP - Quantum Stack in Python."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qsip",
    version="0.1.0",
    author="Yunong Shi",
    author_email="your.email@example.com",
    description="A pure Python implementation of quantum computing concepts for educational purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/godott/quantum-book",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
            "ipykernel>=6.0.0",
            "ipython>=7.30.0",
        ],
        "translators": [
            "openqasm3>=1.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/godott/quantum-book/issues",
        "Source": "https://github.com/godott/quantum-book",
        "Documentation": "https://godott.github.io/quantum-book/",
    },
)