jQuery(function ($) {
    var channel = new goog.appengine.Channel(token);
    var socket = channel.open();
    socket.onopen = function () {
        $.post("/opened");
    };
    socket.onmessage = function (m) {alert("message" + m.data);};
    socket.onerror = function () {alert("error");};
    socket.onclose = function () {alert("closed");};
});
