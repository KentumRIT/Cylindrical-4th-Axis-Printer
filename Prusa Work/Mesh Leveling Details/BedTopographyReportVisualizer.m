function [X,Y,Z] = extract_mesh(filename)
    lines = readlines(filename);

    Z = [];
    for i = 1:length(lines)
        line = lines(i);
        nums = str2double(regexp(line, '[-+]\d*\.?\d+', 'match'));
        Z = [Z;nums];
    end
    
    num_rows = size(Z,1);
    num_cols = size(Z,2);
    
    point_spacing = 360/35;
    x_points = point_spacing * (4 + 3 * (0:(num_cols-1)) );
    y_points = point_spacing * (1 + 3*2 * (0:(num_rows-1)) );
    y_points = flip(y_points);

    [X,Y] = meshgrid(x_points,y_points);

end

filename1 = "7 Bed Topography Report Facing Up (fussed with things, new reference).txt";
filename2 = "8 Bed Topography Report Facing Up (loosened and tightened set screws).txt";
            
%filename2 = "Bed Topography Report Facing Up 2.txt";

[X1,Y1,Z1] = extract_mesh(filename1);
[X2,Y2,Z2] = extract_mesh(filename2);

scaling_factor = 100;

figure('Name','Mandrel Up')
surf(X1,Y1,Z1,'FaceAlpha',0.25)

daspect([1 1 1/scaling_factor])
axis vis3d
camproj('orthographic')

xlabel('x (mm)')
ylabel('y (mm)')
zlabel(sprintf('z (mm) %dX scale',scaling_factor))

rotate3d on

figure('Name','Mandrel Down')
surf(X2,Y2,Z2,'FaceAlpha',0.25)

daspect([1 1 1/scaling_factor])
axis vis3d
camproj('orthographic')

xlabel('x (mm)')
ylabel('y (mm)')
zlabel(sprintf('z (mm) %dX scale',scaling_factor))

rotate3d on

figure('Name','Mesh Deformation Delta')
surf(X1,Y1,Z1-Z2,'FaceAlpha',0.25)

daspect([1 1 1/scaling_factor])
axis vis3d
camproj('orthographic')

xlabel('x (mm)')
ylabel('y (mm)')
zlabel(sprintf('z (mm) %dX scale',scaling_factor))

rotate3d on