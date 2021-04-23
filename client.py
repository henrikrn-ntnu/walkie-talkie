from threading import Thread
import paho.mqtt.client as mqtt
import json


class Client:
    def __init__(self, id=""):
        self.id = id

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))
        self.client.publish("team", json.dumps({'message': 'hei','client_id': self.id}))

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))


    def start(self, broker, port):
        self.client = mqtt.Client(client_id=self.id)
        print("id: "+str(self.client._client_id))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        self.client.subscribe("team/"+self.id)
        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

broker, port = "mqtt.item.ntnu.no", 1883
myclient = Client(id="c2")
myclient.start(broker, port)