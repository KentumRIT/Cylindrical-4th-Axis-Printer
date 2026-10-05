folderpath = "D:\Github Stuff\Cylindrical-4th-Axis-Printer\Prusa Work\Adhesion Testing\Variance Testing\Shear Testing Data";

files = dir(fullfile(folderpath,'*.csv'));

% Find the max run and sample number from folder
max_run=0;
max_sample = 0;

for i = 1:length(files)
    tokens = regexp(files(i).name,...
        'Run\s+(\d+)\s+Sample\s+(\d+)', 'tokens');

    if ~isempty(tokens)
        run = str2double(tokens{1}{1});
        sample = str2double(tokens{1}{2});

        max_run = max(max_run,run);
        max_sample = max(max_sample,sample);
    end
end

% Read all properly named CSVs in folder (Run # Sample # format)
data = cell(max_run, max_sample);

for i = 1:length(files)
    tokens = regexp(files(i).name,...
        'Run\s+(\d+)\s+Sample\s+(\d+)', 'tokens');
    if ~isempty(tokens)
        run = str2double(tokens{1}{1});
        sample = str2double(tokens{1}{2});

        filename = fullfile(folderpath, files(i).name);
        data{run, sample} = readtable(filename,"VariableNamingRule","preserve");
    end
end

% Get max value for each data
force_max = zeros(max_run, max_sample);

for run = 1:max_run
    for sample = 1:max_sample
        force_max(run, sample) = max(data{run,sample}.("Load (lb)"));
    end
end

% Get average & std.dev of max force across all runs
avg_max_force = mean(force_max,1);
stddev_max_force = std(force_max,0,1);  % std.dev of a sample (N-1 weighting)



% Plot all samples and runs as time series
figure()
hold on

% One base color per sample
sample_colors = lines(max_sample);

for sample = 1:max_sample
    for run = 1:max_run

        t = data{run,sample}.Time;
        F = data{run,sample}.("Load (lb)");

        % Base color for this sample
        base_color = sample_colors(sample,:);

        % Vary brightness with run number
        brightness = 0.6 + 0.6 * (run - 1) / max(1, max_run - 1);

        line_color = 1 - brightness * (1 - base_color);
        line_color = max(0, min(1, line_color));

        plot(t, F, '-', ...
            'Color', line_color, ...
            'DisplayName', sprintf('Run %d, Mandrel %d', run, sample));
    end
end

xlabel('Time (s)')
ylabel('Force (lb)')
legend('Location', 'best')

% Plot max force as a bar graph
figure()
hold on

% Create one bar per sample
for sample = 1:max_sample
    bar(sample, avg_max_force(sample), ...
        'FaceColor', sample_colors(sample,:)*0.8, ...
        'EdgeColor', 'none');
end

% Add +/- 1 standard deviation error bars
errorbar(1:max_sample, avg_max_force, stddev_max_force, ...
    'w', 'LineStyle', 'none', 'LineWidth', 1.5, 'CapSize', 10);

% Labels
xticks(1:max_sample)
xticklabels(arrayfun(@(x) sprintf('Mandrel %d', x), ...
    1:max_sample, 'UniformOutput', false));

xlabel('Sample')
ylabel('Average Maximum Force (lb)')

box on