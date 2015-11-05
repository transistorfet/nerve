
$(document).ready(function ()
{

    function pack_form_data(form) {
        var data = { };

        $(form).find('ul.nerve-form-tree').each(function () {
            if ($(this).is(':visible') && $(this).attr('name'))
                pack_form_value(data, $(this).attr('name'), ($(this).hasClass('list')) ? [ ] : { });
        });

        $(form).find('.nerve-form-item input[type!="checkbox"],textarea').each(function () {
            if ($(this).is(':visible') || $(this).is('[type="hidden"]'))
                pack_form_value(data, $(this).attr('name'), $(this).val());
        });

        $(form).find('.nerve-form-item select').each(function () {
            if ($(this).is(':visible'))
                pack_form_value(data, $(this).attr('name'), $(this).val());
        });

        $(form).find('.nerve-form-item input[type="checkbox"]').each(function () {
            if ($(this).is(':visible'))
                pack_form_value(data, $(this).attr('name'), $(this).is(':checked') ? true : false);
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

    $('.nerve-form-submit').click(function (e) {
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
                if (response.status == 'success') {
                    if (submitback == 'true')
                        window.history.back();
                    $('#nerve-error').hide();
                    $('#nerve-notice').html("Saved successfully").show();
                }
                else {
                    $('#nerve-notice').hide();
                    $('#nerve-error').html(response.message).show();
                }
            }
        });
    });


    function rename_form_item(item, base, oldname, newname) {
        var fulloldname = base.join('/') + '/' + oldname;
        var fullnewname = base.join('/') + '/' + newname;

        $(item).attr('name', $(item).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));

        $(item).find('> input[type="checkbox"]').each(function () {
            $(this).attr('id', $(this).attr('id').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        $(item).find('> label.nerve-treeview').each(function () {
            $(this).attr('for', $(this).attr('for').replace(new RegExp('^' + fulloldname), fullnewname));
            $(this).find('> span').html(newname);
        });

        $(item).find('> .nerve-form-item > label').each(function () {
            $(this).html(newname);
        });

        $(item).find('.nerve-form-item input[type="text"],textarea').each(function () {
            $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        $(item).find('.nerve-form-item select').each(function () {
            $(this).attr('name', $(this).attr('name').replace(new RegExp('^' + fulloldname), fullnewname));
        });

        $(item).find('.nerve-form-item input[type="checkbox"]').each(function () {
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
                if (response.status == 'success') {
                    $('#nerve-error').hide();
                    $('#nerve-notice').hide();
                    location.reload();
                }
                else {
                    $('#nerve-notice').hide();
                    $('#nerve-error').html(response.message).show();
                }
            }, 'json');
        }
    });

    $('.nerve-config-delete').click(function (e) {
        if (confirm("Are you sure you want to delete " + this.name + "?")) {
            $.post('/config/delete', { 'objectname' : $(this).attr('name') }, function (response) {
                if (response.status == 'success') {
                    $('#nerve-error').hide();
                    $('#nerve-notice').hide();
                    location.reload();
                }
                else {
                    $('#nerve-notice').hide();
                    $('#nerve-error').html(response.message).show();
                }
            }, 'json');
        }
    });
});

 