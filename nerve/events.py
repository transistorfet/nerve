#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import re
import time


_event_listeners = { }
allowed_subscribe = re.compile(r"^([^/#]+)(|/[+]|/[^/$#]+)*(|/#)*$")        # this doesn't allow '#' on its own
allowed_publish = re.compile(r"^([^/#]+)(|/[^/$#]+)*$")

def subscribe(topic, action, label='', **eventmask):
    if not allowed_subscribe.match(topic):
        raise Exception("invalid event topic in subscribe: " + topic)

    cur = _event_listeners
    for part in topic.split('/'):
        if part not in cur:
            cur[part] = { }
        cur = cur[part]

    if '/' not in cur:
        cur['/'] = [ ]
    cur['/'].append( (label, eventmask, action) )

    publish('$SYS/subscribe', subtopic=topic, action=action)


def unsubscribe(topic, action=None, label=''):
    if not allowed_subscribe.match(topic):
        raise Exception("invalid event topic in unsubscribe: " + topic)

    publish('$SYS/unsubscribe', subtopic=topic, action=action)

    parts = topic.split('/')
    levels = [ _event_listeners ]
    for part in parts:
        if part not in levels[-1]:
            return False
        levels.append(levels[-1][part])

    if '/' not in levels[-1]:
        return False
    for i in range(0, len(levels[-1]['/'])):
        (listlabel, eventmask, callback) = levels[-1]['/'][i]
        if (label and listlabel == label) or (action and action == callback):
            del levels[-1]['/'][i]
            # TODO you should probably delete all entries instead of just one
            break

    if len(levels[-1]['/']) <= 0:
        del levels[-1]['/']
    for i in range(len(levels) - 1, -1, -1):
        if len(levels[i]) <= 0 and i >= 1:
            del levels[i - 1][parts[i - 1]]


def publish(topic, **event):
    if not allowed_publish.match(topic):
        raise Exception("invalid event topic in publish: " + topic)

    # TODO what about retaining the value?  This would require necessary branches to be filled out just so you can store the value somewhere, but it
    #      shouldn't be stored on the individual handlers; this kinda isn't the right datastructure to do it with
    event['topic'] = topic
    nerve.log("routing event " + repr(event), logtype='event')
    _route_event(event, topic, _event_listeners)


def _route_event(event, topic, tree):
    if not topic:
        if '/' in tree:
            _dispatch_event(event, tree['/'])
        return

    (part, _, topic_remain) = topic.partition('/')
    if part in tree:
        _route_event(event, topic_remain, tree[part])
    if '+' in tree and not part.startswith('$'):
        _route_event(event, topic_remain, tree['+'])

    if '#' in tree and not part.startswith('$'):
        _dispatch_event(event, tree['#']['/'])


def _dispatch_event(event, listeners):
    for (label, eventmask, action) in listeners:
        if _check_eventmask(event, eventmask):
            action(event)


def _check_eventmask(event, eventmask):
    for (key, value) in eventmask.items():
        if key not in event:
            return False
        if hasattr(value, 'search'):
            try:
                if not value.search(event[key]):
                    return False
            except:
                return False
        elif value == event[key]:
            return False
    return True



class EventRouter (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)

    def subscribe(self, topic, action, label='', **eventmask):
        return subscribe(topic, action, label, **eventmask)
        
    def unsubscribe(self, topic, action=None, label=''):
        return unsubscribe(topic, action, label)

    def publish(self, topic, **event):
        return publish(topic, **event)


class EventListener (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)
        subscribe(self.get_setting('topic'), action=self, **self.get_setting('eventmask'))

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('topic', "Topic", default='')
        config_info.add_setting('eventmask', "Event Mask", default=dict(), itemtype='str')
        return config_info

    def __call__(self, event):
        self.query('*', event)


