# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Room(db.Model): pass

class Member(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)

    def client_id(self):
        return str(self.key())

    @classmethod
    def by_client_id(klass, client_id):
        return klass.get(client_id)
