# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Room(db.Model): pass

class Member(db.Model):
    client_id = db.StringProperty()
    nickname = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    def get_name(self):
        return self.nickname or self.key().name()

    @classmethod
    def by_client_id(klass, client_id):
        return klass.all().filter("client_id =", client_id)
