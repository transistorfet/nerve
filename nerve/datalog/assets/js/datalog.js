
function NerveGraph(element)
{
    var graphobj = this;

    var graphData;
    var canvas = $(element).find('#graph')[0];
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
    var cursorPosition = 0;

    var end_time = Math.ceil((new Date().getTime() / 1000) / 3600) * 3600;
    var domain = 86400;
    var rangeSteps = 5;
    var domainSteps = 6;

    var colours = [ "red", "blue", "green", "purple", "gray", "orange", "teal", "brown" ];

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
	this.draw_axes(c, data, 2);

	var legend_div = $(element).find('.legend');
	for (var i = 2; i < data.columns.length; i++) {
	    if ($(legend_div).find('#'+data.columns[i].name).prop('checked'))
		this.graph_line(c, data, i, colours[(i - 2) % colours.length]);
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
	c.moveTo(originX + ((data.data[0][1] - start_time) * domainRes), originY - ((data.data[0][column] ? (data.data[0][column] - base) : 0) * rangeRes));
	for (var i = 1; i < data.data.length && data.data[i][1] - start_time < domain; i++) {
	    c.lineTo(originX + ((data.data[i][1] - start_time) * domainRes), originY - ((data.data[i][column] ? (data.data[i][column] - base) : 0) * rangeRes));
	}
	c.stroke();
    }

    this.draw_cursor = function (c) {

	c.lineWidth = 1;
	c.strokeStyle = 'black';

        if (cursorPosition > 0) {
            c.beginPath();
            c.moveTo(cursorPosition, topMargin);
            c.lineTo(cursorPosition, bottomMargin);
            c.stroke();
        }
    }

    this.update_legend = function (data) {
	var legend_div = $(element).find('.legend');
	var cursor_date = new Date((end_time - domain + (domain * ((cursorPosition - leftMargin) / areaWidth))) * 1000);

	var checks = [ ];
	for (var i = 2; i < data.columns.length; i++)
	    checks[i - 2] = 'checked';
	$(legend_div).find('input').each(function (index, e) {
	    if (!e.checked)
		checks[index] = '';
	});
	legend_div.html('');

	for (var i = 2; i < data.columns.length; i++) {
	    $(legend_div).append(
                  '<div class="legend-item">'
                + '<input type="checkbox" id="' + data.columns[i].name + '" ' + checks[i - 2] + '/>'
                + '<span class="legend-colour" style="background: ' + colours[(i - 2) % colours.length] + ';"></span>'
                + '<label>' + data.columns[i].label + '</label>'
                + '<span class="legend-value">' + parseFloat(Math.round(this.get_value_at_cursor(data, i) * 100) / 100).toFixed(2) + '</span><span>' + data.columns[i].units + '</span>'
                + '</div>'
            );
	}
	$(legend_div).append('<div>Timestamp: &nbsp;&nbsp;&nbsp;&nbsp;' + cursor_date.toLocaleDateString() + '  ' + cursor_date.toLocaleTimeString() + '</div>');
    }

    this.get_value_at_cursor = function (data, column) {
        if (cursorPosition <= 0)
            return data.data[data.data.length - 1][column]

        var timestamp = end_time - domain + (domain * ((cursorPosition - leftMargin) / areaWidth));
	for (var i = 0; i < data.data.length; i++) {
            if (data.data[i][1] > timestamp)
                return data.data[i][column];
        }
        return data.data[data.data.length - 1][column]
    }

    canvas.addEventListener("mousedown", function (e) {
        var x = e.pageX - canvas.offsetLeft;
        var y = e.pageY - canvas.offsetTop;

        if (x > leftMargin && x < rightMargin && y > bottomMargin)
            cursorPosition = x;
        else
            cursorPosition = 0;

	var c = canvas.getContext('2d');
        graphobj.draw_graph(c, graphData);
    }, false);



    $(element).delegate('.legend', 'change', function () {
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
    this.update_timer = new NerveTimedEvent(60000, function ()
    {
        graphobj.update_graph();
    });
    this.update_timer.trigger_and_start_timer();

    $('#select-datalog').change(graphobj.update_graph);

    return graphobj;
}

$(document).ready(function () {
    new NerveGraph('.nerve-graph');
});

