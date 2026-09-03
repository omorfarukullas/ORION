#!/usr/bin/env python3
"""
setup.py for ORION — Operational Responsive Intelligent Orchestration Network
"""

from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
readme_path = this_dir / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

requirements = []
req_file = this_dir / "requirements.txt"
if req_file.exists():
    for line in req_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="orion-assistant",
    version="2.0.0",
    author="Omor Faruck Ullas",
    author_email="omor.farukh16@gmail.com",
    description="Operational Responsive Intelligent Orchestration Network — Local-first AI Voice Assistant for PC Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omorfarukullas/ORION",
    license="MIT",
    packages=find_packages(exclude=["tests*", "scratch*"]),
    include_package_data=True,
    package_data={
        "": [
            "config/*.json",
            "data/*.csv",
            "data/*.json",
            "models/*.pkl",
            "web/*",
        ]
    },
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "orion = app:main",
            "orion-web = api.server:run_api_server",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.11",
)
