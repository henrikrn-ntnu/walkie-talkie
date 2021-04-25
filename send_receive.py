import time
import paho.mqtt.client as paho
import hashlib
from datetime import datetime


#Setting global variables
data_block_size = 5000000
WAVE_INPUT_FILENAME = ''
out_hash_md5 = hashlib.md5()
in_hash_md5 = hashlib.md5()

def receive_audiofile(payload):
    WAVE_INPUT_FILENAME = datetime.now().strftime("%H_%M_%S") + ".wav"
    file = open(WAVE_INPUT_FILENAME, 'wr')
    write_to_file(payload, file)
    file.close()
    return WAVE_INPUT_FILENAME
    
def send_audiofile(WAVE_OUTPUT_FILENAME):
    run_flag = True
    file = open(WAVE_OUTPUT_FILENAME, 'rb')
    buffer_list = []
    buffer_list.append(send_header(file))
    while run_flag:
        buffer = file.read(data_block_size)  # change if want smaller or larger data blcoks
        if buffer:
            out_hash_md5.update(buffer)
            out_message = buffer
            buffer_list.append(out_message)
        else:
            #send hash
            out_message = out_hash_md5.hexdigest()
            buffer_list.append(send_end(file))
            buffer_list.append(out_message)
            run_flag = False
    file.close()
    return buffer_list

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
def write_to_file(payload, file):
    if process_message(payload):
        file.write(payload)


def on_publish(client, userdata, mid):
    client.puback_flag = True


def wait_for(client, msgType, running_loop=False):
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
    return header


def send_end(filename):
    #end = "end" + ",," + filename + ",," + out_hash_md5.hexdigest()
    end = "end" + ",," + filename + ",,"
    end = bytearray(end, "utf-8")
    end.extend(b',' * (200 - len(end)))
    return end

def c_publish(client, topic, out_message, qos):
    client.publish(topic, out_message, qos)  # publish
    #if res == 0:  # published ok
    if wait_for(client, "PUBACK", running_loop=True):
        client.puback_flag = False  # reset flag
    else:
        raise SystemExit("not got puback so quitting")


