#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import lxml.html
import requests
#import oauthlib
#import requests_oauthlib

#import oauth2client.client


"""

you could use these drivers to make data accessible.  It would be possible to use this mechanism to get the latest youtube recommendations
for example, in some kind of data format.

This whole module is supposed to be about making data from other websites accessible to the system, possibly for the sake of datalogging,
or more likely, to display it in a special webpage, like a summary of the day, or integrating the latest whatever into... something

"""

class YouTubeAggregator (nerve.Device):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('api_key', "API Key", default='AIzaSyCh7XyVVs4biXd-Rvnm71W5SdejRAK26M4')
        config_info.add_setting('client_id', "Client ID", default='131741203927-9hkaaiouh50ehcqtavp0149oj829cdag.apps.googleusercontent.com')
        config_info.add_setting('client_secret', "Client Secret", default='fSQGuD8jia8FA6yLbB3G7uVw')

        return config_info

    def test(self):
        baseurl = 'https://www.googleapis.com/youtube/v3'
        client_id = self.get_setting('client_id')
        client_secret = self.get_setting('client_secret')

        """
        client = oauthlib.oauth2.BackendApplicationClient(client_id=self.get_setting('client_id'))
        oauth = requests_oauthlib.OAuth2Session(client=client)
        #oauth = requests_oauthlib.OAuth2Session(client_id=client_id, )
        token = oauth.fetch_token(token_url='https://accounts.google.com/o/oauth2/device/code', client_id=client_id, client_secret=client_secret, scope='https://www.googleapis.com/auth/youtube.readonly')
        """

        flow = oauth2client.client.OAuth2WebServerFlow(client_id, client_secret, scope='https://www.googleapis.com/auth/youtube.readonly')

