# -*- coding: utf-8 -*-
from google.appengine.api import channel
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import google.appengine.ext.webapp.template
import django.utils.simplejson
import model

class MainPage(webapp.RequestHandler):
    def get(self):
      self.response.out.write(webapp.template.render(
          'index.html', None
      ))

class GetToken(webapp.RequestHandler):
    sequence = 0

    def __init__(self, *args, **kwargs):
        super(GetToken, self).__init__(*args, **kwargs)

    def post(self):
        GetToken.sequence += 1

        member = model.Member()
        member.client_id = unicode(GetToken.sequence)
        member.put()

        import logging
        logging.debug(member.client_id)

        token = channel.create_channel(member.client_id)
        self.response.out.write(django.utils.simplejson.dumps({
            'token' : token
            }))

class OpenedPage(webapp.RequestHandler):
    def post(self):
        for member in model.Member.all():
            channel.send_message(member.client_id, "an message")

def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ["Hello world!\n"]

application = webapp.WSGIApplication([
    ('/', MainPage), 
    ('/get_token', GetToken),
    ('/opened', OpenedPage), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
