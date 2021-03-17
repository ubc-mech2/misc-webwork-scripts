function plot3DVectors(vectors, names, colors)

    % Plots 3D vectors originating from origin
    % param: vectors - n x 3 matrix with n 3D vectors to plot
    %                  (vectors are rows in matrix)
    %        names   - 1 x n row vector with names for each plotted vector
    %                  (vector arrow is written on each name)
    %        colors  - 1 x n row vector with colors for each vector
    
    function plot3DVector(x, y, z, c, n, size)
        name = strcat('$\overrightarrow{', n, '}$');

        offset = 0.5;
        if z < 0
            offset = -0.5;
        end

        mArrow3([0, 0, 0], [x, y, z], 'color', c, 'stemWidth', size / 300, 'tipWidth', size / 50);
        text(x, y, z + offset, name, 'Color', c, 'Interpreter', 'latex', 'fontSize', 14);

        xLine1 = line([0, x], [0, 0], [0, 0], 'Color', c);
        xLine2 = line([0, x], [y, y], [0, 0], 'Color', c);
        xLine3 = line([0, x], [0, 0], [z, z], 'Color', c);
        xLine4 = line([0, x], [y, y], [z, z], 'Color', c);

        yLine1 = line([0, 0], [0, y], [0, 0], 'Color', c);
        yLine2 = line([x, x], [0, y], [0, 0], 'Color', c);
        yLine3 = line([0, 0], [0, y], [z, z], 'Color', c);
        yLine4 = line([x, x], [0, y], [z, z], 'Color', c);

        zLine1 = line([0, 0], [0, 0], [0, z], 'Color', c);
        zLine2 = line([x, x], [0, 0], [0, z], 'Color', c);
        zLine3 = line([0, 0], [y, y], [0, z], 'Color', c);
        zLine4 = line([x, x], [y, y], [0, z], 'Color', c);

        xLine1.LineStyle = '--';
        xLine2.LineStyle = '--';
        xLine3.LineStyle = '--';
        xLine4.LineStyle = '--';

        yLine1.LineStyle = '--';
        yLine2.LineStyle = '--';
        yLine3.LineStyle = '--';
        yLine4.LineStyle = '--';

        zLine1.LineStyle = '--';
        zLine2.LineStyle = '--';
        zLine3.LineStyle = '--';
        zLine4.LineStyle = '--';
    end

    numRows = height(vectors);
    numCols = width(vectors);

    minNum = -4;
    maxNum = 4;
    for i = 1:numRows
        for j = 1:numCols
            temp = vectors(i, j);
            if temp < minNum
                minNum = temp;
            elseif temp > maxNum
                maxNum = temp;
            end
        end
    end

    if minNum * (-1) > maxNum
        maxNum = minNum * (-1);
    end
    if maxNum * (-1) < minNum
        minNum = maxNum * (-1);
    end

    xTicks = zeros(1, numRows);
    yTicks = zeros(1, numRows);
    zTicks = zeros(1, numRows);

    for i = 1:numRows
        if ~ismember(vectors(i, 1), xTicks)
            xTicks(1, i) = vectors(i, 1);
        end
        if ~ismember(vectors(i, 2), yTicks)
            yTicks(1, i) = vectors(i, 2);
        end
        if ~ismember(vectors(i, 3), zTicks)
            zTicks(1, i) = vectors(i, 3);
        end
    end

    if numCols ~= 3
        error('3D vectors only!');
    end

    for i = 1:numRows
        plot3DVector(vectors(i, 1), vectors(i, 2), vectors(i, 3), colors(i), names(i), maxNum);
        hold on
    end
    hold off

    set(gca, 'Projection','perspective');
    ax = gca;
    ax.DataAspectRatio = [1 1 1];
    ax.XLim = [minNum - 1, maxNum + 1];
    ax.YLim = [minNum - 1, maxNum + 1];
    ax.ZLim = [minNum - 1, maxNum + 1];
    ax.XAxisLocation = 'origin';
    ax.YAxisLocation = 'origin';
    ax.XDir = 'reverse';
    ax.YDir = 'reverse';
    ax.XAxis.FirstCrossoverValue = 0;
    ax.XAxis.SecondCrossoverValue = 0;
    ax.YAxis.FirstCrossoverValue = 0;
    ax.YAxis.SecondCrossoverValue = 0;
    ax.ZAxis.FirstCrossoverValue = 0;
    ax.ZAxis.SecondCrossoverValue = 0;
    ax.XAxis.MinorTick = 'on';
    ax.XAxis.MinorTickValues = minNum:maxNum;
    ax.YAxis.MinorTick = 'on';
    ax.YAxis.MinorTickValues = minNum:maxNum;
    ax.ZAxis.MinorTick = 'on';
    ax.ZAxis.MinorTickValues = minNum:maxNum;

    mArrow3([minNum - 1, 0, 0], [maxNum + 1, 0, 0], 'stemWidth', maxNum / 250, 'tipWidth', maxNum / 100);
    mArrow3([0, minNum - 1, 0], [0, maxNum + 1, 0], 'stemWidth', maxNum / 250, 'tipWidth', maxNum / 100);
    mArrow3([0, 0, minNum - 1], [0, 0, maxNum + 1], 'stemWidth', maxNum / 250, 'tipWidth', maxNum / 100);

    text(maxNum + 1.5, 0, 0, 'X');
    text(0, maxNum + 1.5, 0, 'Y');
    text(0, 0, maxNum + 1.5, 'Z');

    xticks(sort(xTicks));
    yticks(sort(yTicks));
    zticks(sort(zTicks));

    view(3)
end