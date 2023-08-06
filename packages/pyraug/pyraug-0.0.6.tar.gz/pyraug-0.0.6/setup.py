import pathlib

import pkg_resources
from setuptools import find_packages, setup

with pathlib.Path("requirements.txt").open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyraug",
    version="0.0.6",
    author="Clement Chadebec (HekA team INRIA)",
    author_email="clement.chadebec@inria.fr",
    description="Data Augmentation with VAE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clementchadebec/pyraug",
    project_urls={"Bug Tracker": "https://github.com/clementchadebec/pyraug/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "numpy>=1.22.0",
        "Pillow>=8.3.2",
        "torch>=1.8.1",
        "dill>=0.3.3",
        "nibabel>=3.2.1",
        "pydantic>=1.8.2",
        "dataclasses>=0.6",
    ],
    python_requires=">=3.6",
)
