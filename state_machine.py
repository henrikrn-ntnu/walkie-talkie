import logging
import stmpy
from datetime import datetime
import wave
import pyaudio

class WalkieTalkieSTM:
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
        self.p_out
        self.stream_out
        self.frames
        self.audiofiles = []
        self.WAVE_OUTPUT_FILENAME = ''

    def create_machine(name):
        ''' Create state machine with helper method '''
        walkie_talkie = WalkieTalkieSTM(name)
        #TODO: Add deferred events? Have to make states and triggers instead
        t0 = {'source': 'initial', 
              'target': 'listening',
              'effect': 'subscribe'}
        t1 = {'trigger':'button_press', 
              'source': 'listening', 
              'target':'record_message',
              'effect': 'start_recording'}
        t2 = {'trigger': 'button_release', 
              'source': 'record_message', 
              'target': 'listening',
              'effect': 'stop_recording; send_message'}
        t3 = {'trigger': 'on_message_receive', 
              'source': 'listening', 
              'target': 'listening',
              'effect': 'add_to_list; play_messages'}
        t4 = {'trigger': 'pause', 
              'source': 'listening', 
              'target': 'paused',
              'effect': 'status_change'} #status_change may be useless
        t5 = {'trigger': 'on_message_receive', 
              'source': 'paused', 
              'target': 'paused',
              'effect': 'add_to_list'}
        t6 = {'trigger': 'unpause', 
              'source': 'paused', 
              'target': 'listening',
              'effect': 'play_message'}
        t7 = {'trigger': 't',
              'source': 'record_message',
              'target': 'listening',
              'effect': 'ignore_recording'}

        walkie_talkie_stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3, t4, t5, t6, t7])
        walkie_talkie.stm = walkie_talkie_stm
        return walkie_talkie_stm

    def subscribe(self):
        ''' This should be put in the top of the main file '''
        MQTT_BROKER = 'mqtt.item.ntnu.no'
        MQTT_PORT = 1883
        MQTT_TOPIC_INPUT = 'team8/WalkieTalkie/' + self.name
        MQTT_TOPIC_OUTPUT = 'team8/WalkieTalkie'
        #TODO: actually subscribe

    def start_recording(self):
        self.stm.start_timer('t', self.max_recording_time * 1000)
        
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
            data = self.stream_out.read(self.audiovariables['CHUNK'])
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
        
    def send_message(self):
        msg = self.WAVE_OUTPUT_FILENAME
        #TODO: logic for publishing message on all channels
        self.WAVE_OUTPUT_FILENAME = '' # remove filename (probably not necessary) 

    def add_to_list(self):
        #add recording recieved from broker to list of audiofiles
        #TODO: add logic for fetching .wav file
        file = '' #something.wav
        self.audiofiles.append(file)

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
                self.stream_in.write(data)
                data = wf.readframes(chunk)
            self._logger.debug('Recording played')

            """ Graceful shutdown """ 
            stream_in.close()
            p_in.terminate()

    def status_change(self):
        return

    def ignore_recording(self):
        ''' Stop recording '''
        self.stream_out.stop_stream()
        self.stream_out.close()
        self.p_out.terminate()
        self._logger.debug('Recording ignored')

        
    

