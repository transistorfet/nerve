#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.serial
import nerve.events

import time


class MySensorsSerialGateway (nerve.serial.SerialDevice):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        return config_info

    """
    def get_config_data(self):
        #del self.config['__children__']
        return self.config
    """

    def set_child(self, index, obj):
        pass

    def del_child(self, index):
        return False

    def on_connect(self):
        time.sleep(2)
        for node in self.keys_children():
            self.reset_node(int(node))
            time.sleep(5)

    def on_receive(self, line):
        args = line.split(';')
        if len(args) != 6:
            nerve.log("mysensors: invalid message received: " + line, logtype='error')
            return
        nodeid = args[0]
        sensorid = args[1]
        msgtype = int(args[2])
        ack = int(args[3])
        subtype = int(args[4])
        payload = args[5]

        current_time = time.time()
        node = self.get_child(nodeid)
        if node:
            node.last_recv = current_time

        if msgtype == MsgType.PRESENTATION:
            nerve.log("mysensors: new sensor presented itself: " + str(nodeid) + ":" + str(sensorid))
            # TODO this is a hack because the internet is connected to sensor 6 remote receptacle
            if sensorid == 6:
                return
            self._add_sensor(nodeid, sensorid, subtype, payload)

        elif msgtype == MsgType.SET:
            #sensor = self.get_sensor(nodeid, sensorid)
            sensor = node.get_child(sensorid)
            if not sensor:
                sensor = self._add_sensor(nodeid, sensorid)
            sensor.last_recv = current_time
            sensor.last_type = subtype
            sensor.last_value = payload
            sensor._on_receive()

        elif msgtype == MsgType.REQ:
            pass

        elif msgtype == MsgType.INTERNAL:
            if subtype == SubTypeInternal.I_LOG_MESSAGE:
                nerve.log("mysensors: " + payload)

            elif subtype == SubTypeInternal.I_BATTERY_LEVEL:
                node = self.get_node(nodeid)
                if node:
                    node.battery_level = float(payload)

            elif subtype == SubTypeInternal.I_SKETCH_NAME:
                node = self.get_node(nodeid)
                if node:
                    node.name = payload

            elif subtype == SubTypeInternal.I_SKETCH_VERSION:
                node = self.get_node(nodeid)
                if node:
                    node.version = payload

            elif subtype == SubTypeInternal.I_CONFIG:
                self.send("%s;%s;3;0;%d;M" % (nodeid, sensorid, subtype))

        elif msgtype == MsgType.STREAM:
            pass
        else:
            nerve.log("received an invalid message type: " + line, logtype='error')

    def on_idle(self):
        pass

    def _add_sensor(self, nodeid, sensorid, subtype=0, version=''):
        node = self.get_child(nodeid)

        if not node:
            node = MySensorsNode(nodeid=nodeid)
            super().set_child(nodeid, node)

        return node._add_sensor(sensorid, subtype, version)

    def get_node(self, nodeid):
        return self.get_child(nodeid)

    def get_sensor(self, nodeid, sensorid):
        node = self.get_child(nodeid)
        if not node:
            return None
        return node.get_child(sensorid)

    def reset_node(self, id):
        self.send("%s;%s;3;0;%d;%s" % (str(id), '255', SubTypeInternal.I_REBOOT, ''))

    def assign_id(self, id):
        self.send("%s;%s;3;0;%d;%s" % ('255', '255', SubTypeInternal.I_ID_RESPONSE, str(id)))


