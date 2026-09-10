import tkinter as tk
from tkinter import filedialog
import os
import re

# Print parameters
first_layer_repeat = 2          # Number of times to repeat the first layer, with 0 printing the first layer once
max_x_pos = 320                 # Max position the x axis can go to before crashing
layer_temps = [260,235,220]     # Temperatures for layers to print in C. The last temp in list used for all subsequent layers
z_offset = -0.15                # Offset between probing nozzle and printing nozzle

# Function definitions
def select_file():
    """ Purpose: Get user selected filepath
    args:
        - root, active Tkinter window
    returns:
        - file_path, file path to the selected file, empty if none was selected
    """

    # Run Tkinter
    root = tk.Tk()  # Create Tkinter window for parent
    root.withdraw() # Hide root window
    
    # Get the documents filepath, open the file dialog box at documents, get selected file path
    # documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
    dir = "D:\\Github Stuff\\Cylindrical-4th-Axis-Printer\\Adhesion Testing Print Files"
    file_path = filedialog.askopenfilename(
        title="Select a File",
        initialdir=dir,
        filetypes=(
            ("GCODE Files", "*.gcode"),
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        )
    )
    
    # Close the Tkinter window
    root.destroy()

    # Return the selected filepath
    return file_path

def get_layer_changes(contents):
    """ Purpose: Get line number (indices) of all layer starts in contents
    args:
        - contents, a list of strings where each entry is a line of Gcode
    returns:
        - layer_starts, a list of indices for contents where each entry is the start of a new layer
    """

    layer_indices = [i for i, line in enumerate(contents)
                 if ";LAYER_CHANGE" in line]
    
    last_section = contents[layer_indices[-1]:]
    try:
        last_index = last_section.index(";TYPE:Custom\n") + layer_indices[-1]
    except ValueError:
        raise ValueError("End Gcode not found")

    layer_indices.append(last_index)
    return layer_indices

def adjust_z(match):
    """ Purpose: Adjust Z values in gcode
    args:
        - match, a regular expression match for number following "Z"
    returns:
        - z_val, adjusted Z value as a string 
    """

    z_val = float(match.group(1))
    z_val += z_offset
    return f"Z{z_val:.4f}"

# Get Gcode file & extract contents
unedited_file_path = select_file()
if not unedited_file_path:
    raise FileNotFoundError("No file selected")

with open(unedited_file_path) as unedited_f:
    contents = unedited_f.readlines()

# Get indices for all layer changes
layer_indices = get_layer_changes(contents)

# Delete all old temperature commands from within layers
contents[layer_indices[0]:layer_indices[-1]] = [
    line for line in contents[layer_indices[0]:layer_indices[-1]]
    if not re.match(r'^(M104|M109)\b', line)
]

# Get indices for all layer changes
layer_indices = get_layer_changes(contents)

# Check if the print head will crash into the mandrel holders
pattern = re.compile(r'^(G0|G1).*?X([-+]?\d*\.?\d+)')
for line in contents:
    match = pattern.search(line)
    if match:
        if float(match.group(2)) > max_x_pos:
            raise ValueError("X axis moves outside of range")

# Shift Z values of all movement commands in layer printing up to mandrel height
pattern = re.compile(r'Z([-+]?\d*\.?\d+)')
contents[layer_indices[0]:layer_indices[-1]] = [
    pattern.sub(adjust_z, line)
    for line in contents[layer_indices[0]:layer_indices[-1]]
]

# Re-zero extruder at start of repeated layer
first_layer_lines = contents[layer_indices[0]:layer_indices[1]]
first_layer_lines.insert(3,f"G92 E0.0\n")

# Insert repeated first layer gcode
for i in range(first_layer_repeat):
    contents[layer_indices[1]:layer_indices[1]] = first_layer_lines
    for i in range(1,len(layer_indices)): layer_indices[i] += len(first_layer_lines)

# Add temperature commands for every layer
num_layers = len(layer_indices) - 1
for i in range(min(len(layer_temps), num_layers)):
    temp = layer_temps[i]
    contents.insert(layer_indices[i]+4,f"M109 R{temp:d}\n")
    for j in range(i+1,len(layer_indices)): layer_indices[j] += 1

# Write to a new edited file
base, ext = os.path.splitext(unedited_file_path)
edited_file_path = f"{base}_edited{ext}"
with open(edited_file_path, "w") as edited_f:
    edited_f.writelines(contents)

# Debugging
print("Done")


# Unused code
# # Get first layer height & check errors
# pattern = re.compile(r";Z:([-+]?\d*\.?\d+)\n")
# first_layer_z = [
#     float(pattern.match(line).group(1))
#     for line in first_layer_lines
#     if pattern.match(line)
# ]
# if len(first_layer_z) == 0:
#     raise ValueError("No layer height line <;Z:XX> found in layer 1")
# elif len(first_layer_z) > 1:
#     raise ValueError("More than one layer height line <;Z:XX> found in layer 1")
# first_layer_z = first_layer_z[0]

# # Add pre-print z move and waits
# # Find pre-print nozzle heating
# try:
#    pre_print_index = contents.index("; set extruder temp\n")
# except ValueError:
#    pre_print_index = layer_starts[0]
# contents.insert(pre_print_index,"G92 Z0\n")                 # Rezero Z
# contents.insert(pre_print_index,"G0 Z28.5\n")               # Move bed up to print height
# contents.insert(pre_print_index,"T0 S1 L0 D0")              # Pick up tool
# contents.insert(pre_print_index,"M601\n")                   # Wait for user inpuit
# contents.insert(pre_print_index,"M117 Attach mandrels\n")   # Display message
# contents.insert(pre_print_index,"P0 S1 L2 D0")              # Park tool
# contents.insert(pre_print_index,"G0 Z150\n")                # Move bed down
# for i in range(len(layer_starts)): layer_starts[i] += 7     # Update layer starts with added lines
