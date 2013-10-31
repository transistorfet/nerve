

class InvalidRequest (Exception):
    pass

# TODO change Node to Endpoint or something

class Node (object):
    def __init__(self):
	pass

    def send(self, text):
	# TODO emit error??
	pass


class Message (object):
    # TODO addr and server could be replaced with a node, and then all the code will use node.send(text) to reply to the sender
    def __init__(self, line, from_node, to_node):
	self.from_node = from_node
	self.to_node = to_node
	self.line = line
	self.args = line.split()
	self.query = self.args.pop(0)
	self.names = self.query.split('.')


class Device (object):
    def __init__(self):
	self.name = None

    def dispatch(self, msg, index=0):
	if index + 1 != len(msg.names):
	    raise InvalidRequest
	func = getattr(self, msg.names[index])
	return func(msg)


class Namespace (object):
    root = None

    def __init__(self):
	self.devices = { }

    def add(self, name, dev):
	self.devices[name] = dev
	dev.name = name

    def get(self, name):
	if name in self.devices:
	    return self.devices[name]
	return None

    def query(self, line, from_node=None, to_node=None):
	msg = Message(line, from_node, to_node)
	self.dispatch(msg)

    def dispatch(self, msg, index=0):
	if index > len(msg.names):
	    raise InvalidRequest
	if not msg.names[index] in self.devices:
	    raise InvalidRequest
	dev = self.devices[msg.names[index]]
	return dev.dispatch(msg, index + 1)


