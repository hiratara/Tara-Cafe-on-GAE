from google.appengine.ext import webapp
import google.appengine.ext.webapp.util
from google.appengine.api import channel
import model

class CleanMembers(webapp.RequestHandler):
    def notify_all(self, room, message):
        for member in model.Member.all().ancestor(room):
            try:
                channel.send_message(member.client_id(), message)
            except channel.InvalidChannelClientIdError:
                pass  # may be an expired client ID.

    def get(self):
        import datetime
        that_time = datetime.datetime.now() \
                    + datetime.timedelta(seconds=-60 * 3)
        for member in model.Member.all().filter('date <', that_time):
            deleting_id = member.client_id()
            room = member.parent()
            member.delete()

            self.notify_all(room, "Deleted %s." % deleting_id)

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
