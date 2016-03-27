

NerveForm = {
    pack_form_data: function (form)
    {
        var data = { };

        $(form).find('ul.nerve-form-tree').each(function () {
            if ($(this).is(':visible') && $(this).attr('name'))
                NerveForm.pack_form_value(data, $(this).attr('name'), ($(this).hasClass('list')) ? [ ] : { });
        });

        $(form).find('.nerve-form-item input:not([type="checkbox"],[type="radio"],[type="submit"],[type="button"]),select,textarea').each(function () {
            if ($(this).is(':visible') || $(this).is('[type="hidden"]'))
                NerveForm.pack_form_value(data, $(this).attr('name'), $(this).val());
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            if ($(this).is(':visible'))
                NerveForm.pack_form_value(data, $(this).attr('name'), $(this).is(':checked') ? true : false);
        });

        $(form).find('.nerve-form-item input[type="radio"]:checked').each(function () {
            if ($(this).is(':visible'))
                NerveForm.pack_form_value(data, $(this).attr('name'), $(this).val());
        });

        return data;
    },

    pack_form_value: function (data, pathname, value)
    {
        var segments = pathname.split('/');
        var leaf = segments.pop();
        var parent_data = data;
        for (var i = 0; i < segments.length; i++) {
            if (!parent_data[segments[i]]) {
                var next = (i + 1 < segments.length) ? segments[i + 1] : leaf;
                if (!isNaN(parseFloat(next)) && isFinite(next))
                    parent_data[segments[i]] = [ ];
                else
                    parent_data[segments[i]] = { };
            }
            parent_data = parent_data[segments[i]];
        }
        parent_data[leaf] = value;
    },

    submit: function (form)
    {
        var postvars = NerveForm.pack_form_data(form);
        var submitback = $(form).attr('data-back');

        $.ajax({
            method: $(form).attr('method'),
            url: $(form).attr('action'),
            contentType: 'application/json',
            data: JSON.stringify(postvars),
            dataType: 'json',
            success: function (response) {
                if (response.notice) {
                    $(form).trigger('nerve:form:success');
                    if (submitback == 'true')
                        window.history.back();
                    Nerve.set_notice(response.notice);
                }
                else if (response.error) {
                    $(form).trigger('nerve:form:error');
                    Nerve.set_error(response.error);
                }
            }
        });
    },

    rename_form_item: function (item, base, oldname, newname)
    {
        var fulloldname = base.join('/') + '/' + oldname;
        var fullnewname = base.join('/') + '/' + newname;

        $(item).attr('name', $(item).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));

        // change the item label (for single items and structs)
        $(item).find('> label.nerve-form-tree > span').html(newname);
        $(item).find('> .nerve-form-item > label').html(newname);

        // change the id of form-tree headers, and their associated expand/collapse checkbox
        $(item).find('label.nerve-form-tree').each(function () {
            var expand = document.getElementById($(this).attr('for'));
            $(expand).attr('id', $(expand).attr('id').replace(new RegExp('^(e[0-9]*-)' + fulloldname), "$1" + fullnewname));
            $(this).attr('for', $(this).attr('for').replace(new RegExp('^(e[0-9]*-)' + fulloldname), "$1" + fullnewname));
        });

        // change names of all ul form-tree elements, and li elements that are direct children of ul form-trees
        $(item).find('ul.nerve-form-tree, ul.nerve-form-tree > li').each(function () {
            $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        // change names of all input elements, except checkboxes
        $(item).find('.nerve-form-item input:not([type="checkbox"]),select,textarea').each(function () {
            $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        // change names of all checkboxes that are not the direct child of an li (which we assume are expand/collapse checkboxes)
        $(item).find('.nerve-form-item input[type="checkbox"]').each(function () {
            if ($(this).parent().not('li'))
                $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });
    },

    add_item: function (button)
    {
        var item = $($(button).next().html());
        if ($(item).find('.nerve-form-move-up').length) {
            if ($(button).prev().length) {
                var base = $(button).prev().attr('name').split('/');
                var prevname = base.pop();
                var newname = (parseInt(prevname) + 1).toString();
            }
            else {
                var base = $(button).attr('data-name').split('/');
                var newname = '0';
            }
            NerveForm.rename_form_item(item, base, '__new__', newname);
        }
        $(button).before(item);
    },

    delete_item: function (button)
    {
        if (confirm("Are you sure you would like to delete item")) {
            var item = $(button).parent().parent();
            if ($(item).find('.nerve-form-move-up').length) {
                var base = $(item).attr('name').split('/');
                var newname = parseInt(base.pop());
                var nextitem = $(item).next();
                while ($(nextitem).is('li')) {
                    NerveForm.rename_form_item(nextitem, base, $(nextitem).attr('name').split('/').pop(), newname.toString());
                    newname += 1;
                    nextitem = $(nextitem).next();
                }
            }
            $(item).remove();
        }
    },

    rename_item: function (button)
    {
        var item = $(button).parent().parent();
        var base = $(item).attr('name').split('/');
        var oldname = base.pop();

        var newname = prompt("Rename", oldname);
        if (newname)
            NerveForm.rename_form_item(item, base, oldname, newname);
    },

    move_item_up: function (button)
    {
        var item = $(button).parent().parent();
        var previtem = $(item).prev();
        var base = $(item).attr('name').split('/');
        var oldname = base.pop();
        var newname = (parseInt(oldname) - 1).toString();

        if (previtem.length) {
            NerveForm.rename_form_item(item, base, oldname, newname);
            NerveForm.rename_form_item(previtem, base, newname, oldname);
            $(item).detach();
            $(previtem).before(item);
        }
    },

    move_item_down: function (button)
    {
        var item = $(button).parent().parent();
        var nextitem = $(item).next();
        var base = $(item).attr('name').split('/');
        var oldname = base.pop();
        var newname = (parseInt(oldname) + 1).toString();

        if (nextitem.length && nextitem.is('li')) {
            NerveForm.rename_form_item(item, base, oldname, newname);
            NerveForm.rename_form_item(nextitem, base, newname, oldname);
            $(item).detach();
            $(nextitem).after(item);
        }
    },

    change_type: function (button)
    {
        if (!$(button).val())
            return;

        var ul = $(button).parent().parent().parent().parent();
        $.post('/config/defaults', { 'type' : $(button).val(), 'basename' : $(ul).attr('name') }, function (response) {
            $(ul).html($(response).children());
        }, 'html');
    }
}


$(document).ready(function ()
{

    /*
    $('.nerve-form').each(function () {
        new NerveForm(this);
    });
    */

    /*
    $(document).on('nerve:form:success', '.nerve-form', function () {
        console.log("fuck yeah");
    });
    */

    $(document).on('submit', '.nerve-form', function (e) {
        e.preventDefault();
        NerveForm.submit(this);
    });

    //$(document).on('click', '.nerve-form-submit', function (e) {
    //    NerveForm.submit(this.form);
    //});

    $(document).on('click', '.nerve-form-add', function (e) {
        NerveForm.add_item(this);
    });

    $(document).on('click', '.nerve-form-delete', function (e) {
        NerveForm.delete_item(this);
    });

    $(document).on('click', '.nerve-form-rename', function (e) {
        NerveForm.rename_item(this);
    });

    $(document).on('click', '.nerve-form-move-up', function (e) {
        NerveForm.move_item_up(this);
    });

    $(document).on('click', '.nerve-form-move-down', function (e) {
        NerveForm.move_item_down(this);
    });

    $(document).on('change', '.nerve-form-change-type', function (e) {
        NerveForm.change_type(this);
    });


    $('.nerve-config-add').click(function (e) {
        if (this.name[0] == '/')
            window.location = '/config/add' + this.name;
    });

    $('.nerve-config-edit').click(function (e) {
        if (this.name[0] == '/')
            window.location = '/config/edit' + this.name;
    });

    $('.nerve-config-rename').click(function (e) {
        var newname = prompt("Rename", $(this).attr('name'));
        if (newname) {
            $.post('/config/rename', { 'oldname' : $(this).attr('name'), 'newname': newname }, function (response) {
                if (response.notice) {
                    Nerve.clear_notices();
                    location.reload();
                }
                else if (response.error) {
                    Nerve.set_error(response.error);
                }
            }, 'json');
        }
    });

    $('.nerve-config-delete').click(function (e) {
        if (confirm("Are you sure you want to delete " + this.name + "?")) {
            $.post('/config/delete', { 'objectname' : $(this).attr('name') }, function (response) {
                if (response.status == 'success') {
                    Nerve.clear_notices();
                    location.reload();
                }
                else if (response.error) {
                    Nerve.set_error(response.error);
                }
            }, 'json');
        }
    });
});


/* 
$(document).ready(function ()
{

    function pack_form_data(form) {
        var data = { };

        $(form).find('ul.nerve-form-tree').each(function () {
            if ($(this).is(':visible') && $(this).attr('name'))
                pack_form_value(data, $(this).attr('name'), ($(this).hasClass('list')) ? [ ] : { });
        });

        $(form).find('.nerve-form-item input:not([type="checkbox"],[type="radio"],[type="submit"],[type="button"]),select,textarea').each(function () {
            if ($(this).is(':visible') || $(this).is('[type="hidden"]'))
                pack_form_value(data, $(this).attr('name'), $(this).val());
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            if ($(this).is(':visible'))
                pack_form_value(data, $(this).attr('name'), $(this).is(':checked') ? true : false);
        });

        $(form).find('.nerve-form-item input[type="radio"]:checked').each(function () {
            if ($(this).is(':visible'))
                pack_form_value(data, $(this).attr('name'), $(this).val());
        });

        return data;
    }

    function pack_form_value(data, pathname, value) {
        var segments = pathname.split('/');
        var leaf = segments.pop();
        var parent_data = data;
        for (var i = 0; i < segments.length; i++) {
            if (!parent_data[segments[i]]) {
                var next = (i + 1 < segments.length) ? segments[i + 1] : leaf;
                if (!isNaN(parseFloat(next)) && isFinite(next))
                    parent_data[segments[i]] = [ ];
                else
                    parent_data[segments[i]] = { };
            }
            parent_data = parent_data[segments[i]];
        }
        parent_data[leaf] = value;
    }

    $(document).on('submit', 'form.nerve-form', function (e) {
        e.preventDefault();
    });

    $(document).on('click', '.nerve-form-submit', function (e) {
        var form = $(this).parent().children('.nerve-form-tree');
        var postvars = pack_form_data(form);
        var submitback = $(this).attr('data-back');

        $.ajax({
            method: 'POST',
            url: $(this).attr('data-target'),
            contentType: 'application/json',
            data: JSON.stringify(postvars),
            dataType: 'json',
            success: function (response) {
                if (response.notice) {
                    if (submitback == 'true')
                        window.history.back();
                    Nerve.set_notice(response.notice);
                }
                else if (response.error) {
                    Nerve.set_error(response.error);
                }
            }
        });
    });


    function rename_form_item(item, base, oldname, newname) {
        var fulloldname = base.join('/') + '/' + oldname;
        var fullnewname = base.join('/') + '/' + newname;

        $(item).attr('name', $(item).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));

        // change the item label (for single items and structs)
        $(item).find('> label.nerve-form-tree > span').html(newname);
        $(item).find('> .nerve-form-item > label').html(newname);

        // change the id of form-tree headers, and their associated expand/collapse checkbox
        $(item).find('label.nerve-form-tree').each(function () {
            var expand = document.getElementById($(this).attr('for'));
            $(expand).attr('id', $(expand).attr('id').replace(new RegExp('^(e[0-9]*-)' + fulloldname), "$1" + fullnewname));
            $(this).attr('for', $(this).attr('for').replace(new RegExp('^(e[0-9]*-)' + fulloldname), "$1" + fullnewname));
        });

        // change names of all ul form-tree elements, and li elements that are direct children of ul form-trees
        $(item).find('ul.nerve-form-tree, ul.nerve-form-tree > li').each(function () {
            $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        // change names of all input elements, except checkboxes
        $(item).find('.nerve-form-item input:not([type="checkbox"]),select,textarea').each(function () {
            $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        // change names of all checkboxes that are not the direct child of an li (which we assume are expand/collapse checkboxes)
        $(item).find('.nerve-form-item input[type="checkbox"]').each(function () {
            if ($(this).parent().not('li'))
                $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });
    }

    $(document).on('click', '.nerve-form-add', function (e) {
        var item = $($(this).next().html());
        if ($(item).find('.nerve-form-move-up').length) {
            if ($(this).prev().length) {
                var base = $(this).prev().attr('name').split('/');
                var prevname = base.pop();
                var newname = (parseInt(prevname) + 1).toString();
            }
            else {
                var base = $(this).attr('data-name').split('/');
                var newname = '0';
            }
            rename_form_item(item, base, '__new__', newname);
        }
        $(this).before(item);
    });

    $(document).on('click', '.nerve-form-delete', function (e) {
        if (confirm("Are you sure you would like to delete item")) {
            var item = $(this).parent().parent();
            if ($(item).find('.nerve-form-move-up').length) {
                var base = $(item).attr('name').split('/');
                var newname = parseInt(base.pop());
                var nextitem = $(item).next();
                while ($(nextitem).is('li')) {
                    rename_form_item(nextitem, base, $(nextitem).attr('name').split('/').pop(), newname.toString());
                    newname += 1;
                    nextitem = $(nextitem).next();
                }
            }
            $(item).remove();
        }
    });

    $(document).on('click', '.nerve-form-rename', function (e) {
        var item = $(this).parent().parent();
        var base = $(item).attr('name').split('/');
        var oldname = base.pop();

        var newname = prompt("Rename", oldname);
        if (newname)
            rename_form_item(item, base, oldname, newname);
    });

    $(document).on('click', '.nerve-form-move-up', function (e) {
        var item = $(this).parent().parent();
        var previtem = $(item).prev();
        var base = $(item).attr('name').split('/');
        var oldname = base.pop();
        var newname = (parseInt(oldname) - 1).toString();

        if (previtem.length) {
            rename_form_item(item, base, oldname, newname);
            rename_form_item(previtem, base, newname, oldname);
            $(item).detach();
            $(previtem).before(item);
        }
    });

    $(document).on('click', '.nerve-form-move-down', function (e) {
        var item = $(this).parent().parent();
        var nextitem = $(item).next();
        var base = $(item).attr('name').split('/');
        var oldname = base.pop();
        var newname = (parseInt(oldname) + 1).toString();

        if (nextitem.length && nextitem.is('li')) {
            rename_form_item(item, base, oldname, newname);
            rename_form_item(nextitem, base, newname, oldname);
            $(item).detach();
            $(nextitem).after(item);
        }
    });

    $(document).on('change', '.nerve-form-change-type', function (e) {
        if (!$(this).val())
            return;

        var ul = $(this).parent().parent().parent().parent();
        $.post('/config/defaults', { 'type' : $(this).val(), 'basename' : $(ul).attr('name') }, function (response) {
            $(ul).html($(response).children());
        }, 'html');
    });


    $('.nerve-config-add').click(function (e) {
        if (this.name[0] == '/')
            window.location = '/config/add' + this.name;
    });

    $('.nerve-config-edit').click(function (e) {
        if (this.name[0] == '/')
            window.location = '/config/edit' + this.name;
    });

    $('.nerve-config-rename').click(function (e) {
        var newname = prompt("Rename", $(this).attr('name'));
        if (newname) {
            $.post('/config/rename', { 'oldname' : $(this).attr('name'), 'newname': newname }, function (response) {
                if (response.notice) {
                    Nerve.clear_notices();
                    location.reload();
                }
                else if (response.error) {
                    Nerve.set_error(response.error);
                }
            }, 'json');
        }
    });

    $('.nerve-config-delete').click(function (e) {
        if (confirm("Are you sure you want to delete " + this.name + "?")) {
            $.post('/config/delete', { 'objectname' : $(this).attr('name') }, function (response) {
                if (response.status == 'success') {
                    Nerve.clear_notices();
                    location.reload();
                }
                else if (response.error) {
                    Nerve.set_error(response.error);
                }
            }, 'json');
        }
    });
});
*/


