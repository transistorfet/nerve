
function nerve_query(element) {
    var query = $(element).attr('data-query');
    $.post('/query/'+query, {}, function(response) {
	$(element).html(response)
    }, 'json');
}

function nerve_query_block(element) {
    var query = $(element).attr('data-query');
    var parent = $(element);
    $.post('/query/'+query, {}, function(response) {
	for (var key in response) {
	    $('.' + key, parent).html(response[key])
	}
    }, 'json');
}

$(document).ready(function()
{

    $('.nerve-button').click(function () {
	var query = $(this).attr('data-query');
	$.post('/query', {'queries[]':[query]}, function(response) {
	}, 'json');
    });

    $('.nerve-input-submit').click(function () {
	var textid = $(this).attr('data-id');
	var query = $('#'+textid).attr('data-query');
	var text = $('#'+textid).val();
	if (text) {
	    $.post('/query', {'queries[]':query+' '+text}, function(response) {
	    }, 'json');
	}
    });

    $('.nerve-query').each(function(element) {
	var time = $(this).attr('data-time');
	nerve_query(this);
	setInterval(nerve_query, time, this);
    });

    $('.nerve-query-block').each(function(element) {
	var time = $(this).attr('data-time');
	nerve_query_block(this);
	setInterval(nerve_query_block, time, this);
    });

});


