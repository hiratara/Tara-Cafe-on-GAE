# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import google.appengine.ext.webapp.template
import model

class MainPage(webapp.RequestHandler):
    def get(self):
        rooms = model.Room.all()

        self.response.out.write(webapp.template.render(
            'index.html', {
                "rooms" : rooms
            }
        ))

application = webapp.WSGIApplication([
    (r'/', MainPage), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
