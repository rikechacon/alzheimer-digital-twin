#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Alzheimer Digital Twin - Setup Configuration"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="alzdt",
    version="0.8.0",
    author="Alzheimer Digital Twin Consortium",
    author_email="alzdt.collab@digitaltwin.org",
    description="Sistema ciber-físico-biológico para prevención personalizada del Alzheimer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alzheimer-digital-twin/alzdt-core",
    packages=find_packages(exclude=["tests*", "notebooks*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "full": [
            "jax>=0.4.16",
            "pygmo>=2.19.0",
            "nibabel>=5.1.0",
            "monai>=1.2.0",
            "sqlalchemy>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "alzdt-simulate=alzdt.cli:simulate",
            "alzdt-optimize=alzdt.cli:optimize",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
