# -*- coding: utf-8 -*-
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
import google.appengine.ext.webapp.template
import django.utils.simplejson
import model
import login

class MainPage(webapp.RequestHandler):
    @login.openid_required
    def get(self, room_id):
      self.response.out.write(webapp.template.render(
          'index.html', {
              "logout_url" : users.create_logout_url("/"),
              "room_id"    : room_id,
              }
      ))

class GetToken(webapp.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(GetToken, self).__init__(*args, **kwargs)

    def post(self, room_id):
        member = model.Member()
        member.put()

        token = channel.create_channel(member.client_id())
        self.response.out.write(django.utils.simplejson.dumps({
            'token' : token,
            'clientID' : member.client_id(),
            }))

class Say(webapp.RequestHandler):
    def post(self, room_id):
        saying = self.request.get("saying")
        user = users.get_current_user()

        for member in model.Member.all():
            try:
                channel.send_message(member.client_id(), "%s : %s" % (user.nickname(), saying))
            except channel.InvalidChannelClientIdError:
                pass  # may be an expired client ID.

class Pong(webapp.RequestHandler):
    def post(self, room_id):
        import datetime
        client_id = self.request.get('id')
        member = model.Member.by_client_id(client_id)
        member.date = datetime.datetime.now()
        member.put()
        self.response.out.write("PONG\n")

application = webapp.WSGIApplication([
    (r'/room/(\w+)', MainPage), 
    (r'/room/(\w+)/get_token', GetToken),
    (r'/room/(\w+)/ping', Pong),
    (r'/room/(\w+)/say', Say), 
    ], debug=True)

def main():
    webapp.util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
