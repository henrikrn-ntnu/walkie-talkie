import logging
import stmpy
from datetime import datetime
import wave
import pyaudio
import paho.mqtt.client as mqtt
import paho.mqtt.client as publish
import hashlib
from threading import Thread
from appJar import gui

#Put this in a header file when that stops being a bitch

import hashlib
from datetime import datetime


#Setting global variables
broker = "mqtt.item.ntnu.no"
topic = "team8/WalkieTalkie"
qos = 0
data_block_size = 5000000
WAVE_INPUT_FILENAME = ''
out_hash_md5 = hashlib.md5()
in_hash_md5 = hashlib.md5()

def receive_audiofile(payload):
    WAVE_INPUT_FILENAME = datetime.now().strftime("%H_%M_%S") + ".wav"
    file = open(WAVE_INPUT_FILENAME, 'wr')
    write_to_file(payload, file)
    print("Written to file")
    file.close()
    return WAVE_INPUT_FILENAME
    
def send_audiofile(WAVE_OUTPUT_FILENAME):
    run_flag = True
    file = open(WAVE_OUTPUT_FILENAME, 'rb')
    buffer_list = []
    buffer_list.append(send_header(WAVE_OUTPUT_FILENAME))
    while run_flag:
        buffer = file.read(data_block_size)  # change if want smaller or larger data blcoks
        if buffer:
            out_hash_md5.update(buffer)
            out_message = buffer
            buffer_list.append(out_message)
        else:
            #send hash
            out_message = out_hash_md5.hexdigest()
            buffer_list.append(send_end(WAVE_OUTPUT_FILENAME))
            buffer_list.append(out_message)
            run_flag = False
    file.close()
    return buffer_list

# for outfile as I'm rnning sender and receiver together
def process_message(msg):
    """ This is the main receiver code
    """
    if len(msg) == 200:  # is header or end
        msg_in = msg.decode("utf-8")
        msg_in = msg_in.split(",,")
        if msg_in[0] == "end":  # is it really last packet?
            #in_hash_final = in_hash_md5.hexdigest()
            return False
        else:
            if msg_in[0] != "header":
                in_hash_md5.update(msg)
                return True
            else:
                return False
    else:
        in_hash_md5.update(msg)
        return True


# define callback
def write_to_file(payload, file):
    if process_message(payload):
        file.write(payload)


def on_publish(client, userdata, mid):
    client.puback_flag = True


def wait_for(client, msgType, running_loop=False):
    client.running_loop = running_loop  # if using external loop
    while True:
        if msgType == "PUBACK":
            if client.on_publish:
                if client.puback_flag:
                    return True

        if not client.running_loop:
            client.loop(.00)  # check for messages manually
    return True


def send_header(filename):
    header = "header" + ",," + filename + ",,"
    header = bytearray(header, "utf-8")
    header.extend(b',' * (200 - len(header)))
    return header


def send_end(filename):
    #end = "end" + ",," + filename + ",," + out_hash_md5.hexdigest()
    end = "end" + ",," + filename + ",,"
    end = bytearray(end, "utf-8")
    end.extend(b',' * (200 - len(end)))
    return end

def c_publish(client, topic, out_message, qos):
    client.publish(topic, out_message, qos)  # publish
    #if res == 0:  # published ok
    if wait_for(client, "PUBACK", running_loop=True):
        client.puback_flag = False  # reset flag
    else:
        raise SystemExit("not got puback so quitting")

