import model
from google.appengine.api import channel

class RoomService(object):
    def __init__(self, room):
        self.room = room

    def connect(self):
        member = model.Member(parent=self.room)
        member.put()

        token = channel.create_channel(member.client_id())

        return member, token

    def say(self, user, saying):
        nickname = '[System]'
        if user: nickname = user.nickname()

        for member in model.Member.all().ancestor(self.room):
            try:
                channel.send_message(
                    member.client_id(), 
                    "%s : %s" % (nickname, saying)
                )
            except channel.InvalidChannelClientIdError:
                pass  # may be an expired client ID.

    def ping(self, client_id):
        import datetime
        member = model.Member.by_client_id(client_id)
        member.date = datetime.datetime.now()
        member.put()

