import paho.mqtt.client as mqtt
from threading import Thread
import json

class ServerClient:
    def __init__(self):
        self.client_list = []

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.payload))
        
        message_as_string = msg.payload.decode("utf-8")
        message_as_json = json.loads(message_as_string)
        client_id = message_as_json["client_id"]
        self.update_client_list(client_id)

        for channel in self.client_list:
            if channel is not client_id:
                client_channel = "team/"+channel
                try:
                    # TODO: sende lydfilen (bytes? wav?)
                    self.client.publish(client_channel, msg.payload)
                except e:
                    print(e)

    def start(self, broker, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        self.client.subscribe("team")
        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

    def update_client_list(self, client):
        if client not in self.client_list:
            self.client_list.append(client)

    # TODO: def remove_client(self, client):




broker, port = "mqtt.item.ntnu.no", 1883
myclient = ServerClient()
myclient.start(broker, port)