(function ($) {
     function esc(str) {
        return $("<div/>").text(str).html();
    }

     function formatTimestamp(str){
         var t = new Date(str);
         var week_ja = ["日", "月", "火", "水", "木", "金", "土"][t.getDay()];
         return [
             "[", t.getFullYear(), "年 ", (t.getMonth() + 1), "月 ",
             t.getDate(), "日（", week_ja, "曜日） ", 
             t.getHours(), "時 ", t.getMinutes(), "分 ", t.getSeconds(), "秒]"
         ].join("");
     }

     var Room = function (room_id) {
         this.room_id = room_id;
         this.onopen = function () {};
     };
     Room.prototype = {
         setNickname : function (nickname) {
             return $.post(
                 this.room_id + "/set_name", 
                 {nickname : nickname}
             ); 
         },
         updateMemberList : function () {
            $.post(this.room_id + "/get_members", function (members) {
                var member_htmls = $.map(members, function (m) {
                    return [
                        '<span style="white-space: nowrap;">', 
                        esc(m.name), 
                        "</span><br>"
                    ];
                });
                $("#members").html(member_htmls.join(""));
            }, "json");
         },
         openSocket : function () {
             var self = this;
             var channel = new goog.appengine.Channel(this.token);
             var socket = channel.open();
             socket.onopen = function () {
                 setInterval(function () {
                     $.post(self.room_id + "/ping"); 
                 }, 1000 * 60);

                 self.onopen();
             };
             socket.onmessage = function (m) {
                 var data = $.parseJSON(m.data);
                 if (data.event == "said") {
                     var timestamp = formatTimestamp(data.timestamp);

                     if (data.from == "[System]") {
                         $("#logs").prepend([
                             "<div>",
                             timestamp, "<br>",
                             '<span style="color: #ff0;">', 
                             esc(data.content), 
                             "</span>", "<hr>",
                             "</div>"
                         ].join(""));
                     } else {
                         $("#logs").prepend([
                             "<div>",
                             timestamp, "<br>",
                             '<span style="font-weight: bold;">', 
                             esc(data.from), 
                             "</span>&gt;", esc(data.content), "<hr>",
                             "</div>"
                         ].join(""));
                     }
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
         },
         run : function () {
            var self = this;
            var room_id = this.room_id;

            $.post(
                room_id + "/get_token", null, null, "json"
            ).next(function (got) {
                self.token = got.token;
                self.clientID = got.clientID;
                self.openSocket();
            });

            /* Don't update members until /set_name finished 
               with current (broken) protocol. */
            // this.updateMemberList();

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
