

function NerveButton(element)
{
    this.submit = function ()
    {
        var query = $(element).attr('data-query');
        $.post('/query/' + query, { }, function(response) {
        }, 'json');
    }

    $(element).click(this.submit);
}

function NerveInputSubmit(element)
{
    this.submit = function () {
        var sourceid = $(element).attr('data-source');
        var query = $(element).attr('data-query');
        var data = $('#'+sourceid).val();
        if (data) {
            $.post('/query', { 'queries[]': [ query + ' ' + data ] }, function(response) {
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

    this.time = $(element).attr('data-time');
    this.interval = 0;

    $(window).on('focus', function () {
        if (!obj.interval) {
            obj.interval = setInterval(obj.query, obj.time);
        }
    });

    $(window).on('blur', function () {
        if (obj.interval) {
            clearInterval(obj.interval);
            obj.interval = 0;
        }
    });

    $(element).click(this.query);
    this.query();
}

function NerveQueryBlock(element)
{
    this.query = function ()
    {
        var query = $(element).attr('data-query');
        var parent = $(element);
        $.post('/query/'+query, {}, function(response) {
            for (var key in response) {
                $('.' + key, parent).html(response[key])
            }
        }, 'json');
    }

    this.time = $(element).attr('data-time');
    this.interval = setInterval(this.query, this.time);
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
        $.get(url, { }, function (response) {
            editor_area.val(response);
        }, 'html');
    }

    save_button.click(this.save);
    this.load();
}

function NerveTabs(element)
{
    var container = $(element).attr('data-container');

    $(element).find('.tab').click(function() {
        var data_content = $(this).attr('data-content');

        if (data_content[0] == '/') {
            document.location = data_content;
        }
        else {
            $('#' + container + ' > div').hide();
            $('#' + container + '-' + data_content).show();

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
});



