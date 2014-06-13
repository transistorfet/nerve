
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

    $('#getstatus').click(function () {
	$.post('/music/status', {}, function(response) {
	    $('#status_song').text(response.song)
	    $('#status_volume').text(response.volume)
	    $('#status_state').text(response.state)
	    $('#status_random').text(response.random)
	}, 'json');
    });

    $('.update').click(function() {
	var path = $(this).attr('data-path');
	var time = $(this).attr('data-time');
	$.post(path, {}, function(response) {
	    for (var key in response) {
		//var target = $(this).find('.' + key)
		var target = $('.' + key, this)
		if (target) {
		    $(target).html(response[key])
		}
	    }
	}, 'json');
    });

});

