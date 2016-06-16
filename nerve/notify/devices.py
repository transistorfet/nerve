#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import time


class NotifyDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.next_id = 1
        self.notifications = [ ]

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('forwards', "Forward Actions", default=[], itemtype='str')
        return config_info


    def get_child(self, index):
        nid = int(index)
        for note in self.notifications:
            if note['id'] == nid:
                return note
        super().get_child(index)

    def keys_children(self):
        return sorted([ str(note['id']) for note in self.notifications ]) + super().keys_children()

    # TODO we actually don't need this because we never create and store objects in the _children dict.  This only prevents children from being added to this object
    #def set_child(self, index, obj):
    #    pass

    #def del_child(self, index):
    #    return False

    # TODO this isn't needed at all because if the above two methods are used, there wont be children to save in the first place.  This would only be for when there are
    #      child objects that you don't want to persist across restarts
    #def save_object_children(self):
    #    return { }


    def count(self):
        count = 0
        for note in self.notifications:
            if not note['acknowledged']:
                count += 1
        return count

    def list(self):
        return list(self.notifications)

    def add(self, message, severity='info'):
        nid = self.next_id
        self.next_id += 1

        self.notifications.insert(0, {
            'id': nid,
            'timestamp': time.time(),
            'acknowledged': False,
            'severity': severity,
            'message': message
        })
        self.forward(self.notifications[0])
        return nid

    def acknowledge(self, nid=-1):
        nid = int(nid)
        for note in self.notifications:
            if nid == -1 or nid == note['id']:
                note['acknowledged'] = True

    def clear(self, nid=-1):
        nid = int(nid)
        if nid == -1:
            self.notifications = [ ]
            return

        for (i, note) in enumerate(self.notifications):
            if note['id'] == nid:
                del self.notifications[i]
                return

    def forward(self, notification):
        for ref in self.get_setting('forwards'):
            nerve.query(ref, notification)

