
import thread
import xmmsclient

import device

class Xmms2:
    def __init__(self):
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

    def toggle(self):
	self.xmms.playback_status(self._toggle)

    def _toggle(self, res):
	if res.value() == xmmsclient.PLAYBACK_STATUS_PLAY:
	    self.xmms.playback_pause()
	else:
	    self.xmms.playback_start()

    def next(self):
	self.xmms.playlist_set_next_rel(1)
	self.xmms.playback_tickle()

    def previous(self):
	self.xmms.playlist_set_next_rel(-1)
	self.xmms.playback_tickle()

    def sort(self):
	self.xmms.playlist_sort([ 'url' ])

    def shuffle(self):
	self.xmms.playlist_shuffle()

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
	print self.artist + " - " + self.title

    def fileno(self):
	return self.xmms.get_fd()


class Xmms2 (device.Device):
    def __init__(self):
	self.winamp = winamp.Winamp()

    def next(self, msg):
	self.winamp.next()
	song = self.winamp.getCurrentPlayingTitle()
	serv.send('.'.join(msg.names[:-1]) + ".getsong " + song, msg.addr)

    def previous(self, msg):
	self.winamp.previous()
	song = self.winamp.getCurrentPlayingTitle()
	serv.send('.'.join(msg.names[:-1]) + ".getsong " + song, msg.addr)

    def toggle(self, msg):
	s = self.winamp.getPlaybackStatus()
	if s == winamp.Winamp.PLAYBACK_PLAYING or s == winamp.Winamp.PLAYBACK_PAUSE:
	    self.winamp.pause()
	elif s == winamp.Winamp.PLAYBACK_NOT_PLAYING:
	    self.winamp.play()

    def getvolume(self, msg):
	volume = self.winamp.getVolume()
	serv.send(msg.query + " " + str(volume), msg.addr)

    def getsong(self, msg):
	song = self.winamp.getCurrentPlayingTitle()
	serv.send(msg.query + " " + song, msg.addr)

 



def main():
    lock = False
    relay1 = False
    xmms = Xmms()
    deskclock = LoggedSerial('/dev/ttyACM0', 19200)
    lights = LoggedSerial('/dev/ttyACM1', 19200)

    while 1:
	# TODO you end up writing this a lot, i guess because xmms keeps exiting the select early?
	deskclock.write('L0=' + time.strftime("%H:%M %a %b %d") + '\n')
	if lock == True:
	    deskclock.write('L1=...             \n')
	else:
	    title = xmms.title.ljust(16)
	    title = title[0:16]
	    deskclock.write('L1=' + title.encode('ascii', 'replace') + '\n')

	(rl, wl, el) = select.select([ xmms, deskclock ], [ deskclock ], [], 5.0)
	if deskclock in rl:
	    line = deskclock.readline()
	    line = line.strip()
	    print line
	    if line == "B7=0" or line == 'I0=A2C8':
		if lock == False: xmms.next()
	    elif line == "B6=0" or line == 'I0=A2A8':
		if lock == False: xmms.playpause()
	    elif line == "B5=0" or line == 'I0=A298':
		if lock == False: xmms.previous()
	    elif line == "B3=0" or line == 'I0=A207':
		relay1 = not relay1
		if relay1:
		    deskclock.write('R1=1\n')
		else:
		    deskclock.write('R1=0\n')
	    elif line == "B0=0":
		xmms.shuffle()
	    elif line == "B1=0":
		xmms.sort()
	    elif line == "B2=0":
		lock = not lock
	    elif line[0:5] == 'I0=A2':
		#lights.write('I' + (0x0200 + int(line[5:6])) + '\n')
		s = 'I' + str(0x0200 + int('0x' + line[5:7], 16)) + '\n'
		print s
		lights.write(s)
	elif xmms in rl:
	    xmms.xmms.ioin()

	if xmms.xmms.want_ioout():
	    xmms.xmms.ioout()

main()
 

