(function ($) {
     function esc(str) {
        return $("<div/>").text(str).html();
    }

     function formatTimestamp(date){
         var t = date;
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
         this.logs = [];
         this.logSize = 20;
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
         addLog : function (timestamp, htmlMessage) {
             timestamp = timestamp || new Date();

             // order by timestamp DESC
             var shouldInsertAfter = null;
             for (var i = 0; i < this.logs.length; i++) {
                 if (timestamp > this.logs[i].timestamp) break;
                 shouldInsertAfter = i;
             }

             var id = "log-" + timestamp.getTime() + "-" + 
                      Math.floor(Math.random() * 1000);
             var timestampStr = formatTimestamp(timestamp);
             var htmlLog = [
                 '<div id="', id, '">', timestampStr, "<br>", 
                 htmlMessage, "<hr>", "</div>"
             ].join("");
             var elemLog = {
                 timestamp : timestamp,
                 id : id
             };
             if (shouldInsertAfter == null) {
                 // Insert at first (It may be the first log.)
                 $("#logs").prepend(htmlLog);
                 this.logs.unshift(elemLog);
             } else {
                 $("#" + this.logs[shouldInsertAfter].id).after(htmlLog);
                 this.logs.splice(shouldInsertAfter + 1, 0, elemLog);
             }

             while (this.logs.length > this.logSize) { (function (log) {
                 $("#" + log.id).remove();
             })(this.logs.pop()); }
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
                     var timestamp = new Date(data.timestamp);

                     if (data.from == null) {
                         self.addLog(timestamp, [
                             '<span style="color: #ff0;">', 
                             esc(data.content), 
                             "</span>"
                         ].join(''));
                     } else {
                         self.addLog(timestamp, [
                             '<span style="font-weight: bold;">', 
                             esc(data.from), 
                             "</span>&gt;", esc(data.content)
                         ].join(''));
                     }
                 } else if (data.event == "closed") {
                     self.addLog(timestamp, [
                         '<span  class="error">closed connection(', 
                         esc(data.reason) , 
                         ")</span>"
                     ].join(''));
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
