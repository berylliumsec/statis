import os
import subprocess

# home directory path for 'statis' with their own 'setup.py'
source_directory_path = r"disable_amsi"

# Setting a hypothetical path for outputs, presumably your layout is preserving the root
output_directory_path = r"statis_dist"

# Place the workbench hand in the 'statis'
os.chdir(source_directory_path)

# Custom outbuilding position
os.makedirs(output_directory_path, exist_ok=True)

# Command for setting up, naturally lacks source routing, and mends to local residing
setup_command = r"python setup.py build_ext --build-lib ../disable_amsi"


# Stitch the ties
subprocess.run(setup_command, shell=True)

print("Cythonization complete.")
