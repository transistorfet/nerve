

var Nerve = { };

Nerve.query = function (query, success, error, returntype)
{
    returntype = returntype || 'json';

    var postvars = {  };

    if ($.isArray(query))
        postvars['requests[]'] = query;
    else
        postvars['requests[]'] = [ query ];

    $.post('/query', postvars, success, error, returntype);
}

Nerve.request = function (url, data, success, error, returntype, method, contenttype)
{
    var request = { };

    request['url'] = url;
    request['method'] = method || 'POST';
    request['dataType'] = returntype || 'json';

    if (contenttype === undefined || contenttype == 'application/json') {
        request['contentType'] = 'application/json';
        request['data'] = JSON.stringify(data);
    }
    else if (contenttype == 'application/x-www-form-urlencoded')
        request['data'] = data;
    else {
        request['contentType'] = contenttype;
        request['data'] = data;
    }

    request['success'] = success || Nerve.display_response;
    request['error'] = error;

    $.ajax(request);
}

Nerve.join_path = function (base, path)
{
    if (path[0] == '/' || path.indexOf('://') != -1)
        return path;
    return base.rtrim('/') + '/' + path;
}

Nerve.display_response = function (response) {
    if (response.error) {
        Nerve.set_error(response.error);
        return false;
    }
    else if (response.notice) {
        Nerve.set_notice(response.notice);
    }
    return true;
}

Nerve.set_notice = function (message)
{
    $('#nerve-error').hide();
    $('#nerve-notice').html(message).show();
}

Nerve.set_error = function (message)
{
    $('#nerve-notice').hide();
    $('#nerve-error').html(message).show();
}

Nerve.clear_notices = function ()
{
    $('#nerve-notice').hide();
    $('#nerve-error').hide();
}


