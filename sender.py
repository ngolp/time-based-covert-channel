import socket
import json
import time
import random

#----------------------------------------------------------------------------------------------------#
# GLOBALS
#----------------------------------------------------------------------------------------------------#

# MODE VALUES
WINDOW_MODE = 1                 # WINDOW MODE: If x < 5 packets delivered within 0.1 seconds, then 0; else 1
TIME_WINDOW = 0.1
PACKETS_SENT_FOR_ZERO = 4
PACKETS_SENT_FOR_ONE = 10
THRESHOLD_MODE = 2              # THRESHOLD MODE 2: if two packets delivered before 0.1 seconds, then 0; else 1
TIME_THRESHOLD = 0.1

# JOSH MODE (toggle this yourself!)
JOSH_MODE = False                # Prefixes all messages with "How we doin "

# CONNECTION SETTINGS
HOST = "127.0.0.1"
PORT = 1337

# seed the global deterministic RNG
SHARED_SECRET_SEED = b"NEVER_HARDCODE_YOUR_KEYS"
SEED_INT = int.from_bytes(SHARED_SECRET_SEED, 'big')
RNG = random.Random(SEED_INT)

#----------------------------------------------------------------------------------------------------#
# FUNCTIONS
#----------------------------------------------------------------------------------------------------#

# build a dummy http packet
def build_http_packet():

    dummy_json = {
            "zero": "cool",
            "acid": "burn",
            "phantom": "phreak",
    }
    path = "/youtubei/v1/player?prettyPrint=false"
    host = "youtube.com"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    content_type = "application/json; charset=UTF-8"
    body = json.dumps(dummy_json)
    connection = "keep-alive"

    request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: {connection}\r\n"
        f"\r\n"
        f"{body}"
    )

    return request.encode("utf-8")

# WINDOW MODE: If x < 5 packets delivered within 0.1 seconds, then 0; else 1
def send_packets_within_window(sock, pkt_num, window):
    start = time.time()
    packets_sent = 0

    # send the packets for the bit (as long as we're in the time window)
    while time.time() - start < window:
        if packets_sent < pkt_num:
            sock.sendall(build_http_packet())
            packets_sent += 1
        else: # if we've sent all the packets we need to send, break out of the loop
            break

    # wait remaining time, if any
    elapsed = time.time() - start
    if elapsed < window:
        time.sleep(window - elapsed)

# THRESHOLD MODE: if two packets delivered before 0.1 seconds, then 0; else 1
def send_packets_within_threshold(sock, bit, threshold):
    sock.sendall(build_http_packet()) # send packet 1
    if(bit):
        time.sleep(threshold)
    sock.sendall(build_http_packet()) # send packet 2

# send a one
def send_one(sock):
    if SELECTED_MODE == WINDOW_MODE:
        send_packets_within_window(sock, PACKETS_SENT_FOR_ONE, TIME_WINDOW)
    elif SELECTED_MODE == THRESHOLD_MODE:
        send_packets_within_threshold(sock, 1, TIME_THRESHOLD)
    
# send a zero
def send_zero(sock):
    if SELECTED_MODE == WINDOW_MODE:
        send_packets_within_window(sock, PACKETS_SENT_FOR_ZERO, TIME_WINDOW)
    elif SELECTED_MODE == THRESHOLD_MODE:
        send_packets_within_threshold(sock, 0, TIME_THRESHOLD)

#----------------------------------------------------------------------------------------------------#
# CLIENT START
#----------------------------------------------------------------------------------------------------#

# establish the socketed conn
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # open the file with secret data. If JOSH_MODE is enabled, prefix the message with "How we doin "
    secret_file = open("secretdata.txt")
    secret_data = b""
    if JOSH_MODE:
        secret_data = b"How we doin "
    secret_data += secret_file.read().encode('utf-8')
    print(secret_data)

    # main loop for client to send data
    total_bytes = len(secret_data) # 
    sent_bytes = 0
    sent_bits = 0
    while(True):
        # if we have sent all bytes, we're done
        if(sent_bytes >= total_bytes):
            sock.close()
            break

        # if we sent all bits in a byte, advance to next byte
        if(sent_bits > 7):
            sent_bytes = sent_bytes + 1
            sent_bits = 0
            continue

        # get the current byte and bit to send
        current_byte = secret_data[sent_bytes]
        current_bit = ((current_byte << sent_bits) & 0x80) >> 7

        SELECTED_MODE = RNG.randint(1, 2)
        if(current_bit == 0x01):
            print("sending one")
            send_one(sock)
        else:
            print("sending zero")
            send_zero(sock)

        time.sleep(0.05) # give the server a moment to process

        # send the next bit, and repeat the loop
        sent_bits = sent_bits + 1