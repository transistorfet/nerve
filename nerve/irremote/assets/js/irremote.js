
$(document).ready(function ()
{

    $('.irremote-save').click(function ()
    {
        var codelist = [ ];

        $(this).parent().find('tr').each(function () {
            var code = $(this).find('input[name="code[]"]').val();
            var remote_name = $(this).find('select[name="remote_name[]"]').val();
            var button_name = $(this).find('input[name="button_name[]"]').val();

            if (button_name)
                codelist.push([ code, remote_name, button_name ]);
        });

        $.ajax({
            method: 'POST',
            url: '/irremote/save_names',
            contentType: 'application/json',
            data: JSON.stringify({ 'codelist' : codelist }),
            dataType: 'json',
            success: Nerve.display_response
        });
    });

    $('.irremote-clear').click(function ()
    {
        var table = $(this).parent().find('table');
        $.post('/irremote/clear_recent_codes', { }, function (response)
        {
            table.empty();
        });
    });

    $(document).on('click', '.irremote-codelist.recent .irremote-delete-row', function ()
    {
        $(this).closest('tr').remove();
    });

    $(document).on('click', '.irremote-codelist.remote .irremote-delete-row', function ()
    {
        var row = $(this).closest('tr');
        var code = row.find('input[name="code[]"]').val();
        var button_name = row.find('input[name="button_name[]"]').val();

        var dialog = new NerveDialog();
        dialog.confirm("Are you sure you want to delete the entry for code <b>" + code + ": " + button_name + "</b> and it's associated action?", function () {
            $.post('/irremote/delete_code', { 'code': code }, function (response) {
                if (dialog.display_response(response))
                    row.remove();
            });
            return false;
        });
    });

    $(document).on('click', '.irremote-send', function ()
    {
        $.post('/irremote/send_code', { code: $(this).attr('data-code') }, function (response)
        {
        });
    });

    // TODO this isn't being used.  The nerve-dialog-open button has all the info for creating the dialog
    $(document).on('click', '.irremote-edit', function ()
    {
        var dialog = new NerveDialog()
            .set_modal(true)
            .set_option('ok', false)
            .onsubmit(function ()
            {
                console.log("Good");
            })
            .open_url('/irremote/edit_action/' + $(this).attr('data-code'));
    });

    $('#irremote-view').click(function ()
    {
        var remote_name = $('#irremote-remote-name').val();
        $.post('/irremote/get_saved_codes', { 'remote_name': remote_name }, function (response)
        {
            $('#irremote-remote-view').show();
            $('#irremote-remote-view h5').html('Saved Codes for ' + (remote_name ? remote_name : 'unassigned'));
            $('table.irremote-codelist.remote').html(response);
        }, 'html');
    });

    $('#irremote-add-remote').on('nerve:dialog:success', null, function (event, response)
    {
        $('#irremote-remote-name').append($('<option value="' + response.remote_name + '" selected>' + response.remote_name + '</option>'))
    });

    $('#irremote-delete-remote').click(function ()
    {
        var remote = $('#irremote-remote-name').val();
        var dialog = new NerveDialog();

        dialog.set_modal(true);
        if (remote) {
            dialog.set_content("Are you sure you want to delete <b>" + remote + "</b> and all of it's associated buttons and actions?")
            dialog.open(function (that)
            {
                $.post('/irremote/remove_remote', { remote_name: remote }, function (response)
                {
                    if (dialog.display_response(response))
                        $('#irremote-remote-name [value="' + remote + '"]').remove()
                }, 'json');
            });
        }
        else {
            dialog.set_option('cancel', false);
            dialog.set_content("You can't delete 'unassigned'.");
            dialog.open();
        }
    });

    $('.irremote-toggle-program').click(function ()
    {
        $.post('/irremote/toggle_program_mode', { }, function (response)
        {
            if (response.program_mode == true)
                $('.irremote-toggle-program').addClass('nerve-highlight');
            else
                $('.irremote-toggle-program').removeClass('nerve-highlight');
        }, 'json');
    });

    var last_update = Date.now();
    var update_request = null;
    var update = new NerveTimedEvent(1000, function ()
    {
        update_request = $.post('/irremote/get_recent_codes', { 'last_update': last_update / 1000 }, function (response)
        {
            update_request = null;
            if (response.trim()) {
                last_update = Date.now();

                var rows = $(response);
                $('table.irremote-codelist.recent tr').each(function () {
                    var code = $(this).find('input[name="code[]"]').val();
                    var row = rows.find('input[name="code[]"][value="' + code + '"]').closest('tr');
                    if (code && row.length > 0) {
                        //row.html($(this).html());
                        //rows.after(this);
                        //$(this).detach();
                        //row.remove();
                        //rows.after(this);
                        row.remove();
                    }
                });

                $('table.irremote-codelist.recent').prepend(rows);
                //$('table.irremote-codelist.recent').html(response);
            }
            update.reset();
        }, 'html');
    });
    update.reset();

    $(window).on('beforeunload', function ()
    {
        if (update_request)
            update_request.abort();
    });
});

