#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import re
import time


_event_listeners = { }
allowed_subscribe = re.compile(r"^#$|^([^/#]+)(|/[+]|/[^/$#]+)*(|/#)*$")
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

    publish('$SYS/subscribe', subtopic=topic, label=label, action=action)

    """
    # TODO for debugging
    import json
    def json_default(obj):
        return str(obj)
    print(json.dumps(_event_listeners, sort_keys=True, indent=4, default=json_default))
    """

def unsubscribe(topic=None, action=None, label='', base=_event_listeners):
    if topic and not allowed_subscribe.match(topic):
        raise Exception("invalid event topic in unsubscribe: " + topic)

    publish('$SYS/unsubscribe', subtopic=topic, label=label, action=action)
    return _unsubscribe(topic, action, label, _event_listeners)

    """
    _unsubscribe(topic, action, label, _event_listeners)
    # TODO for debugging
    import json
    def json_default(obj):
        return str(obj)
    print(json.dumps(_event_listeners, sort_keys=True, indent=4, default=json_default))
    """

def _unsubscribe(topic=None, action=None, label='', base=_event_listeners):
    if topic:
        parts = topic.split('/', 1)
        if parts[0] in base:
            return _unsubscribe(parts[1] if len(parts) > 1 else None, action, label, base[parts[0]])
        return 0
    else:
        count = 0
        to_delete = []
        for name in base:
            if name != '/':
                count += _unsubscribe(None, action, label, base[name])
            else:
                i = 0
                while i < len(base['/']):
                    (listlabel, eventmask, callback) = base['/'][i]
                    if (not label or label == listlabel) and (not action or action == callback):
                        del base['/'][i]
                        count += 1
                    else:
                        i += 1

            if len(base[name]) <= 0:
                to_delete.append(name)

        for name in to_delete:
            del base[name]
        return count


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


"""
def thing():
    print("Hey")
subscribe('devices/coolthing', thing, label='doodad')
subscribe('devices/+/stuff', thing, label='crazy')
#unsubscribe_all('', label='doodad')
unsubscribe_all('devices', label='doodad')
unsubscribe_all('', action=thing)
#subscribe('devices/+', thing, label='ended')
"""

