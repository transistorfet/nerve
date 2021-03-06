
function NerveGraph(element)
{
    var graphobj = this;

    var graphData;
    var canvas = $(element).find('#graph')[0];
    if ($(window).width() < $(canvas).width())
        $(canvas).width($(window).width() - 20);
    var height = canvas.height;
    var width = canvas.width;
    var leftMargin = 50;
    var topMargin = 50;
    var rightMargin = width - 50;
    var bottomMargin = height - 50;
    var originY = bottomMargin;
    var originX = leftMargin;
    var areaHeight = height - 100;
    var areaWidth = width - 100;
    var cursorPositionX = 0;
    var cursorPositionY = 0;
    var selectedColumn = 1;

    var end_time = Math.ceil((new Date().getTime() / 1000) / 3600) * 3600;
    var domain = 86400;
    var rangeSteps = 5;
    var domainSteps = 6;

    var colours = [ "red", "blue", "green", "purple", "orchid", "royalblue", "darkorange", "teal", "brown" ];

    this.update_graph = function ()
    {
	var postvars = { };
	postvars.datalog = $('#select-datalog').val();
	postvars.start_time = end_time - domain;
	postvars.length = domain;

	//var query = $(element).attr('data-query');
	$.post('/datalog/get_data', postvars, function(response) {
	    var c = canvas.getContext('2d');
            graphData = response;
	    graphobj.draw_graph(c, response);
	}, 'json');
    }

    this.draw_graph = function (c, data)
    {
	c.clearRect(0, 0, width, height);
	this.update_legend(data);
	this.draw_axes(c, data, selectedColumn);

	var legend_div = $(element).find('.legend');
	for (var i = 1; i < data.columns.length; i++) {
	    if ($(legend_div).find('#'+data.columns[i].name).prop('checked'))
		this.graph_line(c, data, i, colours[(i - 1) % colours.length]);
	}

        this.draw_cursor(c);
    }

    this.draw_axes = function (c, data, column)
    {
	c.lineWidth = 1;
	c.strokeStyle = 'black';

	c.beginPath();
	c.moveTo(leftMargin, topMargin);
	c.lineTo(leftMargin, bottomMargin);
	c.lineTo(rightMargin, bottomMargin);
	c.stroke();

	c.font = "10px sans-serif";
	c.textAlign = "right";
	var step = (data.columns[column].max - data.columns[column].min) / 5;
	for (var i = 0; i <= rangeSteps; i++) {
	    var val = data.columns[column].min + (i * step);
	    var posY = originY - (i * (areaHeight / rangeSteps));

	    c.fillText(val + data.columns[column].units, originX - 5, posY + 3);

	    c.beginPath();
	    c.moveTo(originX, posY);
	    c.lineTo(originX - 4, posY);
	    c.stroke();

            if (val < data.columns[column].max) {
                for (var j = 0; j < 10; j++) {
                    var offsetY = posY - (j * ((areaHeight / rangeSteps) / 10));
                   
                    c.beginPath();
                    c.moveTo(originX, offsetY);
                    c.lineTo(originX - 4 + ((j % 2) * 2) - ( j == 5 ? 4 : 0 ), offsetY);
                    c.stroke();
                }
            }
	}

	c.font = "10px sans-serif";
	c.textAlign = "center";
	for (var i = 0; i <= domainSteps; i++) {
	    var date = new Date((end_time - domain + (i * (domain / domainSteps))) * 1000);
	    var posX = originX + (i * (areaWidth / domainSteps));

	    c.fillText(date.toLocaleTimeString(), posX, bottomMargin + 15);
	    c.fillText(date.toLocaleDateString(), posX, bottomMargin + 30);

	    c.beginPath();
	    c.moveTo(posX, originY);
	    c.lineTo(posX, originY + 4);
	    c.stroke();
	}
    }

    this.graph_line = function (c, data, column, colour)
    {
        var start_time = end_time - domain;
	var base = data.columns[column].min;
	var range = data.columns[column].max - data.columns[column].min;
	var rangeRes = areaHeight / range;
	var domainRes = areaWidth / domain;

	c.lineWidth = 1;
	c.strokeStyle = colour;

	c.beginPath();
	c.moveTo(originX + ((data.data[0][0] - start_time) * domainRes), originY - ((data.data[0][column] ? (data.data[0][column] - base) : 0) * rangeRes));
	for (var i = 1; i < data.data.length && data.data[i][0] - start_time < domain; i++) {
	    c.lineTo(originX + ((data.data[i][0] - start_time) * domainRes), originY - ((data.data[i][column] ? (data.data[i][column] - base) : 0) * rangeRes));
	}
	c.stroke();
    }

    this.draw_cursor = function (c) {

	c.lineWidth = 1;
	c.strokeStyle = 'black';

        if (cursorPositionX > 0) {
            c.beginPath();
            c.moveTo(cursorPositionX, topMargin);
            c.lineTo(cursorPositionX, bottomMargin);
            c.stroke();
        }

        if (cursorPositionY > 0) {
            c.beginPath();
            c.moveTo(leftMargin, cursorPositionY);
            c.lineTo(rightMargin, cursorPositionY);
            c.stroke();
        }
    }

    this.update_legend = function (data) {
	var legend_div = $(element).find('.legend');

	var checks = [ ];
	for (var i = 1; i < data.columns.length; i++)
	    checks[i - 1] = 'checked';
	$(legend_div).find('input').each(function (index, e) {
	    if (!e.checked)
		checks[index] = '';
	});
	legend_div.empty();

	for (var i = 1; i < data.columns.length; i++) {
	    $(legend_div).append(
                  '<div class="legend-item' + ( i == selectedColumn ? ' nerve-highlight-dim' : '' ) + '">'
                + '<input type="checkbox" id="' + data.columns[i].name + '" ' + checks[i - 1] + '/>'
                + '<span class="legend-colour" style="background: ' + colours[(i - 1) % colours.length] + ';"></span>'
                + '<label data-col="' + i + '">' + data.columns[i].label + '</label>'
                + '<span class="legend-value">' + parseFloat(Math.round(this.get_value_at_cursor(data, i) * 100) / 100).toFixed(2) + '</span><span>' + data.columns[i].units + '</span>'
                + '</div>'
            );
	}

        if (cursorPositionX <= 0)
            var cursor_date = new Date(data.data[data.data.length - 1][0] * 1000);
        else
            var cursor_date = new Date((end_time - domain + (domain * ((cursorPositionX - leftMargin) / areaWidth))) * 1000);
	$(legend_div).append('<div>Timestamp: &nbsp;&nbsp;&nbsp;&nbsp;' + cursor_date.toLocaleDateString() + '  ' + cursor_date.toLocaleTimeString() + '</div>');

        if (cursorPositionY > 0) {
            var value = ((originY - cursorPositionY) / areaHeight) * (data.columns[selectedColumn].max - data.columns[selectedColumn].min) + data.columns[selectedColumn].min;
            $(legend_div).append('<div>Cursor: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + parseFloat(value).toFixed(2) + ' ' + data.columns[selectedColumn].units + '</div>');
        }
    }

    this.get_value_at_cursor = function (data, column) {
        if (cursorPositionX <= 0)
            return data.data[data.data.length - 1][column]

        var timestamp = end_time - domain + (domain * ((cursorPositionX - leftMargin) / areaWidth));
	for (var i = 0; i < data.data.length; i++) {
            if (data.data[i][0] > timestamp)
                return data.data[i][column];
        }
        return data.data[data.data.length - 1][column]
    }

    this.handle_move_cursor = function (e) {
        var x = ((e.pageX ? e.pageX : e.changedTouches[0].pageX) - canvas.offsetLeft) * (canvas.width / $(canvas).width());
        var y = ((e.pageY ? e.pageY : e.changedTouches[0].pageY) - canvas.offsetTop) * (canvas.height / $(canvas).height());

        if (x > leftMargin && x < rightMargin)
            cursorPositionX = x;
        else
            cursorPositionX = 0;

        if (y > topMargin && y < bottomMargin)
            cursorPositionY = y;
        else
            cursorPositionY = 0;

	var c = canvas.getContext('2d');
        graphobj.draw_graph(c, graphData);
    };
    canvas.addEventListener("mousedown", this.handle_move_cursor, false);
    canvas.addEventListener("touchstart", this.handle_move_cursor, false);

    // Redraw if checkbox changes
    $(element).delegate('.legend', 'change', function () {
	var c = canvas.getContext('2d');
        graphobj.draw_graph(c, graphData);
    });

    // Select column and redraw
    $(element).find('.legend').on('click', '.legend-item label', function () {
        selectedColumn = parseInt($(this).attr('data-col'));
	var c = canvas.getContext('2d');
        graphobj.draw_graph(c, graphData);
    });


    // TODO add oldest and newest buttons

    new NerveClickCounter($(element).find('#older'), function (count) {
        for (var i = 0; i < count; i++)
	    end_time -= (domain / 4);
	graphobj.update_graph();
    });

    new NerveClickCounter($(element).find('#newer'), function (count) {
        for (var i = 0; i < count; i++)
	    end_time += (domain / 4);
	graphobj.update_graph();
    });

    new NerveClickCounter($(element).find('#zoomin'), function (count) {
        for (var i = 0; i < count; i++)
	    domain = domain / 1.25;
	graphobj.update_graph();
    });

    new NerveClickCounter($(element).find('#zoomout'), function (count) {
        for (var i = 0; i < count; i++)
            domain = domain * 1.25;
	graphobj.update_graph();
    });


    // update graph data periodically
    this.update_timer = new NerveTimedInterval(60000, function ()
    {
        graphobj.update_graph();
    });
    this.update_timer.trigger_and_reset();

    $('#select-datalog').change(graphobj.update_graph);

    return graphobj;
}

$(document).ready(function () {
    new NerveGraph('.nerve-graph');
});

