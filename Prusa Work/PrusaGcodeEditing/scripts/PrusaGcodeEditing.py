import re


class GcodeEditor:
    """ READ ME

        PURPOSE:
            - This class is built to edit ASCII-style G-code for mesh printing on the PRiSM Lab's PrusaXL printer
            - This is not a very robust system, it relies on exact text-matching to find the end of start G-code and the start of end G-code. Make sure you use the Prusa Slicer to generate the G-code
    
        IMPLEMENTED FEATURES:
            - Pre-printing prime & wipe sequence
            - First layer ironing
            - Checking for crash into mandrel holders
            - Layer-by-layer printing temp control
            - First-layer Z offset from mesh surface

        TODO:
            - None ATM
        """

    def __init__(self):
        # Define X/Y positions for wiping
        self.mandrel_y_positions = [10.3, 72.0, 133.9, 195.8, 257.3, 319.5]
        self.wipe_x_pos = 0

        # Define speed multipliers for each type of printing section
        # (sections defined with the ";TYPE:" header that aren't on the non-printing moves list will use a multiplier of 1)
        # all multipliers based off the default "speed for print moves" ratios in the Prusa slicer
        self.printing_move_types = [
            ("Perimeter", 1),
            ("Small perimeter", 1),
            ("External perimeter", 1),
            ("Overhang perimeter", 1),
            ("Internal infill", 20/17),
            ("Solid infill", 20/17),
            ("Top solid infill", 10/17),
            ("Bridge infill", 45/170),
            ("Support material", 12/17),
            ("Support material interface", 5/17)
        ]

        # Define non-printing move types. Speeds won't be changed here
        self.non_printing_move_types = [
            "Custom"
        ]



    def __get_first_xy(self, gcode: list[str]) -> tuple[float,float]:
        """ Purpose: scan G0/G1 commands in gcode and return the (x_val, y_val)
                position once both an X and a Y coordinate have been seen.
                Values persist across lines, so an X on one line and a Y on a
                later line are still paired together correctly.
                
            args:
                - gcode,       the ASCII-text G-code for just the printing section of an object
            
            returns:
                - x_val,    the first encountered X coordinate
                - y_val,    the first encountered Y coordinate
        """

        x_val, y_val = None, None
        for line in gcode:
            cmd_match = re.match(r'^(G0|G1)\b', line)
            if not cmd_match:
                continue
            x_match = re.search(r'\sX(-?\d*\.?\d+)', line)
            y_match = re.search(r'\sY(-?\d*\.?\d+)', line)
            if x_match:
                x_val = x_match.group(1)
            if y_match:
                y_val = y_match.group(1)
            if x_val is not None and y_val is not None:
                return float(x_val), float(y_val)

        raise ValueError("Could not find both an X and a Y position in gcode")

    def __get_layer_changes(self, gcode: list[str]) -> list[int]:
        """ Purpose: Get line number (indices) of all layer starts in gcode

            args:
                - gcode,        a list of strings where each entry is a line of G-code
            
            returns:
                - layer_starts, a list of indices for gcode where each entry is the start of a new layer
        """
        
        layer_indices = [i for i, line in enumerate(gcode)
                    if ";LAYER_CHANGE" in line]
        
        last_section = gcode[layer_indices[-1]:]
        try:
            last_index = last_section.index(";TYPE:Custom\n") + layer_indices[-1]
        except ValueError:
            raise ValueError("End G-code not found")
    
        layer_indices.append(last_index)
        return layer_indices

    def edit_gcode(self, gcode: list[str], ironing_passes: int, layer_temps: list[float], layer_speeds: list[float], extrusion_mult: float, z_offset: float, max_x_pos: float = 320) -> tuple[list[str], list[str], list[str]]:
        """ Purpose: Edit G-code for printing on mesh

            args:
                - gcode,            the ASCII-text G-code broken down into a list where each entry is a line of the original file (as happens when using readlines)
                - ironing_passes,   number of times to repeat the first layer, with 0 printing the first layer once
                - layer_temps,      temperatures for layers to print in C. The last temp in list used for all subsequent layers
                - layer_speeds,     for each layer, perimeter speeds in mm/s. Other printing moves will be a multiple of perimeter speed; see init for details. Non-printing moves won't have their speeds changed. Layers not indicated will not be changed
                - extrusion_mult,   extrusion multiplier FOR THE FIRST LAYER ONLY. Affects only positive extrusions. Slicing must be done in relative extrusion mode
                - z_offset,         offset from surface of mesh to first layer print height
                - max_x_pos,        max position the X axis can go to before crashing
            
            returns:
                - start_gcode,      all G-code up to the first instance of ;LAYER_CHANGE
                - printing_gcode,   all G-code between start and end G-code
                - end_gocde,        all G-code after and including ;TYPE:Custom
        """
        
        z_offset = z_offset - 0.15  # printing nozzle sits 0.15 mm higher than probing nozzle

        # Delete native Prusa object G-code
        gcode = [
            line for line in gcode
            if not re.match(r'^(M486)\b', line)
        ]

        # Isolate start and end G-code
        layer_indices = self.__get_layer_changes(gcode)
        start_gcode = gcode[0:layer_indices[0]]
        end_gcode = gcode[layer_indices[-1]:]
        printing_gcode = gcode[layer_indices[0]:layer_indices[-1] + 1]  # we include the ";TYPE:CUSTOM" line in the printing G-code so the __get_layer_changes() function recognizes end G-code


        # Check if print head will crash
        pattern = re.compile(r'^(G0|G1).*?X([-+]?\d*\.?\d+)')
        for line in gcode:
            match = pattern.search(line)
            if match:
                if float(match.group(2)) > max_x_pos:
                    raise ValueError("X axis moves outside of range")


        # Delete all old temperature commands from within printing G-code
        printing_gcode = [
            line for line in printing_gcode
            if not re.match(r'^(M104|M109)\b', line)
        ]


        # Find layer changes again now that we've deleted content
        layer_indices = self.__get_layer_changes(printing_gcode)


        # Shift Z values
        def adjust_z(match):
            z_val = float(match.group(1))
            z_val += z_offset
            return f"Z{z_val:.4f}"
        
        pattern = re.compile(r'Z([-+]?\d*\.?\d+)')
        printing_gcode = [
            pattern.sub(adjust_z, line)
            for line in printing_gcode[layer_indices[0]:layer_indices[-1]]
        ]


        # Adjust E values in first layer
        def adjust_e(match):
            e_val = float(match.group(1))
            if e_val > 0:
                e_val = e_val*extrusion_mult
            return f"E{e_val:0.6f}"

        pattern = re.compile(r'E([-+]?\d*\.?\d+)')
        first_layer_gcode = printing_gcode[layer_indices[0]:layer_indices[1]]
        first_layer_gcode = [
            pattern.sub(adjust_e, line)
            for line in first_layer_gcode
        ]
        printing_gcode[layer_indices[0]:layer_indices[1]] = first_layer_gcode


        # Adjust printing speeds
        num_layers = len(layer_indices) - 1
        for i in range(1,min(len(layer_speeds), num_layers)):
            layer_gcode = printing_gcode[layer_indices[0]:layer_indices[i+1]]


            for line in layer_gcode
            # Find a section of printing code beginning with ";TYPE:" 
        # Find the printing speed for this block, should immediately follow the comment block, if none found use previous known speed as printing speed for this block
        # Replace all instances of the printing speed with the modified speed, but leave non-printing moves (moves using higher speeds) alone

        # Ironing functionality
        if ironing_passes != 0:
            # Prepare ironing code by removing extrusion from G0/G1 moves in the first layer code
            first_layer_gcode = printing_gcode[layer_indices[0]:layer_indices[1]]
            pattern = re.compile(r'^(G0|G1)(.*?)(?:E[-+]?\d*\.?\d+)(.*)$', re.IGNORECASE)
            first_layer_gcode = [
                f"{match.group(1)}{match.group(2)}{match.group(3)}\n" 
                if (match := pattern.search(line)) else line
                for line in first_layer_gcode
            ]

            # Insert ironing G-code
            for i in range(ironing_passes):
                printing_gcode[layer_indices[1]:layer_indices[1]] = first_layer_gcode
                for i in range(1,len(layer_indices)): layer_indices[i] += len(first_layer_gcode)    # update layer indices as we go so we don't have to search again


        # Add temperature commands to each layer
        num_layers = len(layer_indices) - 1
        for i in range(1,min(len(layer_temps), num_layers)):                    # skip the first layer b/c we want to add that command inside the prime & wipe sequence
            temp = layer_temps[i]
            printing_gcode.insert(layer_indices[i]+4,f"M109 R{temp:d}\n")
            for j in range(i+1,len(layer_indices)): layer_indices[j] += 1       # update layer indices as we go so we don't have to search again


        # Add prime and wipe commands to first layer
        first_x,first_y = self.__get_first_xy(printing_gcode[layer_indices[0]:layer_indices[1]])
        #   mandrel_y = min(self.mandrel_y_positions, key=lambda n: abs(n-first_y))
        mandrel_y = self.mandrel_y_positions[0]
        wipe_speed = 700   # mm/min
        travel_speed = 10000
        num_wipes = 3

        wipe_start_gcode = [
            "\n; Prime and Wipe Sequence\n",
            f"G0 X{self.wipe_x_pos:.2f} Y{(mandrel_y):.2f} Z5 F{travel_speed}	; move to mandrel end\n",
            f"G0 Z0 F{wipe_speed}                	; rest on mandrel while heating\n",
            f"M109 R{layer_temps[0]}    			; wait for temp\n",
            f"G0 Y{(mandrel_y + 10):.2f} Z0.5 F{travel_speed}    	; move to first wipe position\n",
            f"G1 E8.0 F{wipe_speed}  			; purge nozzle\n",
            f"G4 S4                           ; wait for purge\n",
            f"G1 E-0.5 F{wipe_speed}          ; relieve pressure\n"
        ]
        wipe_gcode_fwrd = [
            f"G0 X{(self.wipe_x_pos):.2f} Y{(mandrel_y + 10):.2f} Z-2 F{travel_speed}  	; wipe forwards\n",
            f"G1 Y{(mandrel_y):.2f} Z0 F{wipe_speed}\n",
            f"G0 Y{(mandrel_y - 5):.2f} Z-1 F{wipe_speed}\n"
        ]
        wipe_gcode_bwrd = [
            f"G0 X{(self.wipe_x_pos + 5):.2f} Y{(mandrel_y - 10):.2f} Z-2 F{travel_speed}  	; wipe backwards\n",
            f"G0 Y{(mandrel_y):.2f} Z0 F{wipe_speed}  		; wipe nozzle\n",
            f"G0 Y{(mandrel_y + 5):.2f} Z-1 F{wipe_speed}\n"
        ]
        wipe_end_gcode = [
            f"G0 Z10 F{travel_speed}\n",
            f"G0 Y{first_y:.2f} F{travel_speed}	; move to start position\n",
            f"G0 X{first_x:.2f} F{travel_speed}\n\n"
        ]

        wipe_gcode = wipe_start_gcode
        for i in range(num_wipes):
            if i % 2 == 0:
                wipe_gcode += wipe_gcode_fwrd
            else:
                wipe_gcode += wipe_gcode_bwrd
        wipe_gcode += wipe_end_gcode

        wipe_index = layer_indices[0]+3
        printing_gcode[wipe_index:wipe_index] = wipe_gcode
        for i in range(1,len(layer_indices)): layer_indices[i] += len(wipe_gcode)

        return start_gcode, printing_gcode, end_gcode