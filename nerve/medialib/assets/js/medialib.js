
function MediaLibPlaylist(element)
{
    var that = this;

    that.update = function ()
    {
        $.post('/medialib/get_playlist', { 'playlist' : $('#select-playlist').val() }, function (response) {
            $('#medialib-playlist-contents').html(response);
        }, 'html');
    }

    that.remove_selected = function ()
    {
        var postvars = { 'playlist' : $('#select-playlist').val(), 'urls' : [ ] };
        $('input[name="urls[]"]:checked').each(function () {
            postvars['urls'].push($(this).val());
        });

        $.post('/medialib/remove_urls', postvars, function (response) {
            Nerve.display_response(response);
            that.update();
        }, 'json');
    }

    /*
    that.create_playlist = function ()
    {
        var playlist = $('#pl_name').val();
        $.post('/medialib/create_playlist', { 'playlist' : playlist }, function (response) {
            $('#pl_name').val('');
            if (response.error)
                Nerve.set_error(response.error);
            else if (response.notice) {
                Nerve.set_notice(response.notice);
                $('#select-playlist').append('<option value="'+playlist+'">'+playlist+'</option>');
                $('#select-playlist').val(playlist);
                that.update();
            }
        }, 'json');
    }
    */

    $('#medialib-create-playlist').on('nerve:dialog:success', null, function (event, result, response) {
        $('#select-playlist').append('<option value="'+result.playlist+'" selected>'+result.playlist+'</option>');
        that.update();
    });

    that.delete_playlist = function ()
    {
        var playlist = $('#select-playlist').val();
        //new NerveDialog({ content: "Are you sure you want to delete the playlist: " + playlist }).open(function () {
        if (playlist == 'default') {
            new NerveDialog({ cancel: false }).confirm("You cannot delete the default playlist");
        }
        else {
            new NerveDialog().confirm("Are you sure you want to delete the playlist: <b>" + playlist + "</b>", function (dialog) {
                $.post('/medialib/delete_playlist', { 'playlist' : playlist }, function (response) {
                    if (dialog.display_response(response)) {
                        $('#select-playlist option[value="'+playlist+'"]').remove();
                        that.update();
                    }
                });
            });
        }
    }

    that.sort_playlist = function ()
    {
        $.post('/medialib/sort_playlist', { 'playlist' : $('#select-playlist').val() }, that.update, 'html');
    }

    that.shuffle_playlist = function ()
    {
        $.post('/medialib/shuffle_playlist', { 'playlist' : $('#select-playlist').val() }, that.update, 'html');
    }

    that.load_playlist = function ()
    {
        $.post('/query/player/load_playlist', { 'url' : $('#select-playlist').val() }, function (response) { }, 'json');
    }

    $('#select-playlist').change(that.update);
    that.update();

    $('.pl_remove').click(that.remove_selected);
    $('.pl_sort').click(that.sort_playlist);
    $('.pl_shuffle').click(that.shuffle_playlist);
    //$('.pl_create').click(that.create_playlist);
    $('.pl_delete').click(that.delete_playlist);
    $('.pl_load').click(that.load_playlist);

    $('.pl_current').click(function() {
        $('html, body').animate({ scrollTop: $('.nerve-highlight').offset().top - 100 }, 500);
    });

    $('#medialib-playlist-contents').on('click', 'td:last-child', function (event) {
        event.stopPropagation();
        var element = this;
        $.post('/query/player/goto', { 'pos' : $(element).parent().parent().children().index($(element).parent()) }, function (response) {
            $('.medialib-list tr.nerve-highlight').removeClass('nerve-highlight');
            $(element).parent().addClass('nerve-highlight');
        }, 'json');
    });

    that.query_songname = new NerveTimedInterval($('.medialib-query-songname').attr('data-time'), function ()
    {
        var queries = [
            $('.medialib-query-songname').attr('data-query'),
            'player/get_position'
        ];

        Nerve.query(queries, function (response) {
            $('.medialib-query-songname').html(response[0]);
            $('#medialib-playlist-contents tr').removeClass('nerve-highlight');
            $('#medialib-playlist-contents tr').eq(response[1]).addClass('nerve-highlight');
        });
    });
    that.query_songname.trigger_and_reset();
    $('.medialib-query-songname').click(that.query_songname.trigger);

    $('.medialib-button-next').click(function () {
        $.post('/query/'+$(this).attr('data-query'), {}, function(response) {
            var element = $('.medialib-list tr.nerve-highlight');
            $(element).removeClass('nerve-highlight');
            if ($(element).next().length)
                $(element).next().addClass('nerve-highlight');
            that.query_songname.reset();
        }, 'json');
    });

    $('.medialib-button-previous').click(function () {
        $.post('/query/'+$(this).attr('data-query'), {}, function(response) {
            var element = $('.medialib-list tr.nerve-highlight');
            $(element).removeClass('nerve-highlight');
            if ($(element).prev().length)
                $(element).prev().addClass('nerve-highlight');
            that.query_songname.reset();
        }, 'json');
    });


    return that;
}

