
function MediaLibPlaylist(element)
{
    var medialib = this;

    this.update = function ()
    {
	$.post('/medialib/get_playlist', { 'playlist' : $('#select-playlist').val() }, function (response) {
	    $('#playlist-contents').html(response);
	}, 'html');
    }

    this.remove_selected = function ()
    {
	$('#nerve-error').hide();
	$('#nerve-notice').hide();
	var postvars = { 'playlist' : $('#select-playlist').val(), 'urls' : [ ] };
	$("input[name='urls']:checked").each(function () {
	    postvars['urls'].push($(this).val());
	});

	$.post('/medialib/remove_urls', postvars, function (response) {
	    if (response.count === undefined || response.count <= 0)
		$('#nerve-error').html("No tracks were removed").show();
	    else
		$('#nerve-notice').html(response.count + " track(s) were removed from playlist " + postvars['playlist']).show();
	    medialib.update();
	}, 'json');
    }

    $('#select-playlist').change(medialib.update);
    medialib.update();

    $('.pl_remove').click(medialib.remove_selected);

    $('.pl_sort').click(function (e) {
	$.post('/medialib/sort_playlist', { 'playlist' : $('#select-playlist').val() }, medialib.update, 'html');
    });

    $('.pl_shuffle').click(function (e) {
	$.post('/medialib/shuffle_playlist', { 'playlist' : $('#select-playlist').val() }, medialib.update, 'html');
    });

    $('.pl_create').click(function (e) {
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
                medialib.update();
            }
        }, 'json');
    });

    $('.pl_delete').click(function (e) {
        var playlist = $('#select-playlist').val();
        if (confirm("Are you sure you want to delete the playlist: " + playlist)) {
	    $.post('/medialib/delete_playlist', { 'playlist' : playlist }, function (response) {
                if (response.error)
                    $('#nerve-error').html(response.error).show();
                else if (response.notice) {
                    $('#nerve-notice').html(response.notice).show();
                    $('#select-playlist option[value="'+playlist+'"]').remove();
                    medialib.update();
                }
            });
        }
    });

    $('.pl_load').click(function (e) {
	$.post('/query', { 'queries[]' : "player.load_playlist " + $('#select-playlist').val() }, function (response) { }, 'json');
    });
}

function MediaLibSearch(element)
{
    var medialib = this;

    this.search = function ()
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
	    $(element).find('#search-results').html(response);
	    $(element).find('#search-table').show();
	}, 'html');
    }

    this.expand_artist = function (artist)
    {
	var postvars = { };
	postvars['mode'] = 'title';
	postvars['order'] = 'artist';
	postvars['search'] = artist;

	$.post("/medialib/get_search_results", postvars, function(response) {
	    $('#search-results').html(response);
	}, 'html');
    }

    this.add_tracks = function (method)
    {
	var postvars = { };
	postvars['method'] = method;
	postvars['playlist'] = $('#select-playlist').val();
	postvars['media'] = [ ];

	$("input[name='media']:checked").each(function () {
	    postvars['media'].push($(this).val());
	});

	$.post('/medialib/add_tracks', postvars, function (response) {
	    if (response.count === undefined || response.count <= 0) {
		$('#nerve-error').html("No tracks were added").show();
	    }
	    else {
		$('#nerve-notice').html(response.count + " track(s) were added to playlist " + postvars['playlist']).show();
		$("input[name='media']:checked").each(function () {
		    $(this).prop('checked', false);
		});
	    }
	}, 'json');
    }

    $(element).find('#pl_search').click(function () {
	$('#nerve-error').hide();
	$('#nerve-notice').hide();
	medialib.search();
    });
    if (window.location.href.indexOf("?") > 0)
	medialib.search();

    $(element).find('.pl_enqueue').click(function () {
	medialib.add_tracks('enqueue');
    });

    $(element).find('.pl_replace').click(function () {
	if (confirm("Are you sure you want to replace everything on playlist " + $('#select-playlist').val()))
	    medialib.add_tracks('replace');
    });

    $(element).delegate('.expand-artist', 'click', function () {
	medialib.expand_artist($(this).html());
    });

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

 
