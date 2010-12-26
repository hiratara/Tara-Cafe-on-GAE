# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Member(db.Model):
    date      = db.DateTimeProperty(auto_now_add=True)

    def client_id(self):
        return str(self.key())

    @classmethod
    def clean_members(klass):
        import datetime
        that_time = datetime.datetime.now() \
                    + datetime.timedelta(seconds=-60 * 3)
        return db.delete(Member.all().filter('date <', that_time))
