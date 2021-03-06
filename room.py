# -*- coding: utf-8 -*-
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import google.appengine.ext.webapp.template
import django.utils.simplejson
import model
import service
import login
import gaeutil

class UserBase(object):
    def user_id(self): raise NotImplementedError
    def nickname(self): raise NotImplementedError

class User(UserBase):
    def __init__(self, user):
        self.user = user

    def user_id(self):
        return self.user.federated_identity() or self.user.user_id()

    def nickname(self):
        return self.user.nickname()

class GuestUser(UserBase):
    def __init__(self, guest_id):
        self.guest_id = guest_id

    def user_id(self):
        return self.guest_id

    def nickname(self):
        return self.user_id()

class RoomBase(webapp.RequestHandler):
    def get_user(self):
        user = users.get_current_user()
        if user: 
            return User(user)

        guest_id = gaeutil.get_cookie(self.request, "guest_id")
        if not guest_id:
            import datetime, hashlib
            guest_id = hashlib.sha1("%s %s" % (
                datetime.datetime.now().isoformat(),
                self.request.remote_addr
            )).hexdigest()
            gaeutil.set_cookie(self.response, "guest_id", guest_id)

        return GuestUser(guest_id)

class MainPage(RoomBase):
    def get(self, room_id):
        room = model.Room.get_by_key_name(room_id)

        self.response.out.write(webapp.template.render(
            'name_form.html', {"room" : room}
        ))

    def post(self, room_id):
        nickname = self.request.get("nickname", None)
        if not nickname:
            self.redirect(self.request.url)  # redirect by GET
            return

        room = model.Room.get_by_key_name(room_id)
        if not room:
            self.redirect(self.request.relative_url('', True))
            return

        self.response.out.write(webapp.template.render(
            'room.html', {
                "room_id"    : room.key().name(),
                "nickname"   : nickname,
            }
        ))

class GetToken(RoomBase):
    def __init__(self, *args, **kwargs):
        super(GetToken, self).__init__(*args, **kwargs)

    def post(self, room_id):
        room = model.Room.get_by_key_name(room_id)
        user = self.get_user()

        room_service = service.RoomService(room)
        connection = room_service.connect(user)

        self.response.out.write(django.utils.simplejson.dumps({
            'token' : connection.current_token,
            'clientID' : connection.client_id,
            }))

class SendRecentLogs(RoomBase):
    def post(self, room_id):
        room = model.Room.get_by_key_name(room_id)
        user = self.get_user()

        room_service = service.RoomService(room)
        room_service.send_recent_events(
            user, count=int(self.request.get("count"))
        )

        self.response.out.write("OK\n")

class SetName(RoomBase):
    def post(self, room_id):
        room = model.Room.get_by_key_name(room_id)
        user = self.get_user()

        room_service = service.RoomService(room)
        room_service.set_name(user, self.request.get("nickname"))

        self.response.out.write("OK\n")

class GetMembers(RoomBase):
    def post(self, room_id):
        room = model.Room.get_by_key_name(room_id)
        room_service = service.RoomService(room)

        connections = []
        for connection in room_service.get_connections():
            connections.append({"name" : connection.get_name()})

        self.response.out.write(django.utils.simplejson.dumps(connections))

class Say(RoomBase):
    def post(self, room_id):
        room = model.Room.get_by_key_name(room_id)

        saying = self.request.get("saying")
        user = self.get_user()

        room_service = service.RoomService(room)
        room_service.say(user, saying)

class Pong(RoomBase):
    def post(self, room_id):
        room = model.Room.get_by_key_name(room_id)
        user = self.get_user()

        room_service = service.RoomService(room)
        room_service.ping_from(user)

        self.response.out.write("PONG\n")

class ExitPage(RoomBase):
    def get(self, room_id):
        room = model.Room.get_by_key_name(room_id)
        user = self.get_user()

        connection = model.RoomConnection.get_by_room_and_user(room, user)
        exited_nick = connection.get_name()

        service.close_connection(connection)

        self.response.out.write(webapp.template.render(
            'exit.html', {"nickname" : exited_nick}
        ))

application = webapp.WSGIApplication([
    (r'/room/(\w+)', MainPage), 
    (r'/room/(\w+)/get_token', GetToken),
    (r'/room/(\w+)/request_recent_logs', SendRecentLogs),
    (r'/room/(\w+)/set_name', SetName),
    (r'/room/(\w+)/get_members', GetMembers),
    (r'/room/(\w+)/ping', Pong),
    (r'/room/(\w+)/say', Say), 
    (r'/room/(\w+)/exit', ExitPage), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
