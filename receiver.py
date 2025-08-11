import socket
import time
import random

#----------------------------------------------------------------------------------------------------#
# GLOBALS
#----------------------------------------------------------------------------------------------------#

# MODE SETTINGS
WINDOW_MODE = 1                 # WINDOW MODE: If x < 5 packets delivered within 0.1 seconds, then 0; else 1
WINDOW_BYTES = 5
TIME_WINDOW = 0.1
THRESHOLD_MODE = 2              # THRESHOLD MODE: if two packet delivered before 0.1 seconds, then 0; else 1
TIME_THRESHOLD = 0.1

# CONNNECTION SETTINGS
HOST = '0.0.0.0'
PORT = 1337
CONNECTION_TERMINATED = -1

# DEBUG MODE (toggle this yourself!)
DEBUG = False

# seed the global deterministic RNG
SHARED_SECRET_SEED = b"NEVER_HARDCODE_YOUR_KEYS"
SEED_INT = int.from_bytes(SHARED_SECRET_SEED, 'big')
RNG = random.Random(SEED_INT)

# global values for receiving bytes, one bit at a time
num_in_bits = 0
num_in_bytes = 0
in_bytes = []
in_bytes.append(0)

#----------------------------------------------------------------------------------------------------#
# FUNCTIONS
#----------------------------------------------------------------------------------------------------#

# WINDOW MODE: If x < 5 packets delivered within 0.1 seconds, then 0; else 1
def recv_bit_window_mode(conn, window):
    packets_received = 0
    buffer =b""
    conn.setblocking(False)
    
    # wait until we get our first packet to start the timer
    while(buffer == b""):
        try:
            in_data = conn.recv(1024)
            if in_data: # if we get data, start the timer, and collect the data
                start = time.time()
                buffer += in_data
                break
            elif len(in_bytes) > 1: # if no more data (after we've received initial data), end the connection
                return CONNECTION_TERMINATED
        except BlockingIOError:
            continue

    # receive the rest of the packets for the bit (as long as we're in the time window)
    while time.time() - start < window:
        try:
            in_data = conn.recv(1024) # receive the data
            if in_data:
                buffer += in_data # add data to buffer
        except BlockingIOError:
            continue

    # parse how many HTTPS packets we got and determine the bit
    packets_received = buffer.count(b"POST")
    bit = int(packets_received >= WINDOW_BYTES)
    if DEBUG:
        print(f"Packets received: {packets_received}")
        print(f"Interpreted bit: {bit}")
    return bit

# THRESHOLD MODE: if two packets delivered before 0.1 seconds, then 0; else 1
def recv_bit_threshold_mode(conn, threshold):
    conn.setblocking(False)

    # wait until we get our first packet to start the timer
    while(True):
        try:
            in_data = conn.recv(1024)
            if in_data: # if we get data, start the timer
                start = time.time()
                break
            elif len(in_bytes) != None: # if no more data (after we've received initial data), end the connection
                return CONNECTION_TERMINATED
        except BlockingIOError:
            continue

    # receive the second the packet
    in_data = None
    while (True):
        try:
            in_data = conn.recv(1024) # receive the data
        except BlockingIOError:
            if in_data != None: # if we have data (from the second packet), end the timer
                end = time.time()
                break

    elapsed = end - start
    bit = int(elapsed > threshold)
    if DEBUG:
        print(f"Elapsed time: {elapsed}")
        print(f"Interpreted bit: {bit}")
    return bit

# handles a TCP connection to receive a message
def handle_client(conn, addr):
    global num_in_bits, num_in_bytes, in_bytes, RNG

    # main loop for a specific conn
    while(True):
        # receive a bit
        SELECTED_MODE = RNG.randint(1, 2)
        if(SELECTED_MODE == WINDOW_MODE):
            in_bit = recv_bit_window_mode(conn, TIME_WINDOW)
        elif(SELECTED_MODE == THRESHOLD_MODE):
            in_bit = recv_bit_threshold_mode(conn, TIME_THRESHOLD)

        # if end of message, reseed the RNG for the next client and exit
        if (in_bit == CONNECTION_TERMINATED):
            RNG = random.Random(SEED_INT)
            print("end of message")
            return
        
        # if successfully got a bit, add it to our in_bytes]
        else:
            in_bytes[num_in_bytes] = in_bytes[num_in_bytes] | (in_bit << (7 - num_in_bits)) 
            num_in_bits += 1
            if(num_in_bits % 8 == 0) and (num_in_bits != 0):
                num_in_bits = 0
                num_in_bytes += 1
                in_bytes.append(0)

        # print the message (on every complete byte)
        if(num_in_bits == 0):
            print(bytes(bytearray(in_bytes)).decode("utf-8", errors="replace")) # python fuckery

# main loop for server
def server_loop():
    global num_in_bits, num_in_bytes, in_bytes
    # establish socketed connection
    print(f"[*] Listening on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            # service the connection
            conn, addr = s.accept()
            handle_client(conn, addr)

            # once connection finished (and message received), clear the buffer to receive the next message
            in_bytes = []
            in_bytes.append(0)
            num_in_bits = 0
            num_in_bytes = 0

#----------------------------------------------------------------------------------------------------#
# SERVER START
#----------------------------------------------------------------------------------------------------#

# start the server
if __name__ == "__main__":
    server_loop()
