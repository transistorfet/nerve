
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
        $('#nerve-error').hide();
        $('#nerve-notice').hide();
        var postvars = { 'playlist' : $('#select-playlist').val(), 'urls' : [ ] };
        $('input[name="urls[]"]:checked').each(function () {
            postvars['urls'].push($(this).val());
        });

        $.post('/medialib/remove_urls', postvars, function (response) {
            if (response.count === undefined || response.count <= 0)
                $('#nerve-error').html("No tracks were removed").show();
            else
                $('#nerve-notice').html(response.count + " track(s) were removed from playlist " + postvars['playlist']).show();
            that.update();
        }, 'json');
    }

    that.create_playlist = function ()
    {
        $('#nerve-error').hide();
        $('#nerve-notice').hide();

        var playlist = $('#pl_name').val();
        $.post('/medialib/create_playlist', { 'playlist' : playlist }, function (response) {
            $('#pl_name').val('');
            if (response.error)
                $('#nerve-error').html(response.error).show();
            else if (response.notice) {
                $('#nerve-notice').html(response.notice).show();
                $('#select-playlist').append('<option value="'+playlist+'">'+playlist+'</option>');
                $('#select-playlist').val(playlist);
                that.update();
            }
        }, 'json');
    }

    that.delete_playlist = function ()
    {
        var playlist = $('#select-playlist').val();
        if (confirm("Are you sure you want to delete the playlist: " + playlist)) {
            $.post('/medialib/delete_playlist', { 'playlist' : playlist }, function (response) {
                if (response.error)
                    $('#nerve-error').html(response.error).show();
                else if (response.notice) {
                    $('#nerve-notice').html(response.notice).show();
                    $('#select-playlist option[value="'+playlist+'"]').remove();
                    that.update();
                }
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
    $('.pl_create').click(that.create_playlist);
    $('.pl_delete').click(that.delete_playlist);
    $('.pl_load').click(that.load_playlist);

    $('.pl_current').click(function() {
        $('html, body').animate({ scrollTop: $('.nerve-highlight').offset().top - 100 }, 500);
    });

    $(document).on('click', '#medialib-playlist-contents td:last-child', function () {
        var element = this;
        $.post('/query/player/goto', { 'pos' : $(element).parent().parent().children().index($(element).parent()) }, function (response) {
            $('.medialib-list tr.nerve-highlight').removeClass('nerve-highlight');
            $(element).parent().addClass('nerve-highlight');
        }, 'json');
    });

    that.query_songname = new NerveTimedEvent($('.medialib-query-songname').attr('data-time'), function ()
    {
        var queries = [
            $('.medialib-query-songname').attr('data-query'),
            'player/get_position'
        ];

        Nerve.send_query(queries, function (response) {
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

        $('#nerve-notice').hide();
        $('#nerve-error').hide();
        $.post('/medialib/add_media_items', postvars, function (response) {
            if (response.count === undefined || response.count <= 0) {
                $('#nerve-error').html("No tracks were added").show();
            }
            else {
                $('#nerve-notice').html(response.count + " track(s) were added to playlist " + postvars['playlist']).show();
                $("input[name='media[]']:checked").each(function () {
                    $(this).prop('checked', false);
                });
            }
        }, 'json');
    }

    /*
    $(element).find('#pl_search').click(function () {
        $('#nerve-error').hide();
        $('#nerve-notice').hide();
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

        $('#nerve-notice').hide();
        $('#nerve-error').hide();
        $.post('/medialib/modify_tags', postvars, function (response) {
            if (response.count === undefined || response.count <= 0) {
                $('#nerve-error').html("No tags modified").show();
            }
            else {
                $('#nerve-notice').html(response.count + " track(s) had the following tags added: " + postvars['tags']).show();
                $("input[name='media[]']:checked").each(function () {
                    $(this).prop('checked', false);
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
});

 
