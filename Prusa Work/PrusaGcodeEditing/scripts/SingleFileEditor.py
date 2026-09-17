import tkinter as tk
from tkinter import filedialog
import os
from PrusaGcodeEditing import GcodeEditor


# Print parameters
ironing_passes = 2              # Number of times to repeat the first layer, with 0 printing the first layer once
max_x_pos = 320                 # Max position the x axis can go to before crashing
layer_temps = [260,235,220]     # Temperatures for layers to print in C. The last temp in list used for all subsequent layers
layer_speeds = [20,20,20]       # For each layer, perimeter speeds in mm/s. Infill will be printed at 1.25X perimeter speed. Layers not indicated will not be changed
extrusion_mult = 1.5            # Extrusion multiplier FOR THE FIRST LAYER ONLY. Affects only positive extrusions
z_offset = 0.00                 # Offset from surface of mesh to first layer print height

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
    dir = "D:\\Github Stuff\\Cylindrical-4th-Axis-Printer\\Prusa Work"
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

# Get Gcode file & extract contents
unedited_file_path = select_file()
if not unedited_file_path:
    raise FileNotFoundError("No file selected")

with open(unedited_file_path) as unedited_f:
    contents = unedited_f.readlines()

editor = GcodeEditor()
start_code, print_code, end_code = editor.edit_gcode(contents, ironing_passes, layer_temps, layer_speeds, extrusion_mult, z_offset)

contents = start_code + print_code + end_code

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