function MediaLibSearch(element)
{
    var that = this;

    /*
    that.search = function ()
    {
        var postvars = { };

        postvars['mode'] = $(element).find('#mode').val();
        postvars['order'] = $(element).find('#order').val();
        postvars['offset'] = $(element).find('#offset').val();
        postvars['limit'] = $(element).find('#limit').val();
        postvars['search'] = $(element).find('#search').val();
        postvars['recent'] = $(element).find('#recent').val();
        postvars['media_type'] = $(element).find('#media_type').val();

        $.post('/medialib/get_search_results', postvars, function (response) {
            $(element).find('#medialib-search-results').html(response);
            $(element).find('#medialib-search-table').show();
        }, 'html');
    }

    that.expand_artist = function (artist)
    {
        var postvars = { };
        postvars['mode'] = 'title';
        postvars['order'] = 'artist';
        postvars['search'] = artist;

        $.post("/medialib/get_search_results", postvars, function(response) {
            $('#medialib-search-results').html(response);
        }, 'html');
    }
    */

    that.add_media_items = function (operation, options)
    {
        var postvars = options || { };
        postvars['operation'] = operation;
        postvars['media[]'] = [ ];

        $("input[name='media[]']:checked").each(function () {
            postvars['media[]'].push($(this).val());
        });

        $.post('/medialib/add_media_items', postvars, function (response) {
            if (response.error)
                Nerve.set_error(response.error);
            else {
                Nerve.set_notice(response.notice);
                $("input[name='media[]']:checked").each(function () {
                    $(this).prop('checked', false).change();
                });
            }
        }, 'json');
    }

    /*
    $(element).find('#pl_search').click(function () {
        Nerve.clear_notices();
        that.search();
    });
    if (window.location.href.indexOf("?") > 0)
        that.search();
    */


    $(element).find('.pl_enqueue').click(function () {
        that.add_media_items('enqueue', { 'playlist': $('#select-playlist').val() });
    });

    $(element).find('.pl_replace').click(function () {
        if (confirm("Are you sure you want to replace everything on playlist " + $('#select-playlist').val()))
            that.add_media_items('replace', { 'playlist': $('#select-playlist').val() });
    });

    $(element).find('.pl_playnow').click(function () {
        that.add_media_items('playnow', { 'playlist': $('#select-playlist').val() });
    });

    $(element).find('.pl_addtags').click(function () {
        var postvars = { };
        postvars['tags'] = $('#medialib-add-tags').val();
        postvars['media[]'] = [ ];

        $("input[name='media[]']:checked").each(function () {
            postvars['media[]'].push($(this).val());
        });

        $.post('/medialib/modify_tags', postvars, function (response) {
            if (response.error)
                Nerve.set_error(response.error);
            else if (response.notice) {
                Nerve.set_notice(response.notice);
                $("input[name='media[]']:checked").each(function () {
                    $(this).prop('checked', false).change();
                });
                $('#medialib-add-tags').val('');
            }
        }, 'json');
    });

    $(element).find('.remove-tag').click(function () {
        var that = this;
        var postvars = { };
        postvars['id'] = $(this).attr('data-id');
        postvars['tag'] = $(this).prev().text();
        $.post('/medialib/remove_tag', postvars, function (response) {
            if (!response.error) {
                $(that).prev().remove();
                $(that).remove();
            }
        }, 'json');
    });

    /*
    $(element).on('click', '.expand-artist', function () {
        that.expand_artist($(this).html());
    });
    */

    $(document).on('submit', '#medialib-search-form', function () {
        $('#medialib-search-table').html("<hr/>Searching...");
    });

    return that;
}

$(document).ready(function ()
{
    $('.medialib-playlist').each(function () {
        new MediaLibPlaylist(this);
    });

    $('.medialib-search').each(function () {
        new MediaLibSearch(this);
    });


    /*
    $(document.body).on('click', '.medialib-entry', function () {
        // TODO open a dialog to display the entry's metadata
        new NerveDialog().open_url('/medialib/metadata', { file: '??' });
    });
    */

    $('.medialib-list').on('click', 'tr', function (event) {
        if (event.target.type !== 'checkbox')
            $(this).find(':checkbox').trigger('click');
    });

    $('.medialib-list').on('change', 'td:first-child input', function () {
        if ($(this).is(':checked'))
            $(this).closest('tr').addClass('nerve-highlight-dim');
        else
            $(this).closest('tr').removeClass('nerve-highlight-dim');
    });
});

 
