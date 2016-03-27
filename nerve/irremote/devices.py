#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import json


class IRRemoteDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.db = nerve.Database('irremote.sqlite')
        self.db.create_table('remotenames', "id INTEGER PRIMARY KEY, remote_name TEXT UNIQUE")
        self.db.create_table('codenames', "id INTEGER PRIMARY KEY, code TEXT UNIQUE, remote_name TEXT, button_name TEXT")
        self.db.create_table('events', "id INTEGER PRIMARY KEY, code TEXT UNIQUE, object TEXT")

        self.code_history = [ ]
        self.program_mode = False

        self.db.select("code,object")
        for row in self.db.get('events'):
            config = json.loads(row[1])
            self.set_object(row[0], nerve.objects.Module.make_object(config['__type__'], config))

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('max_history', "Max Code History", default=20)
        return config_info

    def get_remote_names(self):
        self.db.select('remote_name')
        self.db.order_by('remote_name')
        return [ row[0] for row in self.db.get('remotenames') ]

    def add_remote(self, name):
        self.db.select('id,remote_name')
        self.db.where('remote_name', name)
        if len(list(self.db.get('remotenames'))) > 0:
            return False
        self.db.insert('remotenames', { 'remote_name': name })
        return True

    def remove_remote(self, name):
        self.db.select('code')
        self.db.where('remote_name', name)
        for row in self.db.get('codenames'):
            self.db.where('code', row[0])
            self.db.delete('events')

        self.db.where('remote_name', name)
        self.db.delete('remotenames')

        self.db.where('remote_name', name)
        self.db.delete('codenames')


    def get_saved_codes(self, remote_name):
        self.db.select('code,remote_name,button_name')
        self.db.where('remote_name', remote_name)
        #self.db.order_by('code')
        self.db.order_by('button_name')
        return list(self.db.get('codenames'))

    def delete_code(self, code):
        self.db.where('code', code)
        self.db.delete('events')

        self.db.where('code', code)
        self.db.delete('codenames')

    def get_recent_codes(self, last_update=0, wait=0):
        while not nerve.Task.quit:
            if wait <= 0 or (len(self.code_history) > 0 and self.code_history[0][0] > last_update):
                break
            wait -= 1
            time.sleep(1)
        return [ self.get_button_name(code) for (update, code) in self.code_history if update > last_update ]

    def clear_recent_codes(self):
        self.code_history = [ ]

    def get_button_name(self, code):
        self.db.select('id,remote_name,button_name')
        self.db.where('code', code)
        results = list(self.db.get('codenames'))
        if len(results) > 0:
            return (code, results[0][1], results[0][2])
        else:
            return (code, '', '')

    def set_button_name(self, code, remote_name, button_name):
        data = { 'code': code, 'remote_name': remote_name, 'button_name': button_name }

        self.db.select('id,code,remote_name,button_name')
        self.db.where('remote_name', remote_name)
        self.db.where('button_name', button_name)
        self.db.or_where('code', code)
        rowid = -1
        for row in self.db.get('codenames'):
            if row[1] == code:
                rowid = row[0]
            else:
                return row[1]

        if rowid >= 0:
            self.db.where('id', rowid)
            self.db.update('codenames', data)
        else:
            self.db.insert('codenames', data)
        return None

    def get_button_code(self, remote_name, button_name):
        self.db.select('id,code')
        self.db.where('remote_name', remote_name)
        self.db.where('button_name', button_name)
        results = list(self.db.get('codenames'))
        if len(results) > 0:
            return results[0][1]
        else:
            return ''

    def add_code_to_history(self, code):
        i = 0
        while i < len(self.code_history):
            if self.code_history[i][1] == code:
                del self.code_history[i]
            else:
                i += 1
                if i >= self.get_setting('max_history') - 1:
                    break
        self.code_history.insert(0, (time.time(), code) )

    def on_receive_code(self, code):
        if code.startswith('x:'):
            nerve.log("received invalid IR code " + code)
            return

        self.add_code_to_history(code)
        (_, remote_name, button_name) = self.get_button_name(code)

        if not self.program_mode:
            try:
                return self.query(code)
            except AttributeError:
                pass

            try:
                return nerve.query('/events/ir/irrecv/' + code)
            except AttributeError:
                nerve.log("No action set for IR code " + code)

    def get_event(self, code):
        self.db.select("id, object")
        self.db.where('code', code)
        results = list(self.db.get('events'))
        if len(results) <= 0:
            return None
        return json.loads(results[0][1])

    def set_event(self, code, obj):
        self.set_object(code, nerve.objects.Module.make_object(obj['__type__'], obj))
        data = { 'code': code, 'object': json.dumps(obj, sort_keys=True) }
        self.db.insert('events', data, replace=True)


