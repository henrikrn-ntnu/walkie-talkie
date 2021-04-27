import logging
import stmpy
from datetime import datetime
import paho.mqtt.client as mqtt

#other files:
from statemachine import WalkieTalkie
from wtgui import WTGUI

class WalkieTalkieManager():    
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))
    
    def on_message(self, client, userdata, msg):
        if len(msg.payload) == 200:
            msg_in = msg.payload.decode("utf-8")
            msg_in = msg_in.split(",,")
            if msg_in[0] == "start":
                self.filename = datetime.now().strftime("%H_%M_%S") + ".wav"
                self.currentfile = open(self.filename, 'wb')
            elif msg_in[0] == "stop":
                self.currentfile.close()
                self.walkie_talkie.filename = self.filename
                self.walkie_talkie_stm.send('on_message_receive')
        else:
            self.currentfile.write(msg.payload)

   
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create client
        self.MQTT_BROKER = 'mqtt.item.ntnu.no'
        self.MQTT_TOPIC_INPUT = 'team8/WalkieTalkie'
        self.MQTT_TOPIC_OUTPUT = 'team8/WalkieTalkie'
        self.MQTT_PORT = 1883

        self.filename = ''
        self.currentfile = ''

        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(self.MQTT_BROKER, self.MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(self.MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.driver = stmpy.Driver()
        self.driver.start(keep_active=True)
        self._logger.debug('Component initialization finished')

        #create walkie talkie
        self.walkie_talkie, self.walkie_talkie_stm = WalkieTalkie.create_machine('wt1')
        self.driver.add_machine(self.walkie_talkie_stm)

        # setup gui
        gui = WTGUI(self.walkie_talkie_stm)



debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

w = WalkieTalkieManager()