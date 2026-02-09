#!/usr/bin/env python3
"""
AutoMesh setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements" / "base.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'trimesh>=3.9.0',
        'open3d>=0.13.0',
    ]

setup(
    name='automesh',
    version='1.0.0',
    description='Automatic CFD mesh refinement tool for OpenFOAM snappyHexMesh',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AutoMesh Contributors',
    url='https://github.com/karthikt/AutoMesh',
    license='MIT',
    
    # Package discovery
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        'meshmind': [
            'templates/snappyhexmesh/*.yml',
        ],
    },
    
    # Dependencies
    python_requires='>=3.8',
    install_requires=requirements,
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=0.5',
        ],
    },
    
    # CLI entry point
    entry_points={
        'console_scripts': [
            'automesh=automesh_cli:main',
        ],
    },
    
    # PyPI classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    
    keywords='cfd mesh openfoam snappyhexmesh stl geometry',
    
    project_urls={
        'Documentation': 'https://karthikt.github.io/AutoMesh',
        'Source': 'https://github.com/karthikt/AutoMesh',
        'Bug Reports': 'https://github.com/karthikt/AutoMesh/issues',
    },
)
