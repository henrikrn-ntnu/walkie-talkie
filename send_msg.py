
import paho.mqtt.client as mqtt

topic = "/team8/send"

#Die Variablen sind bei mir im Skript entsprechend angepasst 
#user = "user"
#pw = "passwort"
host = "mqtt.item.ntnu.no"
port = 1883

def send_msg(sound_file):
    mqttc = mqtt.Client()

    mqttc.on_message = on_message

    #mqttc.username_pw_set(user)
    mqttc.connect(host, port)

    f = open(sound_file, "rb")
    imagestring = f.read()
    f.close()
    byteArray = bytearray(imagestring)

    mqttc.publish(topic, byteArray)

    rc = 0

    while rc == 0:
        rc = mqttc.loop()

send_msg("test.wav")