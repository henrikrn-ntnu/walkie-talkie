import logging
import hashlib

'''
Setting global variables
'''
data_block_size = 500000
WAVE_INPUT_FILENAME = ''
file=''
out_hash_md5 = hashlib.md5()
in_hash_md5 = hashlib.md5()


'''
DEBUG
'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

'''
Defining packet headers for the receive logic to make it possible to build the correct file at the receiver
'''
def packet_start(filename):
    header = "start" + ",," + filename + ",,"
    header = bytearray(header, "utf-8")
    header.extend(b',' * (200 - len(header)))
    return header

def packet_stop(filename):
    header = "stop" + ",," + filename + ",,"
    header = bytearray(header, "utf-8")
    header.extend(b',' * (200 - len(header)))
    return header

'''
Splitting the .wav-file into smaller data packets to be published to the broker. Run flag is used to send start and end in the packet header.
'''
def create_packets(WAVE_OUTPUT_FILENAME):
    logger.debug('Start transforming audiofile to packets')
    run_flag = True
    file = open(WAVE_OUTPUT_FILENAME, 'rb')
    packet_list = []
    header = packet_start(WAVE_OUTPUT_FILENAME)
    packet_list.append(header)
    logger.debug('Appended header to packet list')
    while run_flag:
        buffer = file.read(data_block_size)
        if buffer:
            out_hash_md5.update(buffer)
            out_message = buffer
            packet_list.append(out_message)
            logger.debug('Appended out_message to packet list')
        else:
            out_message = out_hash_md5.hexdigest()
            end = packet_stop(WAVE_OUTPUT_FILENAME)
            packet_list.append(end)
            logger.debug('Appended end to packet list')
            run_flag = False
    file.close()
    logger.debug('Audiofile transformed to packets ready to send')
    return packet_list