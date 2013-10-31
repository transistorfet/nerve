
import nerve

class LayoutDevice (nerve.Device):
    def _get_file_contents(self, filename):
	with open(filename, 'r') as f:
	    data = f.read()
	return data

    # TODO overload dispatch

    def livingroom(self, msg):
	contents = self._get_file_contents('layouts/livingroom.xml')
	msg.from_node.send(msg.query + " " + contents)

    def comproom(self, msg):
	contents = self._get_file_contents('layouts/comproom.xml')
	msg.from_node.send(msg.query + " " + contents)

    def general(self, msg):
	contents = self._get_file_contents('layouts/general.xml')
	msg.from_node.send(msg.query + " " + contents)


