from appJar import gui
from record import Record


class WTGui:
    def __init__(self):
        self.record = Record()
        self.app = gui()
        self.app.setTitle("Walkie-Talkie")
        self.app.setFont(size=24, family="Times")
        self.app.setBg("#7b9095", override=False, tint=False)
        self.app.setSize(200,100)
        self.app.addButton("Record start", self.on_button_pressed_record)
        self.app.addButton("pause", self.on_button_pressed_pause)
        self.app.go()

    def on_button_pressed_record(self, title):
        print('Button with title {} pressed!'.format(title))
        self.app.removeButton( "Record start", self.on_button_pressed_record)
        self.app.removeButton("pause", self.on_button_pressed_pause )
        self.app.addButton("Record stop", self.on_button_pressed_record_done)
        self.app.after(1000, self.record.start_recording)


    def on_button_pressed_record_done(self, title):
        print('Button with title "{}" pressed!'.format(title))
        self.app.removeButton("Record stop", self.on_button_pressed_record_done)
        self.app.addButton("Record start", self.on_button_pressed_record)
        self.app.addLabel("timer", self.record.timer)
        self.app.addButton("pause", self.on_button_pressed_pause)
        self.record.stop()

    def on_button_pressed_pause(self, title):
        print('Button with title "{}" pressed!'.format(title))
        self.app.removeButton("pause", self.on_button_pressed_pause)
        self.app.removeButton("Record start", self.on_button_pressed_record)
        self.app.addButton("un-pause", self.on_button_pressed_unpause)

    def on_button_pressed_unpause(self, title):
        print('Button with title "{}" pressed!'.format(title))
        self.app.removeButton("un-pause", self.on_button_pressed_unpause)
        self.app.addButton("Record start", self.on_button_pressed_record)
        self.app.addButton("pause", self.on_button_pressed_pause)
        self.record.play_recording()


mygui = WTGui()