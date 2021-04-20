import pyaudio
import wave
import keyboard  # using module keyboard
import sys
from datetime import datetime

audiofiles = ["11_13_21.wav", "11_13_29.wav"]
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

while True:
    if keyboard.is_pressed('s'):
        start_recording()
    if keyboard.is_pressed('p'):
        print("Playing recording")
        play_recording() #Play recording
        print("Finished playing")


