import paho.mqtt.client as mqtt
import time

from pause import on_leave, send_retain
broker, port = "mqtt.item.ntnu.no", 1883
MQTT_TOPIC_INPUT = 'team8/pause'

from threading import Thread

class MQTT_Client_1:
    def on_message(self, client, userdata, msg):
        print("on_message(): message: {}".format(msg.payload))
        #self.client.disconnect()

    def start(self, broker, port):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)
        

        on_leave(self, MQTT_TOPIC_INPUT)
 
        self.client.subscribe(MQTT_TOPIC_INPUT)

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

    
def main():
    myclient = MQTT_Client_1()
    myclient.start(broker, port)
    
    
main()