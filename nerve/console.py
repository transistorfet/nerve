
import nerve

import time
import traceback

class Console (nerve.Node):
    def send(self, text):
	# TODO this is how a response is sent to the console??
	print text

    @staticmethod
    def log(text):
	print time.strftime("%Y-%m-%d %H:%M") + " " + text

    @staticmethod
    def loop():
        while 1:
	    line = raw_input(">> ")
	    if line == 'quit':
		break
	    elif (line):
		try:
		    msg = nerve.Message(line, Console, Console)
		    nerve.dispatch(msg)
		except:
		    t = traceback.format_exc()
		    nerve.Console.log(t)

 
