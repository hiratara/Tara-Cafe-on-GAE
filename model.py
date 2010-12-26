# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Member(db.Model):
    date      = db.DateTimeProperty(auto_now_add=True)

    def client_id(self):
        return str(self.key())