class WalkieTalkie:
    '''
    def on_message(self, client, userdata, message):
        return self.driver.send(on_message_receive)
    '''

    def __init__(self, name):
        self._logger = logging.getLogger(__name__)
        self.name = name

        ''' Constants '''
        self.max_recording_time = 60 #seconds
        self.audioconstants = {
            'CHUNK': 1024,
            'FORMAT' : pyaudio.paInt16,
            'CHANNELS' : 2,
            'RATE' : 44100
        }

        ''' Variables used in multiple functions, defined on init to be reachable '''
        self.filename = ''
        self.p_out = ''
        self.stream_out = ''
        self.frames = []
        self.audiofiles = []
        self.WAVE_OUTPUT_FILENAME = ''
        self.MQTT_BROKER = 'mqtt.item.ntnu.no'
        self.MQTT_TOPIC_INPUT = 'team8/WalkieTalkie/'
        self.MQTT_TOPIC_OUTPUT = 'team8/WalkieTalkie'
        self.MQTT_PORT = 1883
        '''
        
        self.mqtt_client.subsribe(self.MQTT_TOPIC_INPUT)
        
        self.mqtt_client.on_message = self.on_message
        self.driver = stmpy.Driver()
        self.driver.start(keep_active=True)
        '''

        #connect to broker
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        self.mqtt_client.loop_start()

    def create_machine(name):
        ''' Create state machine with helper method '''
        walkie_talkie = WalkieTalkie(name)
        #TODO: Add deferred events? Have to make states and triggers instead
        
        t0 = {'source': 'initial', 
              'target': 'listening'}
        t1 = {'trigger':'button_press', 
              'source': 'listening', 
              'target':'record_message'}
        t2 = {'trigger': 'button_release', 
              'source': 'record_message', 
              'target': 'listening',
              'effect': 'stop_timer("t"); stop_recording; send_message'}
        t3 = {'trigger': 'on_message_receive', 
              'source': 'listening', 
              'target': 'listening',
              'effect': 'add_to_list; play_messages'}
        t4 = {'trigger': 'pause', 
              'source': 'listening', 
              'target': 'paused'}
        t5 = {'trigger': 'on_message_receive', 
              'source': 'paused', 
              'target': 'paused',
              'effect': 'add_to_list'}
        t6 = {'trigger': 'unpause', 
              'source': 'paused', 
              'target': 'listening',
              'effect': 'play_messages'}
        t7 = {'trigger': 't',
              'source': 'record_message',
              'target': 'listening',
              'effect': 'ignore_recording'}
        t8 = {'trigger': 'on_message_receive',
              'source': 'record_message',
              'target': 'listening',
              'a': 'defer'}
        s_1 = {'name': 'listening', 'button_release' : 'defer'}
        s_2 = {'name': 'paused'}
        s_3 = {'name': 'record_message','do': 'start_recording(); start_timer("t", 60000)',
            'on_message_receive': 'defer'}

        walkie_talkie_stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8], states = [s_1, s_2, s_3], obj=walkie_talkie)
        walkie_talkie.stm = walkie_talkie_stm
        return walkie_talkie, walkie_talkie_stm


    def start_recording(self):
        #self.stm.start_timer('t', self.max_recording_time * 1000) #Input in milliseconds
        
        ''' Init recording '''
        self.p_out = pyaudio.PyAudio()
        SPEAKERS = self.p_out.get_default_output_device_info()["hostApi"] 
        self.stream_out = self.p_out.open(format=self.audioconstants['FORMAT'],
                        channels=self.audioconstants['CHANNELS'],
                        rate=self.audioconstants['RATE'],
                        input=True,
                        frames_per_buffer = self.audioconstants['CHUNK'],
                        input_host_api_specific_stream_info=SPEAKERS)
        
        ''' Start recording ''' 
        print("* recording")
        self._logger.debug('Recording started')
        self.frames = []
        while True:
            data = self.stream_out.read(self.audioconstants['CHUNK'])
            self.frames.append(data)

    def stop_recording(self):
        ''' Stop recording '''
        self.stream_out.stop_stream()
        self.stream_out.close()
        self.p_out.terminate()
        self._logger.debug('Recording stopped')

        ''' Save recording '''
        self.WAVE_OUTPUT_FILENAME = datetime.now().strftime("%H_%M_%S") + ".wav"
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.audioconstants['CHANNELS'])
        wf.setsampwidth(self.p_out.get_sample_size(self.audioconstants['FORMAT']))
        wf.setframerate(self.audioconstants['RATE'])
        wf.writeframes(b''.join(self.frames))
        wf.close() 
        self._logger.debug('Recording written to file: {}'.format(self.WAVE_OUTPUT_FILENAME))

    def on_publish(self): #Is this on_message_receive?
        self.mqtt_client.puback_flag = True 

    def wait_for(self, msgType, running_loop=False):
        self.mqtt_client.running_loop = running_loop  # if using external loop
        while True:
            if msgType == "PUBACK":
                if self.mqtt_client.on_publish:
                    if self.mqtt_client.puback_flag:
                        return True

            if not self.mqtt_client.running_loop:
                self.mqtt_client.loop(.00)  # check for messages manually
        return True

    def send_message(self):
        filename = self.WAVE_OUTPUT_FILENAME
        buffer_list = send_audiofile(filename)
        for element in buffer_list:
            c_publish(self.mqtt_client, self.MQTT_TOPIC_OUTPUT, element, qos=0)

        self.WAVE_OUTPUT_FILENAME = '' # remove filename just to be safe 

    def add_to_list(self):
        self.audiofiles.append(self.filename)
        self.filename = ''

    def play_messages(self):
        while len(self.audiofiles) > 0:
            chunk = self.audioconstants['CHUNK']

            """ Init audio stream """ 
            try: #This try may be useless because of the while loop
                file = self.audiofiles[0]
                self.audiofiles.pop(0)
            except Exception as e:
                print("No recordings")
                self._logger.error('No recordings to play. {}'.format(e))
                return
            wf = wave.open(file, 'rb')
            p_in = pyaudio.PyAudio()
            stream_in = p_in.open(
                format = p_in.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
            
            """ Play entire file """
            data = wf.readframes(chunk)
            while len(data) > 0:
                stream_in.write(data)
                data = wf.readframes(chunk)
            self._logger.debug('Recording played')

            """ Graceful shutdown """ 
            stream_in.close()
            p_in.terminate()

    def ignore_recording(self):
        ''' Stop recording '''
        self.stream_out.stop_stream()
        self.stream_out.close()
        self.p_out.terminate()
        self._logger.debug('Recording ignored')
       



class WalkieTalkieManager():
    def on_button_pressed_record(self):
        ''' Change layout and send button_press message'''
        self.app.removeButton(self.BUTTON_TEXT_RECORD, self.on_button_pressed_record)
        self.app.removeButton(self.BUTTON_TEXT_PAUSE,self.on_button_pressed_pause)
        self.app.addButton(self.BUTTON_TEXT_STOP, self.on_button_pressed_record_done)
        self.walkie_talkie_stm.send('button_press')

    def on_button_pressed_record_done(self):
        ''' Change layout and send button_release message'''
        self.app.removeButton(self.BUTTON_TEXT_STOP, self.on_button_pressed_record_done)
        self.app.addButton(self.BUTTON_TEXT_RECORD, self.on_button_pressed_record)
        self.app.addButton(self.BUTTON_TEXT_PAUSE,self.on_button_pressed_pause)  
        self.walkie_talkie_stm.send('button_release')

    def on_button_pressed_pause(self):
        ''' Change layout and send pause message'''
        self.app.removeButton(self.BUTTON_TEXT_PAUSE, self.on_button_pressed_pause)
        self.app.removeButton(self.BUTTON_TEXT_RECORD, self.on_button_pressed_record)
        self.app.addButton(self.BUTTON_TEXT_UNPAUSE, self.on_button_pressed_unpause)  
        self.walkie_talkie_stm.send('pause')

    def on_button_pressed_unpause(self):
        ''' Change layout and send unpause message'''
        self.app.removeButton(self.BUTTON_TEXT_UNPAUSE, self.on_button_pressed_unpause)
        self.app.addButton(self.BUTTON_TEXT_RECORD, self.on_button_pressed_record)
        self.app.addButton(self.BUTTON_TEXT_PAUSE,self.on_button_pressed_pause)  
        self.walkie_talkie_stm.send('unpause')  

    def process_message(self, msg):
        """ This is the main receiver code
        """
        if len(msg) == 200:  # is header or end
            msg_in = msg.decode("utf-8")
            msg_in = msg_in.split(",,")
            if msg_in[0] == "end":  # is it really last packet?
                #in_hash_final = in_hash_md5.hexdigest()
                return False
            else:
                if msg_in[0] != "header":
                    in_hash_md5.update(msg)
                    return True
                else:
                    return False
        else:
            in_hash_md5.update(msg)
            return True
    
    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))
    
    def on_message(self, client, userdata, msg):
        #recieve_audiofile()
        self.walkie_talkie.filename = receive_audiofile(msg.payload)
        self.walkie_talkie_stm.send('on_message_receive')

   
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        '''
        out_hash_md5 = hashlib.md5()
        in_hash_md5 = hashlib.md5()
        '''

        # create client
        self.MQTT_BROKER = 'mqtt.item.ntnu.no'
        self.MQTT_TOPIC_INPUT = 'team8/WalkieTalkie'
        self.MQTT_TOPIC_OUTPUT = 'team8/WalkieTalkie'
        self.MQTT_PORT = 1883

        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(self.MQTT_BROKER, self.MQTT_PORT))
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

         # button text
        self.BUTTON_TEXT_RECORD = "Start recording"
        self.BUTTON_TEXT_STOP = "Stop recording"
        self.BUTTON_TEXT_PAUSE = "Pause"
        self.BUTTON_TEXT_UNPAUSE = "Un-pause"

        # setup and display gui
        self.app = gui()
        self.app.setTitle("Walkie-Talkie")
        self.app.setFont(size=24, family="Times")
        self.app.setBg("#7b9095", override=False, tint=False)
        self.app.setSize(200,100)
        self.app.addButton(self.BUTTON_TEXT_RECORD, self.on_button_pressed_record)
        self.app.addButton(self.BUTTON_TEXT_PAUSE, self.on_button_pressed_pause)
        self.app.go()



debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

w = WalkieTalkieManager()




