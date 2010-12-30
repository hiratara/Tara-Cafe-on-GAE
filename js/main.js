(function ($) {
     function esc(str) {
        return $("<div/>").text(str).html();
    }

     var Room = function (room_id) {
         this.room_id = room_id;
         this.onopen = function () {};
     };
     Room.prototype = {
         setNickname : function (nickname) {
             $.post(
                 this.room_id + "/set_name", 
                 {nickname : nickname}
             ); 
         },
         updateMemberList : function () {
            $.post(this.room_id + "/get_members", function (members) {
                members = $.map(members, function (m) { return esc(m.name); });
                $("#members").html(members.join("、"));
            }, "json");
         },
         run : function () {
            var self = this;
            var room_id = this.room_id;

            $.post(room_id + "/get_token", function (got) {
                var channel = new goog.appengine.Channel(got.token);
                var socket = channel.open();
                socket.onopen = function () {
                    setInterval(function () {
                        $.post(room_id + "/ping", {id : got.clientID}); 
                    }, 1000 * 60);

                    self.onopen();
                };
                socket.onmessage = function (m) {
                    var data = $.parseJSON(m.data);
                    if (data.event == "said") {
                        $("#logs").prepend([
                            "<div>",
                            "<span>", esc(data.from), ": </span>",
                            "<span>", esc(data.content), "</span>",
                            "</div>"
                        ].join(""));
                    } else if (data.event == "closed") {
                        $("#logs").prepend([
                            '<div class="error">',
                            "<span>closed connection(", 
                            esc(data.reason) , 
                            ")</span>",
                            "</div>"
                        ].join(""));
                    } else if (data.event == "member_changed") {
                        self.updateMemberList();
                    }
                };
                socket.onerror = function () {alert("error");};
                socket.onclose = function () {alert("closed");};
            }, "json");

            this.updateMemberList();

            $("#say").submit(function (e) {
                $.post(room_id + "/say", {saying : $("#saying").val()}); 
                $("#saying").val('');
                return false;
            });

             $("#nickname").blur(function () {
                 self.setNickname($(this).val());
             });
         }
     };

     window.taracafe = {};
     window.taracafe.Room = Room;
})(jQuery);
