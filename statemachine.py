import logging
import stmpy
from datetime import datetime
import wave
import pyaudio
import paho.mqtt.client as mqtt
import time

import sendreceive as sr

class WalkieTalkie:

    def __init__(self, name):

        # logging
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self.name = name
        self.recording = False
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

        #connect to broker
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        self.mqtt_client.loop_start()

    def create_machine(name):
        ''' Create state machine with helper method '''
        walkie_talkie = WalkieTalkie(name)
        
        t0 = {'source': 'initial', 
              'target': 'listening'}
        t1 = {'trigger':'button_press', 
              'source': 'listening', 
              'target':'record_message',
              'effect': 'start_timer("t", 60000)'}
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
        s_1 = {'name': 'listening', 'button_release': ''}
        s_2 = {'name': 'paused'}
        s_3 = {'name': 'record_message','do': 'start_recording()',
            'on_message_receive': 'defer'}

        walkie_talkie_stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8], states = [s_1, s_2, s_3], obj=walkie_talkie)
        walkie_talkie.stm = walkie_talkie_stm
        return walkie_talkie, walkie_talkie_stm


    def start_recording(self):
        ''' Initialize recording not taken from Stackoverflow at all *sweating intensifies* '''
        self.p_out = pyaudio.PyAudio()
        SPEAKERS = self.p_out.get_default_output_device_info()["hostApi"] 
        self.stream_out = self.p_out.open(format=self.audioconstants['FORMAT'],
                        channels=self.audioconstants['CHANNELS'],
                        rate=self.audioconstants['RATE'],
                        input=True,
                        frames_per_buffer = self.audioconstants['CHUNK'],
                        input_host_api_specific_stream_info=SPEAKERS)
        
        ''' Start recording ''' 
        self._logger.debug('Recording started')
        self.frames = []
        ''' This loop is broken by either timing out or button_release signal from GUI'''
        self.recording = True
        while self.recording:
            data = self.stream_out.read(self.audioconstants['CHUNK'])
            self.frames.append(data)

    def stop_recording(self):
        ''' Stop recording '''
        self.recording = False
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

    def send_message(self):
        filename = self.WAVE_OUTPUT_FILENAME
        self._logger.debug('Start sending message')
        packet_list = sr.create_packets(filename)
        self._logger.debug('Received buffer_list, start sending packets')
        
        ''' Needs to wait a bit before sending next packet. Could e.g., implement an ack-flag if a higher order of QoS were to be used. '''
        for packet in packet_list:
            self._logger.debug('Sending packet')
            self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT, packet, qos=0)
            time.sleep(1)

        self._logger.debug('Packets sent')
        ''' Deleting filename to be sure it does not overwrite an already existing file '''
        self.WAVE_OUTPUT_FILENAME = ''

    def add_to_list(self):
        self.audiofiles.append(self.filename)
        self._logger.debug('Received recording added to list')
        self.filename = ''

    def play_messages(self):
        self._logger.debug('Initialize playing messages')
        while len(self.audiofiles) > 0:
            chunk = self.audioconstants['CHUNK']

            """ Init audio stream """ 
            try: #This try may be useless because of the while loop
                file = self.audiofiles[0]
                self.audiofiles.pop(0)
                wf = wave.open(file, 'rb')
                p_in = pyaudio.PyAudio()
                stream_in = p_in.open(
                    format = p_in.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
                self._logger.debug('Recording ready to play')
            except Exception as e:
                self._logger.error('Something wrong with file. {}'.format(e))
                return

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
        self.recording = False
        self.stream_out.stop_stream()
        self.stream_out.close()
        self.p_out.terminate()
        self._logger.debug('Recording ignored')
