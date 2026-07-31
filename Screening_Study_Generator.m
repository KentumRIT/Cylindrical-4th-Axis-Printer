samples_per_run = 5;            % number of samples to make with each combination of parameters

print_temp_range = [220,280];   % [low,high] (deg C)
print_temp_levels = 2;          % number of different temperatures to test

ironing_range = [0,2];          % number of first layer repeats
ironing_levels = 2;

print_speed_range = [20,80];    % print speed (mm/s)
print_speed_levels = 3;

z_offset_range = [0.05,0.8];    % first layer z offset (mm)
z_offset_levels = 3;

extr_width_range = [100,150];   % first layer extrusion width (%)
extr_width_levels = 2;

attch_width_range = [2,6];      % attachment region width (mm)
attch_width_levels = 2;