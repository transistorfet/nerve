

function NerveButton(element)
{
    this.submit = function ()
    {
        var query = $(element).attr('data-query');
        if (query) {
            if (query[0] == '/' || query.indexOf('http://') == 0)
                $.post('/query', { 'requests[]': [ query ] }, function(response) {}, 'json');
            else
                $.post('/query/'+query, {}, function(response) {}, 'json');
        }
    }

    $(element).click(this.submit);
}

function NerveSlider(element)
{
    this.send_change = function ()
    {
        var query = $(element).attr('data-query');
        var value = $(element).val();
        if (query) {
            $.post('/query/'+query, { 'a' : value }, function(response) {
            }, 'json');
        }
    }

    $(element).on('change input', this.send_change);
}

function NerveInputSubmit(element)
{
    this.submit = function () {
        var sourceid = $(element).attr('data-source');
        var query = $(element).attr('data-query');
        var data = $('#'+sourceid).val();
        if (query && data) {
            $.post('/query/'+query, { 'a' : data }, function(response) {
            }, 'json');
        }
    }

    $(element).click(this.submit);
}

function NerveQuery(element)
{
    var obj = this;

    this.query = function ()
    {
        var query = $(element).attr('data-query');
        $.post('/query/'+query, {}, function(response) {
            $(element).html(response)
        }, 'json');
    }

    this.interval = 0;
    this.time = $(element).attr('data-time');

    this.set_timer = function ()
    {
        if (document.hidden)
            clearInterval(obj.interval);
        else
            obj.interval = setInterval(obj.query, obj.time);
    }

    document.addEventListener('visibilitychange', this.set_timer);
    this.set_timer();

    $(element).click(this.query);
    this.query();
}

function NerveQueryBlock(element)
{
    var obj = this;

    this.query = function ()
    {
        var queries = [ ];
        var elements = [ ];
        var parent = $(element);

        $(element).find('.nerve-query-item').each(function (i, e) {
            queries.push($(e).attr('data-query'));
            elements.push(e);
        });

        $.post('/query', { 'requests[]': queries }, function(response) {
            for (var i in response) {
                $(elements[i]).html(response[i])
            }
        }, 'json');
    }

    this.interval = 0;
    this.time = $(element).attr('data-time');

    this.set_timer = function ()
    {
        if (document.hidden)
            clearInterval(obj.interval);
        else
            obj.interval = setInterval(obj.query, obj.time);
    }

    document.addEventListener('visibilitychange', this.set_timer);
    this.set_timer();

    $(element).click(this.query);
    this.query();
}

function NerveEditor(element)
{
    var save_button = $(element).find('#editor-save');
    var editor_area = $(element).find('#editor-area');

    this.save = function ()
    {
        var url = save_button.attr('data-target');
        var postvars = { };
        postvars['data'] = editor_area.val();
        $.post(url, postvars, function (response) {
            if (response.status == "success")
                $('#nerve-notice').html(response.message).show();
            else
                $('#nerve-error').html(response.message).show();
        }, 'json');
    }

    this.load = function () {
        var url = editor_area.attr('data-source');
        if (url) {
            $.get(url, { }, function (response) {
                editor_area.val(response);
            }, 'html');
        }
    }

    save_button.click(this.save);
    this.load();
}

function NerveTabs(element)
{
    var container = $(element).attr('data-container');

    // hide all elements in the tab's container
    $('#' + container + ' > div').hide();

    // highlight the initially selected tab
    $(element).find('.tab').each(function() {
        var data_content = $(this).attr('data-content');

        if (data_content == window.location.pathname) {
            $(element).find('.tab').removeClass('selected');
            $(this).addClass('selected');
        }
    });

    $(element).find('.tab .selected').each(function () {
        var data_content = $(this).attr('data-content');
        $('#' + container + ' > #' + data_content).show();
    });

    $(element).find('.tab').click(function() {
        var data_content = $(this).attr('data-content');

        if (data_content[0] == '/') {
            document.location = data_content;
        }
        else {
            $('#' + container + ' > div').hide();
            $('#' + container + ' > #' + data_content).show();

            $(element).find('.tab').removeClass('selected');
            $(this).addClass('selected');
        }
    }); 
}

$(document).ready(function()
{
    $('.nerve-button').each(function () {
        new NerveButton(this);
    });

    $('.nerve-slider').each(function () {
        new NerveSlider(this);
    });

    $('.nerve-input-submit').each(function () {
        new NerveInputSubmit(this);
    });

    $('.nerve-query').each(function () {
        new NerveQuery(this);
    });

    $('.nerve-query-block').each(function () {
        new NerveQueryBlock(this);
    });

    $('.nerve-editor').each(function () {
        new NerveEditor(this);
    });

    $('.nerve-tabs').each(function () {
        new NerveTabs(this);
    });

    $('#nerve-status').click(function () {
        $(this).hide();
    });

    $('#nerve-error').click(function () {
        $(this).hide();
    });
});



