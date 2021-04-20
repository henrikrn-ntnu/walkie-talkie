from appJar import gui
from record import start_recording, play_recording, stop

app = gui()
app.setTitle("Walkie-Talkie")
app.setFont(size=24, family="Times")
app.setBg("#7b9095", override=False, tint=False)
app.setSize(200,100)


def on_button_pressed_record(title):
    print('Button with title "{}" pressed!'.format(title))
    app.removeButton("Record start", on_button_pressed_record)
    app.removeButton("pause",on_button_pressed_pause)
    app.addButton("Record stop", on_button_pressed_record_done)
    start_recording()


def on_button_pressed_record_done(title):
    print('Button with title "{}" pressed!'.format(title))
    app.removeButton("Record stop", on_button_pressed_record_done)
    app.addButton("Record start", on_button_pressed_record)
    app.addButton("pause",on_button_pressed_pause)  
    stop()

def on_button_pressed_pause(title):
    print('Button with title "{}" pressed!'.format(title))
    app.removeButton("pause",on_button_pressed_pause)
    app.removeButton("Record start", on_button_pressed_record)
    app.addButton("un-pause",on_button_pressed_unpause)

def on_button_pressed_unpause(title):
    print('Button with title "{}" pressed!'.format(title))
    app.removeButton("un-pause",on_button_pressed_unpause)
    app.addButton("Record start", on_button_pressed_record)
    app.addButton("pause",on_button_pressed_pause)  
    play_recording() 


app.addButton("Record start", on_button_pressed_record)
app.addButton("pause",on_button_pressed_pause)

app.go()