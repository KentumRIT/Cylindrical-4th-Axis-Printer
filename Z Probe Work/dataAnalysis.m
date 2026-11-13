
% Load CSV Data and Plot Position vs. Signal

clear;
clc;
close all;

% Read CSV files
file1 = "30MinRepeatabilityTest-2026-11-11-11-59-05.csv";
file2 = "30MinTestNIDAQ Lights On 12.29pm.csv";
file3 = "30MinRepeatabilityTest-2026-11-11-16-12-23.csv";
file4 = "30MinTestNIDAQ Lights Off 4.42pm.csv";

[ta1,z1,ts1,v1] = extract_data(file1, file2, true);
[ta2,z2,ts2,v2] = extract_data(file3, file4, true);

% zero both positions about an arbitrary threshold voltage
threshold = 0.5;
idx = find(v1 < threshold, 1);
z1 = z1 - z1(idx);

idx = find(v2 < threshold, 1);
z2 = z2 - z2(idx);

get_best_fit(z1,v1,true);
get_best_fit(z2,v2,true);

% get rid of non-linear sensor regime & fit
voltage_bounds = [0.5 2.5];

valid = v1 < voltage_bounds(2) & v1 > voltage_bounds(1);
v1_lin = v1(valid);
z1_lin = z1(valid);

valid = v2 < voltage_bounds(2) & v2 > voltage_bounds(1);
v2_lin = v2(valid);
z2_lin = z2(valid);

% plot best fits
p1 = get_best_fit(z1_lin, v1_lin, true);
p2 = get_best_fit(z2_lin, v2_lin, true);

% plot std dev
get_terms_by_position(z1_lin, v1_lin, 0.01, true);
get_terms_by_position(z2_lin, v2_lin, 0.01, true);

% plot against each other
x_fit = linspace(min(min(v1_lin),min(v2_lin)), max(max(v1_lin),max(v2_lin)), 1000);
y_fit1 = polyval(p1, x_fit);
y_fit2 = polyval(p2, x_fit);

figure;
hold on
plot(x_fit,y_fit1)
plot(x_fit,y_fit2)
title('Light vs Dark')
xlabel('Sensor Signal (V)')
ylabel('Estimated Position (mm)')
legend('light room','dark room')
hold off

function [admet_time,position,sensor_time,voltage] = extract_data(admet_file, sensor_file, plot_results)

    data1 = readtable(admet_file,'VariableNamingRule', 'preserve');
    data2 = readtable(sensor_file,'VariableNamingRule', 'preserve');

    admet_time = data1.("Time");
    position_in = data1.("Position (in)");
    position = position_in * 25.4;

    sensor_time = data2.("Time");
    voltage = data2.("HY810H Signal (V)");

    % plot results
    if ~plot_results
        return;
    end
    figure;

    yyaxis left
    plot(admet_time, position, 'b-', 'LineWidth', 1.5);
    ylabel('Position (mm)');
    ax = gca;
    ax.YColor = 'b';
    
    yyaxis right
    plot(sensor_time, voltage, 'r-', 'LineWidth', 1.5);
    ylabel('Signal (V)');
    ax.YColor = 'r';
    
    xlabel('Time (s)');
    title('Sensor Signal Vs Position');
    
    grid on;
end

function p = get_best_fit(position, voltage, plot_results)
    % ensure both vectors are same size
    position = position(1:min(length(position),length(voltage)));
    voltage = voltage(1:min(length(position),length(voltage)));

    % get best fit
    p = polyfit(voltage, position, 3);
    
    x_fit = linspace(min(voltage), max(voltage), 1000);
    y_fit = polyval(p, x_fit);
    
    % plot results
    if ~plot_results
        return;
    end
    figure;
    hold on
    plot(voltage,position)
    plot(x_fit,y_fit,'--')
    title('Sensor Response')
    xlabel('Sensor Signal (V)')
    ylabel('Position (mm)')
    legend('raw data','best fit')
    hold off
end

function [voltage_std, voltage_mean, position_std, binned_position] = get_terms_by_position(position, voltage, bin_width, plot_results)
    % ensure both vectors are same size
    position = position(1:min(length(position),length(voltage)));
    voltage = voltage(1:min(length(position),length(voltage)));

    % assign measurements to bins
    bin_edges = min(position):bin_width:max(position)+bin_width;
    bin_indices = discretize(position, bin_edges);

    % get rid of empty bins
    valid = ~isnan(bin_indices);
    bin_indices = bin_indices(valid);
    voltage = voltage(valid);

    % sort measurements by bin and separate bins into cells
    [sorted_bins, sorted_idxs] = sort(bin_indices);
    sorted_signal = voltage(sorted_idxs);
    binned_voltage = accumarray(sorted_bins, sorted_signal, ...
    [length(bin_edges) - 1, 1], @(x) {x}, {[]});

    % throw out bins with insufficient size
    count = cellfun(@length, binned_voltage);
    valid = count > 4;
    binned_voltage = binned_voltage(valid);

    binned_position = bin_edges(1:end-1) + bin_width/2;
    binned_position = binned_position(valid);

    % calculate values for voltage
    voltage_std = cellfun(@std, binned_voltage);
    voltage_mean = cellfun(@mean, binned_voltage);
    
    % calculate std dev in position from std dev in voltage
    % sigma_z = sigma_V / |dV/dz|
    p = polyfit(position, voltage, 3);
    dVdz = 3*p(1)*binned_position.^2 + ...
            2*p(2)*binned_position + p(3);
    position_std = voltage_std ./ abs(dVdz).';
    

    % plot results
    if ~plot_results
        return;
    end
    figure;
    
    yyaxis left
    plot(binned_position,2*voltage_std);
    ylabel('Sensor Deviation (V)')
    
    yyaxis right
    plot(binned_position, 2*position_std);
    ylabel('Positional Deviation (mm)');
    
    xlabel('Position (mm)')
    title('Cycle-to-Cycle Deviation (2σ)')
end




