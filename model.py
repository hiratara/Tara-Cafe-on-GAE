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
    current_token = db.StringProperty()
    nickname = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    def get_name(self):
        return self.nickname or self.key().name()

    @classmethod
    def get_by_room_and_user(klass, room, user):
        return klass.get_by_key_name(
            user.user_id(),
            parent=room,
        )

class Log(db.Model):
    room = db.ReferenceProperty(Room)
    user_id = db.StringProperty() # From Member class's key_name
    client_id = db.StringProperty() # From Member class
    nickname = db.StringProperty() # From Member class
    content = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
