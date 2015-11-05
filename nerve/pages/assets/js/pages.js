
$(document).ready(function()
{

    $('#block-editor-save').click(function ()
    {
        $('#nerve-notice').hide();
        $('#nerve-notice').hide();

        var postvars = { };
        postvars['originalname'] = $('#block-original-name').val();
        postvars['blockname'] = $('#block-editor-name').val();
        postvars['blocktext'] = $('#block-editor-text').val();
        $.post('/pages/saveblock', postvars, function (response) {
            if (response.status == "success") {
                $('#nerve-notice').html(response.message).show();
                $('#block-original-name').val(postvars['blockname']);
            }
            else
                $('#nerve-error').html(response.message).show();
        }, 'json');
    });


    $('.page-blocks').delegate('input', 'change', function ()
    {
        var parent = $(this).parent();
        var last = $(parent).find('input').last().clone();

        $(parent).find('input').each(function () {
            if ($(this).val() == '')
                $(parent).remove(this);
        });
        $(parent).appendTo(last);
    });

    /*
    $('#page-editor-save').click(function ()
    {
        $('#nerve-notice').hide();
        $('#nerve-notice').hide();

        var postvars = { };
        postvars['originalname'] = $('#page-original-name').val();
        postvars['pagename'] = $('#page-editor-name').val();

        $('.page-section').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        $.post('/pages/savepage', postvars, function (response) {
            if (response.status == "success") {
                $('#nerve-notice').html(response.message).show();
                $('#page-original-name').val(postvars['pagename']);
            }
            else
                $('#nerve-error').html(response.message).show();
        }, 'json');
    });

    $('#page-editor-view').click(function ()
    {
        window.location = '/pages/' + $('#page-editor-name').val();
    });
    */

    $('#page-editor .nerve-form-submit').click(function ()
    {
        var pagename = $('input[name="pagename"]').val();
        $('input[name="originalname"]').val(pagename);
        //window.location = '/pages/editpage/' + pagename;
        window.history.replaceState({ }, "", '/pages/editpage/' + pagename);
    });

    $('.delete-block').click(function ()
    {
        $('#nerve-notice').hide();
        $('#nerve-notice').hide();

        var blockname = $(this).attr('data-target');

        if (confirm("Are you sure you want to delete block " + blockname)) {
            $.post('/pages/deleteblock', { 'name': blockname }, function (response) {
                if (response.status == "success") {
                    $('.block-item[data-name="'+blockname+'"]').remove();
                    $('#nerve-notice').html(response.message).show();
                }
                else
                    $('#nerve-error').html(response.message).show();
            }, 'json');
        }
    });

    $('.delete-page').click(function ()
    {
        $('#nerve-notice').hide();
        $('#nerve-notice').hide();

        var pagename = $(this).attr('data-target');

        if (confirm("Are you sure you want to delete page " + pagename)) {
            $.post('/pages/deletepage', { 'name': pagename }, function (response) {
                if (response.status == "success") {
                    $('.page-item[data-name="'+pagename+'"]').remove();
                    $('#nerve-notice').html(response.message).show();
                }
                else
                    $('#nerve-error').html(response.message).show();
            }, 'json');
        }
    });
});



