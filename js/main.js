(function ($) {
     var Room = function (room_id) {
         this.room_id = room_id;
     };
     Room.prototype = {
         run : function () {
            var room_id = this.room_id;

            $.post(room_id + "/get_token", function (got) {
                var channel = new goog.appengine.Channel(got.token);
                var socket = channel.open();
                socket.onopen = function () {
                    setInterval(function () {
                        $.post(room_id + "/ping", {id : got.clientID}); 
                    }, 1000 * 60);
                };
                socket.onmessage = function (m) {
                    $("#logs").prepend("<div>" + m.data + "</div>");
                };
                socket.onerror = function () {alert("error");};
                socket.onclose = function () {alert("closed");};
            }, "json");

            $("#say").submit(function (e) {
                $.post(room_id + "/say", {saying : $("#saying").val()}); 
                $("#saying").val('');
                return false;
            });
         }
     };

     window.taracafe = {};
     window.taracafe.Room = Room;
})(jQuery);
