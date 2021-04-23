import paho.mqtt.client as mqtt

topic = "/voice/"

#Die Variablen sind bei mir im Skript entsprechend angepasst 
user = "user"
pw = "passwort"
host = "X.cloudmqtt.com"
port = 116123

def send_msg(sound_file):
   mqttc = mqtt.Client()

    mqttc.on_message = on_message

    mqttc.username_pw_set(user, pw)
    mqttc.connect(host, port)

    f = open("name.wav", "rb")
    imagestring = f.read()
    f.close()
    byteArray = bytearray(imagestring)

    mqttc.publish(topic, byteArray)

    rc = 0

    while rc == 0:
        rc = mqttc.loop()