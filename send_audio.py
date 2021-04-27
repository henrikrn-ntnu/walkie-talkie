import time
import paho.mqtt.client as paho
import hashlib


broker = "mqtt.item.ntnu.no"
# filename="DSCI0027.jpg"
filename = "blah-blah-blah.wav"  # file to send
#filename = "test.wav"
topic = "team8/send"
qos = 1
data_block_size = 5000000
fo = open(filename, "rb")
fout = open("recieved2.wav", "wb")  # use a different filename


# for outfile as I'm rnning sender and receiver together
def process_message(msg):
    """ This is the main receiver code
    """
    if len(msg) == 200:  # is header or end
        msg_in = msg.decode("utf-8")
        msg_in = msg_in.split(",,")
        if msg_in[0] == "end":  # is it really last packet?
            #in_hash_final = in_hash_md5.hexdigest()
            return False
        else:
            if msg_in[0] != "header":
                in_hash_md5.update(msg)
                return True
            else:
                return False
    else:
        in_hash_md5.update(msg)
        return True


# define callback
def on_message(client, userdata, message):
    if process_message(message.payload):
        fout.write(message.payload)


def on_publish(client, userdata, mid):
    client.puback_flag = True


def wait_for(client, msgType, period=0, wait_time=10, running_loop=False):
    client.running_loop = running_loop  # if using external loop
    while True:
        if msgType == "PUBACK":
            if client.on_publish:
                if client.puback_flag:
                    return True

        if not client.running_loop:
            client.loop(.00)  # check for messages manually
    return True


def send_header(filename):
    header = "header" + ",," + filename + ",,"
    header = bytearray(header, "utf-8")
    header.extend(b',' * (200 - len(header)))
    print(header)
    c_publish(client, topic, header, qos)


def send_end(filename):
    #end = "end" + ",," + filename + ",," + out_hash_md5.hexdigest()
    end = "end" + ",," + filename + ",,"
    end = bytearray(end, "utf-8")
    end.extend(b',' * (200 - len(end)))
    print(end)
    c_publish(client, topic, end, qos)


def c_publish(client, topic, out_message, qos):
    client.publish(topic, out_message, qos)  # publish
    #if res == 0:  # published ok
    if wait_for(client, "PUBACK", running_loop=True):
        client.puback_flag = False  # reset flag
    else:
        raise SystemExit("not got puback so quitting")


client = paho.Client(
    "client-001")  # create client object client1.on_publish = on_publish                          #assign function to callback client1.connect(broker,port)                                 #establish connection client1.publish("data/files","on")
######
client.on_message = on_message
client.on_publish = on_publish
client.puback_flag = False  # use flag in publish ack
#####
print("connecting to broker ", broker)
client.connect(broker)  # connect
client.loop_start()  # start loop to process received messages
print("subscribing ")
client.subscribe(topic)  # subscribe
start = time.time()
print("publishing ")
send_header(filename)
Run_flag = True
count = 0
##hashes
out_hash_md5 = hashlib.md5()
in_hash_md5 = hashlib.md5()

while Run_flag:
    chunk = fo.read(data_block_size)  # change if want smaller or larger data blcoks
    if chunk:
        out_hash_md5.update(chunk)
        out_message = chunk
        c_publish(client, topic, out_message, qos)

    else:
        #send hash
        out_message = out_hash_md5.hexdigest()
        send_end(filename)
        client.publish("team", out_message, qos=1)  # publish
        Run_flag = False
time_taken = time.time() - start
print("took ", time_taken)
client.disconnect()  # disconnect
client.loop_stop()  # stop loop
fout.close()  # close files
fo.close()