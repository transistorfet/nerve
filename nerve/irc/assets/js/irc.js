
$(document).ready(function ()
{
    var server = new WebSocket("ws://"+window.location.hostname+":"+window.location.port+"/irc/connect", "IRC");

    server.onmessage = function (event)
    {
        var msg = JSON.parse(event.data);

        if (msg.type == 'output') {
            var scroll = false;
            var terminal = $('#nerve-irc-window');
            if (terminal.scrollTop == terminal.scrollTopMax) scroll = true;
            terminal.append(msg.text);
            terminal.scrollTop = terminal.scrollHeight;
        }
    }

    server.onerror = function (event)
    {
        alert("Connection Lost");
    }

    $('#nerve-irc-input').change(function ()
    {
        var msg = { };
        var text = $(this).val();

        msg.type = 'input';
        msg.text = text
        server.send(JSON.stringify(msg));
        $(this).val('');
    });
});

