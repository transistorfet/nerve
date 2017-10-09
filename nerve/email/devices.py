#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import smtplib
import email.mime.text 


class EmailNotifierQuery (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('server', "Email Server", default='localhost')
        config_info.add_setting('from', "From Address", default='info@jabberwocky.ca')
        config_info.add_setting('to', "To Address", default='philosophizer@gmail.com')
        config_info.add_setting('severity', "Severity Mask", default='serious')
        return config_info

    def __call__(self, note):
        if note['severity'] != self.get_setting('severity'):
            return

        msg = email.mime.text.MIMEText("{0} [{1}]\n{2}".format(time.strftime("%Y-%m-%d %H:%M", time.localtime(note['timestamp'])), note['severity'], note['message']))
        msg['Subject'] = "{0} notification from nerve".format(note['severity'])
        msg['From'] = self.get_setting('from')
        msg['To'] = self.get_setting('to')

        nerve.log("sending email notification to " + msg['To'], logtype='info')
        s = smtplib.SMTP(self.get_setting('server'))
        s.sendmail(msg['From'], [ msg['To'] ], msg.as_string())
        s.quit()

