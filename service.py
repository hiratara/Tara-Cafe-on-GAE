# -*- coding: utf-8 -*-
from google.appengine.ext import db
import model
from google.appengine.api import channel
import django.utils.simplejson
import datetime
import hashlib

def delete_member(member, force=False):
    name = member.get_name()
    room = member.parent()
    member.delete()

    room_service = RoomService(room)
    if force: 
        room_service.say(None, u"%sさんは、もういないようです。" % name)
    else:
        room_service.say(None, u"%sさんが退室されました。" % name)

    room_service.notify_all({"event" : "member_changed"})

class RoomService(object):
    def __init__(self, room):
        self.room = room

    def new_client_id_for(self, user):
        seed = user.user_id() + ' ' + datetime.datetime.now().isoformat()
        return hashlib.sha1(seed).hexdigest()

    def connect(self, user):
        def needs_transaction():
            client_id = self.new_client_id_for(user)
            token = channel.create_channel(client_id)

            current_member = model.Member.get_by_key_name(
                user.user_id(),
                parent=self.room,
            )

            if current_member:
                channel.send_message(
                    current_member.client_id, 
                    '{"event": "closed", "reason": "duplicated"}'
                )
                current_member.client_id = client_id
                current_member.put()

                member = current_member
            else:
                new_member = model.Member(
                    parent=self.room, key_name=user.user_id(),
                    client_id=client_id,
                )
                new_member.put()

                member = new_member
                # Don't notify until set_name finished
                # with current (broken) protocol.
                # self.notify_all({"event" : "member_changed"})

            return member, token

        member, token = db.run_in_transaction(needs_transaction)

        return member, token

    def get_members(self):
        # dont return iter
        members = list(model.Member.all().ancestor(self.room))
        return members

    def notify_all(self, event):
        event_json = django.utils.simplejson.dumps(event)

        for member in self.get_members():
            try:
                channel.send_message(
                    member.client_id, 
                    event_json
                )
            except channel.InvalidChannelClientIdError:
                pass  # may be an expired client ID.

    def say(self, user, saying):
        nickname = '[System]'
        if user:
            member = model.Member.get_by_key_name(
                user.user_id(),
                parent=self.room,
            )
            nickname = member.get_name()

        self.notify_all({
            "event"  : "said",
            "from"   : nickname,
            "content" : saying
        })

    def set_name(self, user, new_name):
        member = model.Member.get_by_key_name(
            user.user_id(),
            parent=self.room,
        )
        old_name = member.nickname
        member.nickname = new_name
        member.put()

        if old_name:
            if old_name != new_name:
                self.say(
                    None, 
                    u"%sさんは%sさんと名前を変えました。" % (old_name, new_name)
                )
        else:
            # XXX set_name means entering this room 
            #     in current (broken) protocol
            self.say(None, u"%sさんが、いらっしゃいました。" % new_name)

        self.notify_all({"event" : "member_changed"})

    def ping(self, client_id):
        member = model.Member.by_client_id(client_id)
        member.date = datetime.datetime.now()
        member.put()

