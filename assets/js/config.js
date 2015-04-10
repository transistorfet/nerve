
$(document).ready(function ()
{
    $('.add').click(function (e) {
        $(this).next().show();
    });

    $('.add-cancel').click(function (e) {
        $(this).parent().parent().hide();
    });

    $('.add-select-type').change(function (e) {
        if (!$(this).val())
            return;

        var div = $(this).parent().parent().find('#add-settings');
        $.post('/config/defaults', { 'type' : $(this).val() }, function (response) {
            var fields = '';
            for (var setting in response) {
                fields += '<div class="nerve-form-item"><label>' + response[setting].propername + '</label><input type="text" name="' + response[setting].name + '" value="' + response[setting].default + '" /></div>';
            }
            $(div).html(fields);
        }, 'json');
    });

    $('.add-create').click(function (e) {
        var form = $(this).parent().parent();
        var postvars = { };

        postvars['__dir__'] = $(this).attr('data-object');
        postvars['__type__'] = $(form).find('.add-select-type').val();
        $(form).find('.nerve-form-item input[type="text"]').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            postvars[$(this).attr('name')] = $(this).is(':checked') ? true : false;
        });

        $.post('/config/create', postvars, function (response) {
	    if (response.status == 'success')
		$(form).find('#nerve-notice').html("Created successfully").show();
	    else
		$(form).find('#nerve-error').html(response.message).show();
        }, 'json');
    });

    $('.object-save').click(function (e) {
        e.preventDefault();

        var form = $(this).parent();
        var postvars = { };

        postvars['objectname'] = $(this).attr('data-object');

        $(form).find('.nerve-form-item input[type="text"]').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            postvars[$(this).attr('name')] = $(this).is(':checked') ? true : false;
        });

        $.post('/config/save', postvars, function (response) {
	    if (response.status == 'success')
		$(form).find('#nerve-notice').html("Saved successfully").show();
	    else
		$(form).find('#nerve-error').html(response.message).show();
        }, 'json');
    });
});

 
