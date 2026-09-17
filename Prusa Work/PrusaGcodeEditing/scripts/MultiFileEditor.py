import tkinter as tk
from tkinter import filedialog
import os
import re
from PrusaGcodeEditing import GcodeEditor

# Print parameters
ironing_passes = [2,2,2,2,2,2]
layer_temps = [[240,230,220],[240,230,220],[240,230,220],[240,230,220],[240,230,220],[240,230,220]]
z_offset = [0.00,0.00,0.00,0.00,0.00,0.00]

# Function definitions
# def get_last_extrusion(gcode):
#     """ Purpose: find the last known extrude commanded position (or relative position)
#     args:
#         - print_code,   the ASCII-text G-code for just the printing section of an object
#     returns:
#         - e_val,        the last known extruder position returns 0 if none found
#     """

#     for line in reversed(gcode):
#         cmd_match = re.match(r'^(G0|G1)\b', line)
#         if not cmd_match:
#             continue
#         e_match = re.search(r'\sE(-?\d*\.?\d+)', line)
#         if e_match:
#             return float(e_match.group(1))

#     return 0

# Open a G-code editor
editor = GcodeEditor()

# Use Tkinter to prompt the user to open a folder
root = tk.Tk()
root.withdraw()  # hide the empty root window
dir = "D:\\Github Stuff\\Cylindrical-4th-Axis-Printer\\Prusa Work"
folder_path = filedialog.askdirectory(
    title="Select folder containing .gcode files",
    initialdir = dir
    )
if not folder_path:
    raise ValueError("No folder was selected.")

# Get the file path to the first .gcode file in the folder arranged alphabetically
gcode_files = sorted(
    f for f in os.listdir(folder_path) if f.lower().endswith(".gcode")
)

# Check to make sure there are the right number of G-code files
if not gcode_files:
    raise FileNotFoundError(f"No .gcode files found in folder: {folder_path}")
if len(gcode_files) != len(ironing_passes):
    raise IndexError(f"The number of .gcode files in the selected folder ({len(gcode_files)}) doesn't match the number of entries in the printing parameters ({len(ironing_passes)})")

file_path = os.path.join(folder_path, gcode_files[0])
with open(file_path) as f:
        contents = f.readlines()

start_code, print_code, end_code = editor.edit_gcode(contents,ironing_passes[0],layer_temps[0],z_offset[0])

edited_contents = start_code + print_code

for i in range(1,len(ironing_passes)):
    # Get the file path to the next .gcode file in the folder arranged alphabetically
    file_path = os.path.join(folder_path, gcode_files[i])
    with open(file_path) as f:
        contents = f.readlines()

    _, print_code, _ = editor.edit_gcode(contents,ironing_passes[i],layer_temps[i],z_offset[i])
    
    # add object start G-code between objects
    object_start_code = [
        "\n; Object Start Sequence\n",
        "G91   		; relative positioning mode\n",
        "G0 Z10		; move up to avoid collisions\n",
        "G90   		; absolute positioning mode\n",
        "M83 		; extruder relative mode\n",
        f"G0 X{0:.2f} F10000;  move to wiping X position\n"
    ]

    edited_contents = edited_contents + object_start_code + print_code

edited_contents = edited_contents + end_code

# Write to a new file in the same folder 
output_path = os.path.join(folder_path, "combined_gcode.gcode")
with open(output_path, "w") as f:
    f.writelines(edited_contents)

# Debugging
print("Done")
