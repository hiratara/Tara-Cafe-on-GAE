# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Room(db.Model):
    """
    key_name - Room name.
    parent   - None
    """
    pass

class Member(db.Model):
    """
    key_name - user_id
    parent   - Room
    """
    client_id = db.StringProperty()  # Unique key. (room + user + time)
    nickname = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    def get_name(self):
        return self.nickname or self.key().name()

    @classmethod
    def by_client_id(klass, client_id):
        return klass.all().filter("client_id =", client_id).get()

    @classmethod
    def get_by_room_and_user(klass, room, user):
        return klass.get_by_key_name(
            user.user_id(),
            parent=room,
        )
