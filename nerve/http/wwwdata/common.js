
$(document).ready(function()
{

    $('.button').click(function () {
	var tag = $(this).attr('data-tag');
	$.post('/query', {'tag':tag}, function(response) {
	}, 'json');
    });

    $('.sendtext').click(function () {
	var textid = $(this).attr('data-text');
	var tag = $('#'+textid).attr('data-tag');
	var text = $('#'+textid).val();
	if (text) {
	    $.post('/query', {'tag':tag+' '+text}, function(response) {
	    }, 'json');
	}
    });

    //$('.slider').slider({ max: $(this).attr('data-max') });

    $('#slider').change(function () {
	var tag = $(this).attr('data-tag');
	$.post('/query', {'tag':tag}, function(response) {
	}, 'json');
    });

    $('.update').click(function() {
	var path = $(this).attr('data-path');
	var time = $(this).attr('data-time');
	var parent = $(this);
	$.post(path, {}, function(response) {
	    for (var key in response) {
		$('.' + key, parent).html(response[key])
	    }
	}, 'json');
    });

});

