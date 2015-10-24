

var Nerve = { };

Nerve.send_query = function (query, success, error)
{
    var postvars = {  }

    if ($.isArray(query))
        postvars['requests[]'] = query;
    else
        postvars['requests[]'] = [ query ];

    $.post('/query', postvars, success, error, 'json');
}


function NerveTimedEvent(interval, ontimeout)
{
    var that = this;
    //var that = (this.prototype == Object.prototype) ? this : { };

    that.timer = undefined;
    that.interval = interval;
    that.ontimeout = ontimeout;

    that.set_ontimeout = function (ontimeout)
    {
        that.ontimeout = ontimeout;
    }

    that.trigger = function ()
    {
        that.ontimeout();
    }

    that.start_timer = function ()
    {
        return that.reset_timer();
    }

    that.trigger_and_start_timer = function ()
    {
        that.trigger();
        that.start_timer();
    }

    that.reset_timer = function ()
    {
        if (document.hidden) {
            if (that.timer) {
                clearInterval(that.timer);
                that.timer = undefined;
            }
        }
        else {
            if (that.timer)
                clearInterval(that.timer);
            that.timer = setInterval(that.trigger, that.interval);
        }
    }

    that.stop_timer = function ()
    {
        clearInterval(that.timer);
    }

    document.addEventListener('visibilitychange', that.start_timer);

    return that;
}


function NerveClickCounter(element, onclick)
{
    var that = this;

    that.timer = undefined;
    that.current_count = 0;
    that.onclick = onclick;

    that.set_onclick = function (onclick)
    {
        that.onclick = onclick;
    }

    that.count_click = function ()
    {
        if (that.timer) {
            clearTimeout(that.timer);
            that.current_count += 1;
        }
        else
            that.current_count = 1;
        that.timer = setTimeout(that.send_click, 250);
    }

    that.send_click = function ()
    {
        if (that.timer) {
            clearTimeout(that.timer);
            that.timer = undefined;
        }
        that.onclick(that.current_count);
        that.current_count = 0;
    }

    $(element).click(that.count_click);

    return that;
}



//// Element Widgets ////

function NerveButton(element)
{
    var that = this;

    that.submit = function ()
    {
        var query = $(element).attr('data-query');
        if (query) {
            if (query[0] == '/' || query.indexOf('http://') == 0)
                $.post('/query', { 'requests[]': [ query ] }, function(response) {}, 'json');
            else
                $.post('/query/'+query, {}, function(response) {}, 'json');
        }
    }

    $(element).click(that.submit);

    return that;
}


function NerveSlider(element)
{
    var that = this;

    that.send_change = function ()
    {
        var query = $(element).attr('data-query');
        var value = $(element).val();
        if (query) {
            $.post('/query/'+query, { 'a' : value }, function(response) {
            }, 'json');
        }
    }

    $(element).on('change input', that.send_change);

    return that;
}


function NerveInputSubmit(element)
{
    var that = this;

    that.submit = function () {
        var sourceid = $(element).attr('data-source');
        var query = $(element).attr('data-query');
        var data = $('#'+sourceid).val();
        var postvars = { };
        postvars[$(element).attr('name')] = data;
        if (query && data) {
            $.post('/query/'+query, postvars, function(response) {
            }, 'json');
        }
    }

    $(element).click(that.submit);

    return that;
}



Nerve.update_element_contents = function (element, response)
{
    if ($(element).attr('data-round')) {
        var decimals = Math.pow(10, $(element).attr('data-round'));
        response = Math.round(parseFloat(response) * decimals) / decimals;
    }
    $(element).html(response)
}


function NerveQuery(element)
{
    var that = this;

    that.query = function ()
    {
        Nerve.send_query($(element).attr('data-query'), function (response) {
            Nerve.update_element_contents(element, response[0]);
        });
    }

    $(element).click(that.query);

    that.update_timer = new NerveTimedEvent($(element).attr('data-time'), that.query);
    that.update_timer.trigger_and_start_timer();

    return that;
}


function NerveQueryBlock(element)
{
    var that = this;

    that.query = function ()
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
                Nerve.update_element_contents(elements[i], response[i]);
            }
        }, 'json');
    }

    $(element).click(that.query);

    that.update_timer = new NerveTimedEvent($(element).attr('data-time'), that.query);
    that.update_timer.trigger_and_start_timer();

    return that;
}


function NerveEditor(element)
{
    var that = this;

    var save_button = $(element).find('#editor-save');
    var editor_area = $(element).find('#editor-area');

    that.save = function ()
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

    that.load = function () {
        var url = editor_area.attr('data-source');
        if (url) {
            $.get(url, { }, function (response) {
                editor_area.val(response);
            }, 'html');
        }
    }

    save_button.click(that.save);
    that.load();

    return that;
}


function NerveTabs(element)
{
    var that = this;

    function select_tab(tab) {
        // unselect all tabs in this tab container, and select the clicked tab
        $(tab).parent().show();
        $(tab).parent().find('.tab').removeClass('selected');
        $(tab).addClass('selected');

        // if there are parent tabs, then select the right parent tab
        var parenttabs = $(tab).parent().attr('data-parent');
        if (parenttabs) {
            select_tab($('#' + parenttabs).find('.tab[data-content=#' + $(tab).parent().attr('id') + ']'));
        }
    }

    function hide_containers(tabs, except) {
        $('div [data-parent=' + $(tabs).attr('id') + ']').each(function () {
            if (!$(that).is(except))
                $(that).hide();
            hide_containers(that);
        });
    }

    function show_container(data_content) {
        //window.location.hash = data_content;
        window.history.pushState({}, '', data_content);
        hide_containers(element, data_content);

        if ($(data_content).is('.nerve-tabs')) {
            if ($(data_content).is(':hidden'))
                $(data_content).slideDown('fast');
            else
                $(data_content).slideUp('fast');

            var selected = $(data_content).find('.tab.selected');
            if (selected.length == 0)
                selected = $(data_content).find('.tab').first();
            //$(selected).trigger('click');
        }
        else {
            $(data_content).show();
        }
    }

    // hide all elements in the tab's container
    $('div [data-parent=' + $(element).attr('id') + ']').hide();

    // highlight the initially selected tab
    $(element).find('.tab').each(function() {
        var data_content = $(this).attr('data-content');

        if (data_content == window.location.pathname) {
            select_tab(this);
        }
        else if (data_content == window.location.hash) {
            select_tab(this);
            show_container(data_content);
        }
    });

    $(element).find('.tab').click(function() {
        var data_content = $(this).attr('data-content');

        if (data_content[0] == '/') {
            window.location = data_content;
        }
        else if (data_content[0] == '#') {
            select_tab(this);
            show_container(data_content);
        }
    }); 

    return that;
}


function NerveFloatingBarTop(element)
{
    var that = this;
    var top = $(element).offset().top;
    var height = $(element).outerHeight();
    console.log(height);

    $(window).scroll(function () {
        if ($(window).scrollTop() >= top) {
            $(element).css('position', 'fixed');
            $(element).css('top', 0);
            $(element).next().css('margin-top', height);
        }
        else {
            $(element).css('position', 'relative');
            $(element).css('top', 'auto');
            $(element).next().css('margin-top', 'inherit');
        }
    });

    return that;
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

    $('.nerve-floatingbar-top').each(function () {
        new NerveFloatingBarTop(this);
    });

    $('#nerve-notice').click(function () {
        $(this).hide();
    });

    $('#nerve-error').click(function () {
        $(this).hide();
    });
});



