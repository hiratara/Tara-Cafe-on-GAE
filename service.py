# -*- coding: utf-8 -*-
from google.appengine.ext import db
import model
from google.appengine.api import channel
import django.utils.simplejson
import datetime
import hashlib
import logging

def close_connection(connection, force=False):
    name = connection.get_name()
    room = connection.parent()
    connection.delete()

    room_service = RoomService(room)
    if force: 
        room_service.say(None, u"%sさんは、もういないようです。" % name)
    else:
        room_service.say(None, u"%sさんが退室されました。" % name)

    room_service.notify_all({"event" : "member_changed"})

def _log_to_event(log):
    """Changes Log's instance into an event.
    """
    return {
        "event" : "said",
        "from" : log.nickname,
        "content" : log.content,
        "timestamp" : log.date.strftime("%d %b, %Y %H:%M:%S GMT"),
    }

def _send_event(client_id, event):
    """Send events to client_id.

       event is a python data structure, which is converted in JSON and sent.
    """
    try:
        channel.send_message(
            client_id, 
            django.utils.simplejson.dumps(event)
        )
    except channel.InvalidChannelClientIdError, e:
        # may be an expired client ID.
        loging.warn(e)

class RoomService(object):
    def __init__(self, room):
        self.room = room

    def new_client_id_for(self, user):
        seed = user.user_id() + ' ' + datetime.datetime.now().isoformat()
        return hashlib.sha1(seed).hexdigest()

    def _send_recent_events(self, client_id):
        """Send events in data store to client_id.

           Some last Log's instances are sent.
        """
        room_logs = model.Log.all().filter("room =", self.room)
        for log in room_logs.order("-date").fetch(20):
            _send_event(client_id, _log_to_event(log))

    def connect(self, user):
        client_id = self.new_client_id_for(user)
        token = channel.create_channel(client_id)

        def needs_transaction():
            cur_conn = model.RoomConnection.get_by_room_and_user(
                self.room, user
            )

            closed_client_id = None
            if cur_conn:
                closed_client_id = cur_conn.client_id
                connection = cur_conn
            else:
                connection = model.RoomConnection(
                    parent=self.room, key_name=user.user_id(),
                )

            connection.client_id = client_id
            connection.current_token = token
            connection.put()

            return connection, closed_client_id

        connection, closed_client_id = db.run_in_transaction(needs_transaction)

        if closed_client_id:
            _send_event(closed_client_id, {
                "event": "closed", "reason": "duplicated"
            })
        else:
            # Don't notify until set_name finished
            # with current (broken) protocol.
            # self.notify_all({"event" : "member_changed"})
            pass

        self._send_recent_events(connection.client_id)

        return connection

    def get_connections(self):
        # dont return iter
        connections = list(model.RoomConnection.all().ancestor(self.room))
        return connections

    def notify_all(self, event):
        for connection in self.get_connections():
            _send_event(connection.client_id, event)

    def say(self, user, saying):
        if user:
            connection = model.RoomConnection.get_by_room_and_user(self.room, user)
            nickname = connection.get_name()
            user_id = connection.key().name()
            client_id = connection.client_id
            nickname = connection.nickname
        else:
            nickname = None
            user_id = None
            client_id = None

        log = model.Log(
            room=self.room,
            user_id=user_id,
            client_id=client_id,
            nickname=nickname,
            content=saying,
        )
        log.put()

        self.notify_all(_log_to_event(log))

    def set_name(self, user, new_name):
        connection = model.RoomConnection.get_by_room_and_user(self.room, user)
        old_name = connection.nickname
        connection.nickname = new_name
        connection.put()

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

    def ping_from(self, user):
        connection = model.RoomConnection.get_by_room_and_user(self.room, user)
        connection.last_time = datetime.datetime.now()
        connection.put()

