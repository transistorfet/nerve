
$(document).ready(function()
{
    $('.tab').click(function() {
	$('#content > div').hide();
	$('#content-' + $(this).attr('data-content')).show();

	$('.tab').removeClass('selected');
	$(this).addClass('selected');
    }); 
});

