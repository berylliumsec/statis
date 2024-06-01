import os
from Cython.Build import cythonize
from setuptools import setup

# Update here to include 'decoy.py' directly
exclude_files = ["setup.py","__init__.py"]

# Updated list comprehension to handle the files directly in the current directory
filenames = [
    os.path.join(".", f)
    for f in os.listdir(".")
    if f.endswith(".py") and f not in exclude_files
]

# Setting up the Cython modules excluding specified files
setup(
    ext_modules=cythonize(filenames),
    compiler_directives={"linetrace": True, "boundscheck": True},
)
