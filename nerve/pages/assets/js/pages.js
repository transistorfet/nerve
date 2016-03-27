
$(document).ready(function()
{

    $('#block-editor-save').click(function ()
    {
        var postvars = { };
        postvars['originalname'] = $('#block-original-name').val();
        postvars['blockname'] = $('#block-editor-name').val();
        postvars['blocktext'] = $('#block-editor-text').val();
        $.post('/pages/saveblock', postvars, function (response) {
            if (Nerve.display_response(response)) {
                $('#block-original-name').val(postvars['blockname']);
            }
        }, 'json');
    });

    $('#page-editor').on('nerve:form:success', null, function ()
    {
        var pagename = $('input[name="pagename"]').val();
        $('input[name="originalname"]').val(pagename);
        //window.location = '/pages/editpage/' + pagename;
        window.history.replaceState({ }, "", '/pages/editpage/' + pagename);
    });

    /*
    $('#page-editor-save').click(function ()
    {
        var postvars = { };
        postvars['originalname'] = $('#page-original-name').val();
        postvars['pagename'] = $('#page-editor-name').val();

        $('.page-section').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        $.post('/pages/savepage', postvars, function (response) {
            if (response.notice) {
                Nerve.set_notice(response.notice);
                $('#page-original-name').val(postvars['pagename']);
            }
            else if (response.error)
                Nerve.set_error(response.error);
        }, 'json');
    });

    $('#page-editor-view').click(function ()
    {
        window.location = '/pages/' + $('#page-editor-name').val();
    });
    */

    /*
    $('#page-editor .nerve-form-submit').click(function ()
    {
        var pagename = $('input[name="pagename"]').val();
        $('input[name="originalname"]').val(pagename);
        //window.location = '/pages/editpage/' + pagename;
        window.history.replaceState({ }, "", '/pages/editpage/' + pagename);
    });
    */


    $('.delete-block').click(function ()
    {
        var blockname = $(this).attr('data-name');

        if (confirm("Are you sure you want to delete block " + blockname)) {
            $.post('/pages/deleteblock', { 'name': blockname }, function (response) {
                if (Nerve.display_response(response)) {
                    $('.block-item[data-name="'+blockname+'"]').remove();
                }
            }, 'json');
        }
    });

    $('.delete-page').click(function ()
    {
        var pagename = $(this).attr('data-name');

        if (confirm("Are you sure you want to delete page " + pagename)) {
            $.post('/pages/deletepage', { 'name': pagename }, function (response) {
                if (Nerve.display_response(response)) {
                    $('.page-item[data-name="'+pagename+'"]').remove();
                }
            }, 'json');
        }
    });
});