NerveTimedEvent = (function ()
{
    var Constructor = function (milliseconds, ontimeout)
    {
        this.timer = undefined;
        this.milliseconds = milliseconds;
        this.ontimeout = ontimeout;

        document.addEventListener('visibilitychange', $.proxy(this.reset, this));

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.set_ontimeout = function (ontimeout)
    {
        this.ontimeout = ontimeout;
    }

    Proto.trigger = function ()
    {
        this.ontimeout();
    }

    Proto.start = function ()
    {
        return this.reset();
    }

    Proto.trigger_and_reset = function ()
    {
        this.trigger();
        this.reset();
    }

    Proto.reset = function ()
    {
        if (document.hidden) {
            if (this.timer) {
                clearTimeout(this.timer);
                this.timer = undefined;
            }
        }
        else {
            if (this.timer)
                clearTimeout(this.timer);
            this.timer = setTimeout($.proxy(this.trigger, this), this.milliseconds);
        }
    }

    Proto.stop = function ()
    {
        clearTimeout(this.timer);
    }

    return Constructor;
})();


NerveTimedInterval = (function ()
{
    var Constructor = function (interval, ontimeout)
    {
        this.timer = undefined;
        this.interval = interval;
        this.ontimeout = ontimeout;

        document.addEventListener('visibilitychange', $.proxy(this.reset, this));

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.set_ontimeout = function (ontimeout)
    {
        this.ontimeout = ontimeout;
    }

    Proto.trigger = function ()
    {
        this.ontimeout();
    }

    Proto.start = function ()
    {
        return this.reset();
    }

    Proto.trigger_and_reset = function ()
    {
        this.trigger();
        this.reset();
    }

    Proto.reset = function ()
    {
        if (document.hidden) {
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = undefined;
            }
        }
        else {
            if (this.timer)
                clearInterval(this.timer);
            this.timer = setInterval($.proxy(this.trigger, this), this.interval);
        }
    }

    Proto.stop = function ()
    {
        clearInterval(this.timer);
    }

    return Constructor;
})();


NerveClickCounter = (function ()
{
    var Constructor = function (element, onclick)
    {
        this.timer = undefined;
        this.current_count = 0;
        this.onclick = onclick;

        $(element).click($.proxy(this.count_click, this));

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.set_onclick = function (onclick)
    {
        this.onclick = onclick;
    }

    Proto.count_click = function ()
    {
        if (this.timer) {
            clearTimeout(this.timer);
            this.current_count += 1;
        }
        else
            this.current_count = 1;
        this.timer = setTimeout($.proxy(this.send_click, this), 250);
    }

    Proto.send_click = function ()
    {
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = undefined;
        }
        this.onclick(this.current_count);
        this.current_count = 0;
    }

    return Constructor;
})();



//// Element Widgets ////

/*
function NerveButton(element)
{
    var that = this;

    that.submit = function ()
    {
        var query = $(element).attr('data-query');
        if (query) {
            // TODO we can move this to join_path()
            if (query[0] == '/' || query.indexOf('http://') == 0)
                $.post('/query', { 'requests[]': [ query ] }, function(response) {}, 'json');
            else
                $.post('/query/'+query, {}, function(response) {}, 'json');
        }
    }

    $(element).click($.proxy(that.submit, that));

    return that;
}


NerveButton = function ()
{
    return this;
}
NerveButton.ready = function ()
{
    $(document).on('click', '.nerve-button', function () {
        NerveButton.trigger(this);
    });
}
NerveButton.trigger = function (element)
{
    var query = $(element).attr('data-query');
    if (query) {
        // TODO we can move this to join_path()
        if (query[0] == '/' || query.indexOf('http://') == 0)
            $.post('/query', { 'requests[]': [ query ] }, function(response) {}, 'json');
        else
            $.post('/query/'+query, {}, function(response) {}, 'json');
    }
}
*/

NerveButton = (function ()
{
    var Constructor = { };

    Constructor.ready = function ()
    {
        $(document).on('click', '.nerve-button', function () {
            Constructor.trigger(this);
        });
    }

    Constructor.trigger = function (element)
    {
        var query = $(element).attr('data-query');
        if (query) {
            // TODO we can move this to join_path()
            if (query[0] == '/' || query.indexOf('http://') == 0)
                $.post('/query', { 'requests[]': [ query ] }, function(response) {}, 'json');
            else
                $.post('/query/'+query, {}, function(response) {}, 'json');
        }
    }
    return Constructor;
})();


NerveSlider = (function ()
{
    var Constructor = function (element)
    {
        this.$element = $(element);
        this.$element.on('change input', $.proxy(this.send_change, this));

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.send_change = function ()
    {
        var query = this.$element.attr('data-query');
        var value = this.$element.val();
        if (query) {
            $.post('/query/'+query, { '$0' : value }, function(response) {
            }, 'json');
        }
    }

    return Constructor;
})();


NerveInputSubmit = (function ()
{
    var Constructor = function (element)
    {
        this.$element = $(element);
        this.$element.click($.proxy(this.submit, this));

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.submit = function () {
        var $sourceid = $(this.$element.attr('data-source'));
        var query = this.$element.attr('data-query');
        var data = $sourceid.val();
        var postvars = { };
        postvars[$sourceid.attr('name')] = data;
        if (query && data) {
            $.post('/query/'+query, postvars, function(response) {
                $sourceid.val('');
            }, 'json');
        }
    }

    return Constructor;
})();



Nerve.update_element_contents = function (element, response)
{
    if ($(element).attr('data-round')) {
        var decimals = Math.pow(10, $(element).attr('data-round'));
        response = Math.round(parseFloat(response) * decimals) / decimals;
    }
    $(element).html(response)
}


NerveQuery = (function ()
{
    var Constructor = function (element)
    {
        this.$element = $(element);
        this.$element.click($.proxy(this.query, this));

        this.update = new NerveTimedInterval(this.$element.attr('data-time'), $.proxy(this.query, this));
        this.update.trigger_and_reset();

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.query = function ()
    {
        var that = this;

        Nerve.query(this.$element.attr('data-query'), function (response) {
            Nerve.update_element_contents(that.$element, response ? response[0] : 'null');
        });
    }

    return Constructor;
})();


NerveQueryBlock = (function ()
{
    var Constructor = function (element)
    {
        this.$element = $(element);

        this.$element.click($.proxy(this.query, this));

        this.update = new NerveTimedInterval(this.$element.attr('data-time'), $.proxy(this.query, this));
        this.update.trigger_and_reset();

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.query = function ()
    {
        var queries = [ ];
        var elements = [ ];

        this.$element.find('.nerve-query-item').each(function (i, e) {
            queries.push($(e).attr('data-query'));
            elements.push(e);
        });

        $.post('/query', { 'requests[]': queries }, function(response) {
            for (var i in response) {
                Nerve.update_element_contents(elements[i], response[i]);
            }
        }, 'json');
    }

    return Constructor;
})();


NerveEditor = (function ()
{
    var Constructor = function (element)
    {
        this.$element = $(element);
        this.save_button = this.$element.find('#editor-save');
        this.editor_area = this.$element.find('#editor-area');

        this.save_button.click($.proxy(this.save, this));
        this.load();

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.save = function ()
    {
        var url = this.save_button.attr('data-action');
        var postvars = { };
        postvars['data'] = this.editor_area.val();
        $.post(url, postvars, Nerve.display_response, 'json');
    }

    Proto.load = function () {
        var url = this.editor_area.attr('data-source');
        if (url) {
            $.get(url, { }, function (response) {
                this.editor_area.val(response);
            }, 'html');
        }
    }

    return Constructor;
})();


NerveTabs = (function ()
{
    var Constructor = function (element)
    {
        var that = this;

        this.$element = $(element);

        // hide all elements in the tab's container
        $('div [data-parent=' + this.$element.attr('id') + ']').hide();

        // highlight the initially selected tab
        $(element).find('.tab').each(function() {
            var data_content = $(this).attr('data-content');

            if (data_content == window.location.pathname) {
                that.select_tab(this);
            }
            else if (data_content == window.location.hash) {
                that.select_tab(this);
                that.show_container(data_content);
            }
        });

        // handle clicking on tabs
        $(element).find('.tab').mousedown(function(e) {
            var data_content = $(this).attr('data-content');

            if (e.which == 2) {
                window.open(data_content, '_blank');
            }
            else if (e.which == 1) {
                if (data_content[0] == '/') {
                    window.location = data_content;
                }
                else if (data_content[0] == '#') {
                    that.select_tab(this);
                    that.show_container(data_content);
                }
            }
        });

        // TODO make it hide the tabs and show them when you scroll up a bit without being at the top (conflicts with floatingbar)
        /*
        if ($(element).hasClass('pulldown')) {
            var current = $(window).scrollTop();
            $(window).scroll(function () {
                if ($(window).scrollTop() >= current) {
                    current = $(window).scrollTop();
                }
            });
        }
        */

        return this;
    }

    var Proto = Constructor.prototype;

    Proto.select_tab = function (tab)
    {
        // unselect all tabs in this tab container, and select the clicked tab
        $(tab).parent().show();
        $(tab).parent().find('.tab').removeClass('selected');
        $(tab).addClass('selected');

        // if there are parent tabs, then select the right parent tab
        var parenttabs = $(tab).parent().attr('data-parent');
        if (parenttabs) {
            this.select_tab($('#' + parenttabs).find('.tab[data-content=#' + $(tab).parent().attr('id') + ']'));
        }
    }

    Proto.hide_containers = function (tabs, except)
    {
        var that = this;

        $('div [data-parent=' + $(tabs).attr('id') + ']').each(function () {
            if (!$(this).is(except))
                $(this).hide();
            that.hide_containers(this);
        });
    }

    Proto.show_container = function (data_content)
    {
        window.location.hash = data_content;
        //window.history.pushState({}, '', data_content);
        this.hide_containers(this.$element, data_content);

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

    return Constructor;
})();


function NerveFloatingBarTop(element)
{
    var that = this;
    var offset = $(element).offset();

    $(window).scroll(function () {
        if ($(window).scrollTop() >= offset.top) {
            if ($(element).css('position') != 'fixed') {
                var height = $(element).outerHeight();

                $(element).css('position', 'fixed');
                $(element).css('top', 0);
                // TODO this is a bit of a hack, we're assuming the right padding is the same as the left padding
                $(element).css('padding-left', parseInt($(element).css('padding-right')) + offset.left);
                $(element).css('border-bottom', '1px solid black');

                // leave a gap above the next element for the floating bar
                $(element).next().css('margin-top', height);
            }
        }
        else {
            if ($(element).css('position') != 'relative') {
                $(element).css('position', 'relative');
                $(element).css('top', 'auto');
                $(element).css('padding-left', parseInt($(element).css('padding-right')));
                $(element).css('border-bottom', '1px none black');

                $(element).next().css('margin-top', 'inherit');
            }
        }
    });

    return that;
}


/*
NerveDisplayToggle = (function ()
{
    $(document).on('click', '.nerve-display-toggle', function () {
        var target = $(this).attr('data-target');
        $(target).slideToggle();
    });
})();
*/

NerveDisplayToggle = (function ()
{
    var Constructor = { };

    Constructor.ready = function ()
    {
        $(document).on('click', '.nerve-display-toggle', function () {
            var target = $(this).attr('data-target');
            $(target).slideToggle();
        });
    }
    return Constructor;
})();



NerveDialogOpen = (function ()
{
    var Constructor = function(element, options)
    {
        this.$element = $(element);
        this.$element.data('nerve-dialog-open', this);
        this.$target = $(this.$element.attr('data-target'));
        this.fetch = this.$element.attr('data-fetch');
        this.dialog = this.$target.length > 0 ? this.$target.data('nerve-dialog') : null;
        return this;
    }

    Constructor.ready = function ()
    {
        $(document).on('click', '.nerve-dialog-open', function () {
            var that = $(this).data('nerve-dialog-open') || new NerveDialogOpen(this);
            that.trigger();
        });
    }

    Constructor.prototype.trigger = function ()
    {
        if (this.fetch) {
            var dialog = new NerveDialog();
            if (this.$element.hasClass('modal'))
                dialog.set_modal(true);
            dialog.open_url(this.fetch);
        }
        else {
            // TODO you can replace this with a static method NerveDialog.prototype.get(this.$element.attr('data-target'))
            //var $target = $(this.$element.attr('data-target'));
            //var dialog = $target.data('nerve-dialog');
            //if (dialog)
            //    dialog.open();
            if (this.dialog)
                this.dialog.open();
        }
    }

    return Constructor;
})();


NerveDialog = (function ()
{
    var Constructor = function(element, options)
    {
        if ($.isPlainObject(element)) {
            options = element;
            element = null;
        }

        this.options = $.extend({}, Constructor.defaults, options);

        this.built = false;
        this.result = null;
        this.underlay = $('<div class="nerve-modal-underlay"></div>');
        this.dialog = element ? $(element) : $('<div class="nerve-dialog"></div>');
        this.dialog.data('nerve-dialog', this);

        if (this.dialog.attr('data-fetch'))
            this.options.fetch = this.dialog.attr('data-fetch');
        if (this.dialog.attr('data-action'))
            this.options.action = this.dialog.attr('data-action');
        if (this.dialog.is('.nerve-dialog.modal'))
            this.options.modal = true;

        //this.dialog.hide();
        //this.dialog.detach();

        //if (this.options.content)
        //    this.set_content(this.options.content);
        if (this.options.fetch)
            this.open_url(this.options.fetch);

        return this;
    }

    Constructor.defaults = {
        modal: true,
        ok: true,
        cancel: true,
        center: true,
        autoclear: true,
        onsubmit: null,
        id: null,
        content: null,
        fetch: null,
        action: null,
    }

    var Proto = Constructor.prototype;

    Proto.build_dialog = function (element)
    {
        var that = this;

        if (that.options.id)
            that.dialog.attr('id', that.options.id);
        if (that.options.content)
            that.dialog.empty().html(that.options.content);
        that._build_buttons();

        that.dialog.on('click', '.nerve-dialog-submit', function () {
            that.submit(this);
        });

        that.dialog.on('click', '.nerve-dialog-cancel', function () {
            that.close();
        });

        that.dialog.on('nerve:form:success', '.nerve-form', function () {
            that.dialog.trigger('nerve:dialog:success');
            that.close();
        });

        // Attach handler to dialog open buttons that target this dialog window
        //$(document).on('click', '.nerve-dialog-open[data-target="#'+that.dialog.attr('id')+'"]', function () {
        //    that.open();
        //});
        that.built = true;
        return that;
    }

    Proto._build_buttons = function ()
    {
        var that = this;

        /*
        var submit = that.dialog.find('.nerve-form-submit');
        if (that.options.ok && that.dialog.find('.nerve-dialog-submit').length <= 0 && submit.length <= 0) {
            that.dialog.append(' ');
            that.dialog.append($('<button class="nerve-dialog-submit">Ok</button>'));
        }
        if (that.options.cancel && that.dialog.find('.nerve-dialog-cancel').length <= 0) {
            var cancel = $('<button type="button" class="nerve-dialog-cancel">Cancel</button>');
            if (submit.length > 0) {
                submit.after(cancel);
                submit.after(' ');
            }
            else {
                that.dialog.append(' ');
                that.dialog.append(cancel);
            }
        }
        */

        var submit = that.dialog.find('.nerve-form-submit');
        var buttons = that.dialog.find('.nerve-dialog-buttons');
        if (submit.length > 0) {
            if (that.options.cancel) {
                submit.after($('<button class="nerve-dialog-cancel">Cancel</button>'))
                submit.after(' ');
            }
        }
        else if (that.dialog.find('.nerve-dialog-buttons').length <= 0) {
            var buttons = $('<div class="nerve-dialog-buttons"></div>');
            if (that.options.ok)
                buttons.append($('<button class="nerve-dialog-submit">Ok</button>'));
            if (that.options.cancel) {
                buttons.append(' ');
                buttons.append($('<button class="nerve-dialog-cancel">Cancel</button>'));
            }
            that.dialog.append(buttons);
        }
        return that;
    }

    Proto.get_option = function (name)
    {
        return this.options[name];
    }

    Proto.set_option = function (name, val)
    {
        if (Constructor.defaults.hasOwnProperty(name))
            this.options[name] = val;
        return this;
    }

    Proto.set_modal = function (bool)
    {
        var that = this;

        if (that.dialog.is(':hidden')) {
            that.options.modal = bool;
            that.options.center = bool;
        }
        return that;
    }

    Proto.set_content = function (content)
    {
        var that = this;

        that.options.content = content;
        /*
        that.dialog.empty().html(content);
        that._build_buttons();
        */
        return that;
    }

    Proto.onsubmit = function (onsubmit)
    {
        var that = this;

        that.options.onsubmit = onsubmit;
        return that;
    }

    Proto.confirm = function (message, onsubmit)
    {
        this.set_content(message);
        this.open(onsubmit);
    }

    Proto.open_url = function (url, data)
    {
        var that = this;

        that.options.autoclear = false;
        $.get(url, data, function (response)
        {
            that.set_content(response);
            that.open();
        }, 'html');
        return that;
    }

    Proto.open = function (onsubmit)
    {
        var that = this;

        if (onsubmit)
            that.options.onsubmit = onsubmit;
        if (that.options.autoclear)
            that.clear_data(that.dialog);

        that._close_other_dialogs();
        if (that.built !== true)
            that.build_dialog();

        if (that.options.modal)
            $(document.body).append(that.underlay);
        $(document.body).append(that.dialog);

        if (that.options.center) {
            that.move_to_center();
            $(window).on('resize.nerve-dialog', function () {
                that.move_to_center();
            });
        }

        that.dialog.show();
        return that;
    }

    Proto.close = function ()
    {
        var that = this;

        that.dialog.hide();
        if (!that.dialog.attr('id'))
            that.dialog.detach();
        if (that.options.modal)
            that.underlay.detach();
        $(window).off('resize.nerve-dialog');
        return that;
    }

    Proto._close_other_dialogs = function ()
    {
        var that = this;

        $('.nerve-dialog').each(function () {
            var obj = $(this).data('nerve-dialog');
            if (obj && obj != that)
                obj.close();
        });
    }

    Proto.move_to_center = function ()
    {
        var that = this;

        var posX = ($(window).width() - that.dialog.outerWidth(true)) / 2;
        var posY = ($(window).height() - that.dialog.outerHeight(true)) / 2;
        posX = (posX >= 0) ? posX : 0;
        posY = (posY >= 0) ? posY : 0;

        //console.log($(window).width() + " " + $(window).height());
        //console.log(that.dialog.outerWidth() + " " + that.dialog.outerHeight());
        //console.log(posX + " " + posY);
        that.dialog.css('position', 'fixed');
        that.dialog.css('left', posX + 'px');
        that.dialog.css('top', posY + 'px');
    }

    Proto.submit = function (button)
    {
        var that = this;

        if (that.options.action) {
            that.result = that.options.pack ? that.options.pack(that.dialog) : that.pack_data(that.dialog);
            Nerve.request(that.options.action, that.result, function (response) {
                if (that.display_response(response))
                    that.dialog.trigger('nerve:dialog:success', [ that.result, response ]);
            });
        }
        else {
            if (that.options.onsubmit)
                that.result = that.options.onsubmit(that);
            else
                that.result = that.options.pack ? that.options.pack(that.dialog) : that.pack_data(that.dialog);

            if (that.result)
                that.dialog.trigger('nerve:dialog:success', [ that.result ]);
        }

        if (that.result)
            that.close();
    }

    Proto.pack_data = function (dialog)
    {
        var postvars = { };

        dialog.find('input:not([type="checkbox"],[type="radio"],[type="button"],[type="submit"]),select,textarea').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });

        dialog.find('input[type="checkbox"]').each(function () {
            postvars[$(this).attr('name')] = $(this).is(':checked') ? true : false;
        });

        dialog.find('input[type="radio"]:checked').each(function () {
            postvars[$(this).attr('name')] = $(this).val();
        });
        return postvars;
    }

    Proto.clear_data = function (dialog)
    {
        dialog.find('input:not([type="checkbox"],[type="radio"],[type="button"],[type="submit"]),select,textarea').val('');
        dialog.find('input[type="checkbox"]').val('');
        dialog.find('input[type="radio"]:checked').prop('checked', false);
    }

    Proto.display_response = function (response)
    {
        if (response.error) {
            this.set_error(response.error);
            return false;
        }
        else if (response.notice) {
            Nerve.set_notice(response.notice);
            this.close();
        }
        return true;
    }

    Proto.set_error = function (error)
    {
        var that = this;
        var errorbar = that.dialog.find('#nerve-error');
        if (errorbar.length <= 0) {
            errorbar = $('<div id="nerve-error"></div>');
            that.dialog.append(errorbar);
        }
        $(errorbar).html(error).show();
    }

    return Constructor;
})();


// Examples:
//    new NerveDialog(null, {
//        modal: true,
//        content: "Are you sure you want to delete " + remote + " and all of it's associated buttons and events?",
//        onsubmit: function ()
//        {
//            return true;    // returning true will hide the dialog
//        }
//    }).open();
// 
//    new NerveDialog()
//        .set_modal(true)
//        .set_content("Are you sure you want to delete " + remote + " and all of it's associated buttons and events?")
//        .open(function ()
//        {
//            return true;    // returning true will hide the dialog
//        });


Nerve.attachWidgets = function (element)
{
    $('.nerve-slider', element).each(function () {
        new NerveSlider(this);
    });

    $('.nerve-input-submit', element).each(function () {
        new NerveInputSubmit(this);
    });

    $('.nerve-query', element).each(function () {
        new NerveQuery(this);
    });

    $('.nerve-query-block', element).each(function () {
        new NerveQueryBlock(this);
    });

    $('.nerve-editor', element).each(function () {
        new NerveEditor(this);
    });

    $('.nerve-tabs', element).each(function () {
        new NerveTabs(this);
    });

    $('.nerve-floatingbar-top', element).each(function () {
        new NerveFloatingBarTop(this);
    });

    $('.nerve-dialog', element).each(function () {
        new NerveDialog(this);
    });
}


$(document).ready(function()
{
    $(document).on('click', '#nerve-notice', function () {
        $(this).hide();
    });

    $(document).on('click', '#nerve-error', function () {
        $(this).hide();
    });


    /// Element Widgets ///

    NerveButton.ready();

    NerveDisplayToggle.ready();

    NerveDialogOpen.ready();

    Nerve.attachWidgets(document);

});