class MySensorsNode (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.nodeid = self.get_setting('nodeid')
        self.name = ''
        self.version = ''
        self.battery_level = 0.0
        self.last_recv = time.time()

    def set_child(self, index, obj):
        pass

    def del_child(self, index):
        return False

    def _add_sensor(self, sensorid, subtype, version):
        sensor = MySensorsSensor(sensorid=sensorid, type=subtype, version=version)
        super().set_child(sensorid, sensor)
        return sensor


class MySensorsSensor (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.sensorid = self.get_setting('sensorid')
        self.type = self.get_setting('type')
        self.version = self.get_setting('version')
        self.should_publish = self.get_setting('should_publish', default=False)
        self.last_recv = 0
        self.last_type = None
        self.last_value = None

    def send_msg(self, subtype, val):
        node = self._parent
        serialdev = node._parent
        serialdev.send("%s;%s;1;0;%d;%s" % (node.nodeid, self.sensorid, int(subtype), str(val)))

    def set_child(self, index, obj):
        pass

    def del_child(self, index):
        return False

    def publish(self, enable):
        self.should_publish = enable

    def set_value(self, val, subtype=None):
        if subtype == None:
            subtype = SubTypeSet.V_LIGHT
        self.send_msg(subtype, val)
        self.last_value = val
        self.last_type = subtype
        self.last_recv = time.time()

    def __call__(self, val=None, subtype=None):
        if val is not None:
            self.set_value(val, subtype)
        else:
            """
            if time.time() > self.last_recv + 3600:
                # TODO you should probably send a message to the node or something... reset it perhaps?
                return None
            """
            return self.last_value

    def toggle(self):
        if self.type == SubTypePresentation.S_LIGHT:
            self.set_value(0 if self.last_value else 1, SubTypeSet.V_LIGHT)

    def last_recv(self):
        return self.last_recv

    def last_type(self):
        return self.last_type

    def last_value(self):
        return self.last_value

    def _on_receive(self):
        # TODO publish event? maybe even have a per sensor or per node flag for whether to publish
        if self.should_publish:
            nerve.events.publish(self.get_pathname(), value=self.last_value)



class MsgType (object):
    PRESENTATION = 0
    SET = 1
    REQ = 2
    INTERNAL = 3
    STREAM = 4

class SubTypePresentation (object):
    S_DOOR              = 0        # Door and window sensors
    S_MOTION            = 1        # Motion sensors
    S_SMOKE             = 2        # Smoke sensor
    S_LIGHT             = 3        # Light Actuator (on/off)
    S_DIMMER            = 4        # Dimmable device of some kind
    S_COVER             = 5        # Window covers or shades
    S_TEMP              = 6        # Temperature sensor
    S_HUM               = 7        # Humidity sensor
    S_BARO              = 8        # Barometer sensor (Pressure)
    S_WIND              = 9        # Wind sensor
    S_RAIN              = 10       # Rain sensor
    S_UV                = 11       # UV sensor
    S_WEIGHT            = 12       # Weight sensor for scales etc.
    S_POWER             = 13       # Power measuring device, like power meters
    S_HEATER            = 14       # Heater device
    S_DISTANCE          = 15       # Distance sensor
    S_LIGHT_LEVEL       = 16       # Light sensor
    S_ARDUINO_NODE      = 17       # Arduino node device
    S_ARDUINO_RELAY     = 18       # Arduino repeating node device
    S_LOCK              = 19       # Lock device
    S_IR                = 20       # Ir sender/receiver device
    S_WATER             = 21       # Water meter
    S_AIR_QUALITY       = 22       # Air quality sensor e.g. MQ-2
    S_CUSTOM            = 23       # Use this for custom sensors where no other fits.
    S_DUST              = 24       # Dust level sensor
    S_SCENE_CONTROLLER  = 25       # Scene controller device

class SubTypeSet (object):
    V_TEMP          = 0         # Temperature
    V_HUM           = 1         # Humidity
    V_LIGHT         = 2         # Light status. 0=off 1=on
    V_DIMMER        = 3         # Dimmer value. 0-100%
    V_PRESSURE      = 4         # Atmospheric Pressure
    V_FORECAST      = 5         # Whether forecast. One of "stable", "sunny", "cloudy", "unstable", "thunderstorm" or "unknown"
    V_RAIN          = 6         # Amount of rain
    V_RAINRATE      = 7         # Rate of rain
    V_WIND          = 8         # Windspeed
    V_GUST          = 9         # Gust
    V_DIRECTION     = 10        # Wind direction
    V_UV            = 11        # UV light level
    V_WEIGHT        = 12        # Weight (for scales etc)
    V_DISTANCE      = 13        # Distance
    V_IMPEDANCE     = 14        # Impedance value
    V_ARMED         = 15        # Armed status of a security sensor. 1=Armed, 0=Bypassed
    V_TRIPPED       = 16        # Tripped status of a security sensor. 1=Tripped, 0=Untripped
    V_WATT          = 17        # Watt value for power meters
    V_KWH           = 18        # Accumulated number of KWH for a power meter
    V_SCENE_ON      = 19        # Turn on a scene
    V_SCENE_OFF     = 20        # Turn of a scene
    V_HEATER        = 21        # Mode of header. One of "Off", "HeatOn", "CoolOn", or "AutoChangeOver"
    V_HEATER_SW     = 22        # Heater switch power. 1=On, 0=Off
    V_LIGHT_LEVEL   = 23        # Light level. 0-100%
    V_VAR1          = 24        # Custom value
    V_VAR2          = 25        # Custom value
    V_VAR3          = 26        # Custom value
    V_VAR4          = 27        # Custom value
    V_VAR5          = 28        # Custom value
    V_UP            = 29        # Window covering. Up.
    V_DOWN          = 30        # Window covering. Down.
    V_STOP          = 31        # Window covering. Stop.
    V_IR_SEND       = 32        # Send out an IR-command
    V_IR_RECEIVE    = 33        # This message contains a received IR-command
    V_FLOW          = 34        # Flow of water (in meter)
    V_VOLUME        = 35        # Water volume
    V_LOCK_STATUS   = 36        # Set or get lock status. 1=Locked, 0=Unlocked
    V_DUST_LEVEL    = 37        # Dust level
    V_VOLTAGE       = 38        # Voltage level
    V_CURRENT       = 39        # Current level


class SubTypeInternal (object):
    I_BATTERY_LEVEL         = 0         # Use this to report the battery level (in percent 0-100).
    I_TIME                  = 1         # Sensors can request the current time from the Controller using this message. The time will be reported as the seconds since 1970
    I_VERSION               = 2         # Sensors report their library version at startup using this message type
    I_ID_REQUEST            = 3         # Use this to request a unique node id from the controller.
    I_ID_RESPONSE           = 4         # Id response back to sensor. Payload contains sensor id.
    I_INCLUSION_MODE        = 5         # Start/stop inclusion mode of the Controller (1=start, 0=stop).
    I_CONFIG                = 6         # Config request from node. Reply with (M)etric or (I)mperal back to sensor.
    I_FIND_PARENT           = 7         # When a sensor starts up, it broadcast a search request to all neighbor nodes. They reply with a I_FIND_PARENT_RESPONSE.
    I_FIND_PARENT_RESPONSE  = 8         # Reply message type to I_FIND_PARENT request.
    I_LOG_MESSAGE           = 9         # Sent by the gateway to the Controller to trace-log a message
    I_CHILDREN              = 10        # A message that can be used to transfer child sensors (from EEPROM routing table) of a repeating node.
    I_SKETCH_NAME           = 11        # Optional sketch name that can be used to identify sensor in the Controller GUI
    I_SKETCH_VERSION        = 12        # Optional sketch version that can be reported to keep track of the version of sensor in the Controller GUI.
    I_REBOOT                = 13        # Used by OTA firmware updates. Request for node to reboot.
    I_GATEWAY_READY         = 14        # Send by gateway to controller when startup is complete.

