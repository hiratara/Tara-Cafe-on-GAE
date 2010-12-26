# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Member(db.Model):
    client_id = db.StringProperty()
    date      = db.DateTimeProperty(auto_now_add=True)
