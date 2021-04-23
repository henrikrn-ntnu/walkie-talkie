from appJar import gui
from record import Record

class WTGui:
    app = gui()
    app.setTitle("Walkie-Talkie")
    app.setFont(size=24, family="Times")
    app.setBg("#7b9095", override=False, tint=False)
    app.setSize(200,100)

    def on_button_pressed_record(title, app=app):
        print('Button with title {} pressed!'.format(title))
        app.removeButton("Record start", app.on_button_pressed_record)
        app.removeButton("pause",app.on_button_pressed_pause)
        app.addButton("Record stop", app.on_button_pressed_record_done)
        Record.start_recording()


    def on_button_pressed_record_done(title, app=app):
        print('Button with title "{}" pressed!'.format(title))
        app.removeButton("Record stop", app.on_button_pressed_record_done)
        app.addButton("Record start", app.on_button_pressed_record)
        app.addButton("pause", app.on_button_pressed_pause)
        Record.stop()

    def on_button_pressed_pause(title, app=app):
        print('Button with title "{}" pressed!'.format(title))
        app.removeButton("pause", app.on_button_pressed_pause)
        app.removeButton("Record start", app.on_button_pressed_record)
        app.addButton("un-pause", app.on_button_pressed_unpause)

    def on_button_pressed_unpause(title, app=app):
        print('Button with title "{}" pressed!'.format(title))
        app.removeButton("un-pause", app.on_button_pressed_unpause)
        app.addButton("Record start", app.on_button_pressed_record)
        app.addButton("pause", app.on_button_pressed_pause)
        Record.play_recording()

    app.addButton("Record start", on_button_pressed_record)
    app.addButton("pause", on_button_pressed_pause)

    app.go()
