
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
            $(div).html(response);
        }, 'html');
    });

    function _pack_values(form) {
        var postvars = { };

        $(form).find('.nerve-form-item input[type="text"],textarea').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        $(form).find('.nerve-form-item select').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            postvars[$(this).attr('name')] = $(this).is(':checked') ? true : false;
        });
        return postvars;
    }

    $('.add-create').click(function (e) {
        var form = $(this).parent().parent();

        var postvars = _pack_values(form);
        postvars['__dir__'] = $(this).attr('data-object');
        postvars['__type__'] = $(form).find('.add-select-type').val();

        $.post('/config/create', postvars, function (response) {
	    if (response.status == 'success') {
		$(form).find('#nerve-error').hide();
		$(form).find('#nerve-notice').hide();
                location.reload();
            }
	    else {
		$(form).find('#nerve-notice').hide();
		$(form).find('#nerve-error').html(response.message).show();
            }
        }, 'json');
    });

    $('.object-save').click(function (e) {
        e.preventDefault();

        var form = $(this).parent();

        var postvars = _pack_values(form);
        postvars['objectname'] = $(this).attr('data-object');

        $.post('/config/save', postvars, function (response) {
	    if (response.status == 'success') {
		$(form).find('#nerve-error').hide();
		$(form).find('#nerve-notice').html("Saved successfully").show();
            }
	    else {
		$(form).find('#nerve-notice').hide();
		$(form).find('#nerve-error').html(response.message).show();
            }
        }, 'json');
    });

    $('.object-delete').click(function (e) {
        e.preventDefault();

        var form = $(this).parent().parent();

        if (confirm("Are you sure you want to delete " + $(this).attr('data-object'))) {
            $.post('/config/delete', { 'objectname' : $(this).attr('data-object') }, function (response) {
                if (response.status == 'success') {
                    $(form).find('#nerve-error').hide();
                    $(form).find('#nerve-notice').hide();
                    location.reload();
                }
                else {
                    $(form).find('#nerve-notice').hide();
                    $(form).find('#nerve-error').html(response.message).show();
                }
            }, 'json');
        }
    });
});

 
