class WalkieTalkie:
    """
    State Machine for a named timer.
    This is the support object for a state machine that models a single timer.
    """
    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component
        self.WAVE_OUTPUT_FILENAME = ''

    def create_machine():
        walkie_talkie = WalkieTalkie(name)
        t0 = {'source':'initial', 
              'target':'listening',
              'effect': 'subscribe'}
        t1 = {'trigger':'button_press', 
              'source':'listening', 
              'target':'record_message',
              'effect': 'start_recording'}
        t2 = {'trigger':'button_release', 
              'source':'record_message', 
              'target':'listening',
              'effect': 'stop_recording; send_message'}
        t3 = {'trigger':'on_message_receive', 
              'source':'listening', 
              'target':'listening',
              'effect': 'add_to_list; play_message'}
        t4 = {'trigger':'pause', 
              'source':'listening', 
              'target':'paused',
              'effect': 'status_change'}
        t5 = {'trigger':'on_message_receive', 
              'source':'paused', 
              'target':'paused',
              'effect': 'add_to_list'}
        t6 = {'trigger':'unpause', 
              'source':'paused', 
              'target':'listening',
              'effect': 'play_message'}
        self.stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3, t4, t5, t6], obj=self)

    def subscribe(self):
        ''' This should be put in the top of the main file '''
        MQTT_BROKER = 'mqtt.item.ntnu.no'
        MQTT_PORT = 1883
        MQTT_TOPIC_INPUT = 'team8/WalkieTalkie/' + name
        MQTT_TOPIC_OUTPUT = 'team8/WalkieTalkie'

    def stop_recording(stream, p, CHANNELS, RATE, FORMAT, frames):
        stream.stop_stream()
        stream.close()
        p.terminate()
        WAVE_OUTPUT_FILENAME = datetime.now().strftime("%H_%M_%S") + ".wav"
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        audiofiles.append(WAVE_OUTPUT_FILENAME)
        
    def start_recording():
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100

        p = pyaudio.PyAudio()

        SPEAKERS = p.get_default_output_device_info()["hostApi"] #The part I have modified

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_host_api_specific_stream_info=SPEAKERS) #The part I have modified
        print("* recording")
        frames = []
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            if keyboard.is_pressed('q'):
                print("* done recording")
                stop_recording(stream, p, CHANNELS, RATE, FORMAT, frames) #Quit recording
                return

    def add_to_list():
        

    def play_recording():
        chunk = 1024
        """ Init audio stream """ 
        try:
            file = audiofiles[0]
            audiofiles.pop(0)
        except:
            print("No recordings")
            return
        wf = wave.open(file, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(
            format = p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)
        
        """ Play entire file """
        data = wf.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunk)

        """ Graceful shutdown """ 
        stream.close()
        p.terminate()

    def send_message():
        return

        
    

