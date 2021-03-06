# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import google.appengine.ext.webapp.template
import model
import service
from google.appengine.api import users

class MainPage(webapp.RequestHandler):
    def get(self):
        room_info = []
        for room in model.Room.all():
            room_service = service.RoomService(room)
            connections = room_service.get_connections()
            room_info.append({
                "room"    : room,
                "connections" : connections,
            })

        self.response.out.write(webapp.template.render(
            'index.html', {
                "room_info" : room_info,
                "logout_url" : users.create_logout_url("/"),
            }
        ))

application = webapp.WSGIApplication([
    (r'/', MainPage), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
