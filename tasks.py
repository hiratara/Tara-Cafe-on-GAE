# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
from google.appengine.api import channel
import service
import model

class CleanMembers(webapp.RequestHandler):
    def get(self):
        import datetime
        that_time = datetime.datetime.now() \
                    + datetime.timedelta(seconds=-60 * 3)
        for connection in model.RoomConnection.all().filter('date <', that_time):
            service.close_connection(connection, force=True)

        self.response.out.write("Deleted.\n")

class AddRoom(webapp.RequestHandler):
    def get(self, room_id):
        model.Room(key_name=room_id).put()
        self.response.out.write("Added %s." % room_id)

application = webapp.WSGIApplication([
    (r'/tasks/clean_members', CleanMembers),
    (r'/tasks/add_room/(\w+)', AddRoom),
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
