import logging
import stmpy
from datetime import datetime
import paho.mqtt.client as mqtt
from statemachine import WalkieTalkie
from wtgui import WTGUI

class WalkieTalkieManager():    
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))

    ''' Making and writing to file using the header-logic defined in send.py '''
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
        ''' DEBUG '''
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        ''' Connecting to Broker '''
        self.MQTT_BROKER = 'mqtt.item.ntnu.no'
        self.MQTT_TOPIC_INPUT = 'team8/WalkieTalkie'
        self.MQTT_TOPIC_OUTPUT = 'team8/WalkieTalkie'
        self.MQTT_PORT = 1883
        self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        self.mqtt_client.subscribe(self.MQTT_TOPIC_INPUT)
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(self.MQTT_BROKER, self.MQTT_PORT))
        
        ''' Defining callback methods '''
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        ''' Initializing variables '''
        self.filename = ''
        self.currentfile = ''

        ''' Start the internal loop to process MQTT messages '''
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.loop_start()

        ''' Start the stmpy driver '''
        self.driver = stmpy.Driver()
        self.driver.start(keep_active=True)
        self._logger.debug('Component initialization finished')

        ''' Create WalkieTalkie and assigning driver to state machine '''
        self.walkie_talkie, self.walkie_talkie_stm = WalkieTalkie.create_machine('wt1')
        self.driver.add_machine(self.walkie_talkie_stm)

        ''' Setup GUI '''
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