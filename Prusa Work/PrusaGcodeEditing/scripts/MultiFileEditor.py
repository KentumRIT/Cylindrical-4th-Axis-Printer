import tkinter as tk
from tkinter import filedialog
import os
import re
from PrusaGcodeEditing import GcodeEditor


# Print parameters
standard_printing_temp = 220                                # deg C
first_layer_temps = [260, 260, 260, 260, 260, 260]          # layer temps for each print are first layer temp, midpoint, standard printing temp

first_layer_speed_mults = [0.45, 0.45, 0.45, 0.45, 0.45, 0.45]    # layer speed multipliers for each print are first layer mult, midpoint, 1.0

ironing_passes = [1, 1, 1, 1, 1, 1]                         # how many times to repeat 1st layer G-code with no additional extrusion

z_offsets = [0.25, 0.25, 0.25, 0.25, 0.25, 0.25]            # distance between the mandrel surface and the first layer in the Z direction

extrusion_mults= [1.75, 1.75, 1.75, 1.75, 1.75, 1.75]             # multiplier for positive extrusion moves in the first layer


# Open a G-code editor
editor = GcodeEditor()

# Use Tkinter to prompt the user to open a folder
root = tk.Tk()
root.withdraw()  # hide the empty root window
dir = "D:\\Github Stuff\\Cylindrical-4th-Axis-Printer\\Prusa Work\\Adhesion Testing\\Variance Testing"
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



layer_temps = [first_layer_temps[0], round((first_layer_temps[0] + standard_printing_temp)/2) , standard_printing_temp]
speed_mults = [first_layer_speed_mults[0], float(first_layer_speed_mults[0] + 1)/2 , 1]

start_code, print_code, end_code = editor.edit_gcode(contents,ironing_passes[0],layer_temps,speed_mults,extrusion_mults[0],z_offsets[0])

edited_contents = start_code + print_code

# Edit the G-code for each file
for i in range(1,len(ironing_passes)):
    # Get the file path to the next .gcode file in the folder arranged alphabetically
    file_path = os.path.join(folder_path, gcode_files[i])
    with open(file_path) as f:
        contents = f.readlines()

    layer_temps = [first_layer_temps[i], round((first_layer_temps[i] + standard_printing_temp)/2) , standard_printing_temp]
    speed_mults = [first_layer_speed_mults[i], float(first_layer_speed_mults[i] + 1)/2 , 1]

    _, print_code, _ = editor.edit_gcode(contents,ironing_passes[i],layer_temps,speed_mults,extrusion_mults[i],z_offsets[i])
    
    # add object start G-code between objects
    object_start_code = [
        "\n; Object Start Sequence\n",
        "G91   		; relative positioning mode\n",
        "G0 Z10		; move up to avoid collisions\n",
        "G90   		; absolute positioning mode\n",
        "M83 		; extruder relative mode\n",
        f"G0 X{0:.2f} F10000;  move to wiping X/Y position\n",
        f"G0 Y{0:.2f}\n\n"
    ]

    edited_contents = edited_contents + object_start_code + print_code

edited_contents = edited_contents + end_code

# Write to a new file in the same folder 
# output_path = os.path.join(folder_path, "combined_gcode.gcode")
output_path = os.path.join("D:\\Github Stuff\\Cylindrical-4th-Axis-Printer\\Prusa Work\\Adhesion Testing\\Variance Testing\\Printing G-code\\change_this_name.gcode")
with open(output_path, "w") as f:
    f.writelines(edited_contents)

# Debugging
print("Done")
