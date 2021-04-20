
import paho.mqtt.client as mqtt


def on_leave(self, TOPIC): 
    print("on_leave!!!!!!!!!" )
    self.client.publish(TOPIC,None,0, True,None )
    self.client.disconnect()



def send_retain(self, TOPIC,messages):
     self.client.publish(TOPIC,messages,0, True,None )

