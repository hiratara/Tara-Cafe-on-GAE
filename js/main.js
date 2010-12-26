jQuery(function ($) {
    $.post("/get_token", function (got) {
        var channel = new goog.appengine.Channel(got.token);
        var socket = channel.open();
        socket.onopen = function () {
            setInterval(function () {
                $.post("/ping", {id : got.clientID}); 
            }, 1000 * 60);
        };
        socket.onmessage = function (m) {alert("message" + m.data);};
        socket.onerror = function () {alert("error");};
        socket.onclose = function () {alert("closed");};
    }, "json");
});
