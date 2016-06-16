
$(document).ready(function ()
{
    var update_request = null;
    var update = new NerveTimedEvent(5000, function ()
    {
        update_request = $.post('/notify/list', { }, function (response)
        {
            update_request = null;
            $('#nerve-notifications-list').html(response);
            update.reset();
        }, 'html');
    });
    update.trigger();

    $(window).on('beforeunload', function ()
    {
        if (update_request)
            update_request.abort();
    });

    $('.notify-acknowledge').click(function () {
        var postvars = { };
        postvars['nids[]'] = [ ];

        $("input[name='nids[]']:checked").each(function () {
            postvars['nids[]'].push($(this).val());
        });

        $.post('/notify/acknowledge', postvars, function (response) {
            update.trigger();
        }, 'json');
    });

    $(document).on('change', '.notify-select-all', function () {
        var value = $(this).prop('checked');
        $("input[name='nids[]']").prop('checked', value).change();
    });

    $('.notify-acknowledge-all').click(function () {
        $.post('/notify/acknowledge_all', function (response) {
            update.trigger();
        }, 'json');
    });

    $('.notify-clear').click(function () {
        var postvars = { };
        postvars['nids[]'] = [ ];

        $("input[name='nids[]']:checked").each(function () {
            postvars['nids[]'].push($(this).val());
        });

        $.post('/notify/clear', postvars, function (response) {
            update.trigger();
        }, 'json');
    });

    $('.notify-clear-all').click(function () {
        $.post('/notify/clear_all', function (response) {
            update.trigger();
        }, 'json');
    });
});

