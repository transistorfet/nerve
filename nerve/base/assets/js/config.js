
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




    function pack_form_data(form) {
        var data = { };

        $(form).find('.nerve-form-item input[type="text"],textarea').each(function () {
            add_form_value(postvars, $(this).attr('name'), $(this).val());
        });

        $(form).find('.nerve-form-item select').each(function () {
            add_form_value(postvars, $(this).attr('name'), $(this).val());
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            add_form_value(postvars, $(this).attr('name'), $(this).is(':checked') ? true : false);
        });

        return postvars;
    }

    function add_form_value(postvars, pathname, value) {
        var segments = pathname.substring(1).split('/');
        var leaf = segments.pop();
        var parent_data = postvars;
        for (var i = 0; i < segments.length; i++) {
            if (!parent_data[segments[i]]) {
                var next = (i + 1 < segments.length) ? segments[i + 1] : leaf;
                if (!isNaN(parseFloat(next)) && isFinite(next))
                    parent_data[segments[i]] = [ ];
                else
                    parent_data[segments[i]] = { };
            }
            parent_data = parent_data[segments[i]];
        }
        parent_data[leaf] = value;
    }

    $('.nerve-form-submit').click(function (e) {
        e.preventDefault();

        var form = $(this).parent().children('.nerve-form-tree');

        var postvars = pack_form_data(form);
        postvars['__name__'] = $(this).attr('data-object');

        $.ajax({
            method: 'POST',
            url: '/config/save',
            contentType: 'application/json',
            data: JSON.stringify(postvars),
            dataType: 'json',
            success: function (response) {
                if (response.status == 'success') {
                    $(form).find('#nerve-error').hide();
                    $(form).find('#nerve-notice').html("Saved successfully").show();
                }
                else {
                    $(form).find('#nerve-notice').hide();
                    $(form).find('#nerve-error').html(response.message).show();
                }
            }
        });
    });

    $('.nerve-config-edit').click(function (e) {
        //var div = $(this).parent().parent().find('#add-settings');
        var element = this;
        if ($(element).is(':visible')) {
            $.post('/config/edit', { 'path' : $(this).attr('name') }, function (response) {
                $(element).before(response);
                $(element).hide();
            }, 'html');
        }
    });
});

 
