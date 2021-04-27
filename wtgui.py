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

class WTGUI:
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

    def __init__(self, walkie_talkie_stm):
        self.walkie_talkie_stm = walkie_talkie_stm

        # button text
        self.BUTTON_TEXT_RECORD = "Start recording"
        self.BUTTON_TEXT_STOP = "Stop recording"
        self.BUTTON_TEXT_PAUSE = "Pause"
        self.BUTTON_TEXT_UNPAUSE = "Un-pause"

        # setup and display gui
        self.app = gui()
        self.app.setTitle("Walkie-Talkie")
        self.app.setFont(size=24)
        self.app.setBg("#7b9095", override=False, tint=False)
        self.app.setSize(200,100)
        self.app.addButton(self.BUTTON_TEXT_RECORD, self.on_button_pressed_record)
        self.app.addButton(self.BUTTON_TEXT_PAUSE, self.on_button_pressed_pause)
        self.app.go()