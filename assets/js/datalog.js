
function NerveGraph(element)
{
    var graphobj = this;
    var datalog_name = $('#select-datalog').val();

    var canvas = $(element).find('#graph')[0];
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

    var end_time = Math.ceil((new Date().getTime() / 1000) / 3600) * 3600;
    var domain = 86400;
    var rangeSteps = 5;
    var domainSteps = 6;

    var colours = [ "red", "blue", "green", "purple", "yellow", "brown", "orange" ];

    this.update_graph = function ()
    {
	var postvars = { };
	postvars.datalog = datalog_name;
	postvars.start_time = end_time - domain;
	postvars.length = domain;

	//var query = $(element).attr('data-query');
	$.post('/datalog/get_data', postvars, function(response) {
	    graphobj.draw_graph(response);
	}, 'json');
    }

    this.draw_graph = function (data)
    {
	var c = canvas.getContext('2d');

	c.clearRect(0, 0, width, height);
	this.update_legend(data);
	this.draw_axes(c, data, 2);

	var legend_div = $(element).find('.legend');
	for (var i = 2; i < data.columns.length; i++) {
	    if ($(legend_div).find('#'+data.columns[i].name).prop('checked'))
		this.graph_line(c, data, i, colours[i - 2]);
	}
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
                    c.lineTo(originX - 4, offsetY);
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
	c.moveTo(originX + ((data.data[0][1] - start_time) * domainRes), originY - (data.data[0][column] * rangeRes));
	for (var i = 1; i < data.data.length && data.data[i][1] - start_time < domain; i++) {
	    c.lineTo(originX + ((data.data[i][1] - start_time) * domainRes), originY - (data.data[i][column] * rangeRes));
	}
	c.stroke();
    }

    this.update_legend = function (data) {
	var legend_div = $(element).find('.legend');

	var checks = [ ];
	for (var i = 2; i < data.columns.length; i++)
	    checks[i - 2] = 'checked';
	$(legend_div).find('input').each(function (index, e) {
	    if (!e.checked)
		checks[index] = '';
	});
	legend_div.html('');

	for (var i = 2; i < data.columns.length; i++) {
	    $(legend_div).append('<div><input type="checkbox" id="' + data.columns[i].name + '" ' + checks[i - 2] + '/><span class=".nerve-graph legend-colour" style="background: ' + colours[i - 2] + ';"></span><label>' + data.columns[i].label + '</label></div>');
	}
    }

    $(element).delegate('.legend', 'change', function () {
	graphobj.update_graph();
    });

    $(element).find('#oldest').click(function () {
	
    });

    $(element).find('#older').click(function () {
	end_time -= (domain / 4);
	graphobj.update_graph();
    });

    $(element).find('#newer').click(function () {
	end_time += (domain / 4);
	graphobj.update_graph();
    });

    $(element).find('#zoomin').click(function () {
	domain = domain / 1.25;
	graphobj.update_graph();
    });

    $(element).find('#zoomout').click(function () {
        domain = domain * 1.25;
	graphobj.update_graph();
    });

    this.interval = setInterval(this.update_graph, 60000)
    this.update_graph();
}

$(document).ready(function () {
    var graph = NerveGraph('.nerve-graph');

    $('#select-datalog').change(function (e) {
	graph.datalog_name = e.val();
	graph.update_graph();
    });
});

