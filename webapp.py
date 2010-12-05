# -*- coding: utf-8 -*-
from google.appengine.api import channel
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import google.appengine.ext.webapp.template

class MainPage(webapp.RequestHandler):
    def get(self):
      token = channel.create_channel("ThisIsMyKey")
      self.response.out.write(webapp.template.render(
              'index.html', {'token': token}
              ))

class OpenedPage(webapp.RequestHandler):
    def post(self):
      channel.send_message("ThisIsMyKey", "an message")

def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ["Hello world!\n"]

application = webapp.WSGIApplication([
    ('/', MainPage), 
    ('/opened', OpenedPage), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
