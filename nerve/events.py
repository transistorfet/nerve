#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import re
import time


class EventRouter (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)

    def subscribe(self, action, **kwargs):
        eventmask = kwargs
        #self._event_listeners.append( (eventmask, action) )
        listener = EventListener(eventmask=kwargs)
        print(listener)
        
    def unsubscribe(self, eid):
        pass

    def publish(self, type, **kwargs):
        return publish(type, **kwargs)


def publish(type, **kwargs):
    event = kwargs
    event['type'] = type

    nerve.log("routing event " + repr(event), logtype='event')
    for listener in EventListener._event_listeners:
        listener(event) 


class EventListener (nerve.ObjectNode):
    _event_listeners = [ ]

    def __init__(self, **config):
        super().__init__(**config)
        self._event_listeners.append(self)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('eventmask', "Event Mask", default=dict(), itemtype='str')
        return config_info

    def check(self, event):
        for (key, value) in self.get_setting('eventmask').items():
            if not re.search(value, event[key]):
                return False
        return True

    def __call__(self, event):
        if self.check(event):
            self.query('*', event)


