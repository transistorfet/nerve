
import thread
import os
import sys
import select
import xmmsclient

import nerve

class Xmms2 (nerve.Device):
    def __init__(self):
	nerve.Device.__init__(self)
	self.xmms = xmmsclient.XMMS('PyXMMS')
	self.artist = ""
	self.title = ""
	try:
	    self.xmms.connect(os.getenv("XMMS_PATH"))
	except IOError, detail:
	    print "Connection failed:", detail
	    sys.exit(1)
	self.xmms.playback_current_id(self._get_info)
	self.xmms.broadcast_playback_current_id(self._get_info)
	self.reply = None
	self.stop_thread = False
	thread.start_new_thread(self.do_thread, (self,))

    def __del__(self):
	self.stop_thread = True

    def do_thread(self, nothing):
	while not self.stop_thread:
	    fd = self.xmms.get_fd()

	    if self.xmms.want_ioout():
		self.xmms.ioout()

	    (i, o, e) = select.select([ fd ], [ ], [ fd ], 0.1)
	    if i and i[0] == fd:
		self.xmms.ioin()
	    if e and e[0] == fd:
		self.xmms.disconnect()
		self.stop_thread = True


    ### Resources ###

    def toggle(self, msg):
	self.xmms.playback_status(self._toggle)

    def _toggle(self, res):
	if res.value() == xmmsclient.PLAYBACK_STATUS_PLAY:
	    self.xmms.playback_pause()
	else:
	    self.xmms.playback_start()

    def next(self, msg):
	self.xmms.playlist_set_next_rel(1)
	self.xmms.playback_tickle()
	#song = self.winamp.getCurrentPlayingTitle()
	#msg.server.send('.'.join(msg.names[:-1]) + ".getsong " + song, msg.addr)
	# you need a way to say 'call function (playback_current_song

    def previous(self, msg):
	self.xmms.playlist_set_next_rel(-1)
	self.xmms.playback_tickle()

    def sort(self, msg):
	self.xmms.playlist_sort([ 'url' ])

    def shuffle(self, msg):
	self.xmms.playlist_shuffle()

    def getsong(self, msg):
	self.reply = msg
	msg.from_node.send(msg.query + " " + self.artist + " - " + self.title)

    def update_info(self):
	self.xmms.playback_current_id(self._get_info)

    def _get_info(self, res):
	self.xmms.medialib_get_info(res.value(), self._update_song_info)

    def _update_song_info(self, res):
	info = res.value()
	if 'artist' in info:
	    self.artist = info['artist']
	else:
	    self.artist = "No Artist"
	if 'title' in info:
	    self.title = info['title']
	else:
	    self.title = "No Title"
	#print self.artist + " - " + self.title
	msg = self.reply
	if msg:
	    msg.from_node.send(msg.query + " " + self.artist + " - " + self.title)



