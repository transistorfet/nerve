
import nerve

class Layout (nerve.Device):
    def _get_file_contents(self, filename):
	with open(filename, 'r') as f:
	    data = f.read()
	return data

    # When the phone requests layout.default, return the default layout XML file
    def livingroom(self, msg):
	contents = self._get_file_contents('layouts/livingroom.xml')
	msg.from_node.send(msg.query + " " + contents)

    def comproom(self, msg):
	contents = self._get_file_contents('layouts/comproom.xml')
	msg.from_node.send(msg.query + " " + contents)

    def general(self, msg):
	contents = self._get_file_contents('layouts/general.xml')
	msg.from_node.send(msg.query + " " + contents)


