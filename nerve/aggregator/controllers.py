#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http

import json
import requests
import urllib.parse
import oauth2client.client

class AggregatorController (nerve.http.SessionMixIn, nerve.http.Controller):
    @nerve.public
    def youtube_authorize(self, request):
        redirect_uri = request.make_url('youtube_authorize')
        client_id = '131741203927-9hkaaiouh50ehcqtavp0149oj829cdag.apps.googleusercontent.com'
        client_secret = 'fSQGuD8jia8FA6yLbB3G7uVw'

        #redirect_uri = 'http://jabberwocky.ca/redirect.php?url=' + urllib.parse.quote(request.make_url('youtube_authorize'))
        #client_id = '131741203927-7kee2e858ug0unbidngtl0eetokckqbt.apps.googleusercontent.com'
        #client_secret = 'ye801tEJfi1i7NS5c17i_4_9'

        flow = oauth2client.client.OAuth2WebServerFlow(client_id, client_secret, scope='https://www.googleapis.com/auth/youtube.readonly', redirect_uri=redirect_uri)
        if 'code' not in request.args:
            auth_uri = flow.step1_get_authorize_url()
            self.redirect_to(auth_uri)
        else:
            authcode = request.args['code']
            credentials = flow.step2_exchange(authcode)

            self.session['credentials'] = credentials.to_json()
            self.redirect_to(request.make_url('youtube_home'))

    def _youtube_get_cred(self, request):
        credentials = oauth2client.client.OAuth2Credentials.from_json(self.session['credentials']) if 'credentials' in self.session else None
        print(credentials)
        if not credentials or credentials.access_token_expired:
            self.redirect_to(request.make_url('youtube_authorize'))
            return None
        headers = { }
        credentials.apply(headers)
        return headers

    def _youtube_query(self, query, headers):
        baseurl = 'https://www.googleapis.com/youtube/v3'
        r = requests.get(baseurl + query, headers=headers)
        print(r.text)
        return json.loads(r.text)

    @nerve.public
    def youtube_home(self, request):
        headers = self._youtube_get_cred(request)
        if not headers:
            return

        data = { }
        data['videos'] = self._youtube_query('/activities?part=snippet,contentDetails&maxResults=50&home=true', headers)
        self.load_template_view('nerve/aggregator/views/home.blk.pyhtml', data, request)
        self.template_add_to_section('cssfiles', '/aggregator/assets/css/youtube.css')

    @nerve.public
    def youtube_subscriptions(self, request):
        headers = self._youtube_get_cred(request)
        if not headers:
            return

        data = { }
        data['subscriptions'] = self._youtube_query('/subscriptions?part=snippet&maxResults=50&mine=true', headers)
        self.load_template_view('nerve/aggregator/views/subscriptions.blk.pyhtml', data, request)
        self.template_add_to_section('cssfiles', '/aggregator/assets/css/youtube.css')

    @nerve.public
    def youtube_test(self, request):
        print("TESTING")

