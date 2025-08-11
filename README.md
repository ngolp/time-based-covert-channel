# time-based-covert-channel

## General Information
1. This is a custom timing-based covert channel I made with Python.
2. It supports protocol hopping between two modes.
3. "Window Mode" is a rate/throughput covert channel, measuring how many packets are received within a window of time to encode a 0 bit or 1 bit.
4. "Threshold Mode" is an interpacket timing covert channel, measuring the time delta between two received packets to encode a 0 bit or 1 bit.
5. Both the sender and receiver use an equally seeded deterministic random number generator to randomly switch between these two modes, further obfuscating covert channel network traffic among other network traffic.
6. Because this covert channel is purely time-based, it is protocol agnostic and suitable for a variety of network protocols. For simplicity, we use HTTP packets built in the sender's _build_http_packet()_ function (modeled after captured packets of me scrolling through youtube).

<img width="975" height="517" alt="image" src="https://github.com/user-attachments/assets/7d62fcb4-280d-4b29-979f-fbd66645eb6d" />

## Configuration
1. Download the files from this repository (sender.py, receiver.py, and secretdata.txt)
2. Open sender.py, you'll find configuration settings relating to window mode (time window duration, and number of packets to send within that window) and threshold mode (interpacket time threshold). You'll also find connection settings and the deterministic random number generator's initialization. Customize these settings to change the behavior of the sender.

<img width="945" height="437" alt="image" src="https://github.com/user-attachments/assets/92a38f17-0a93-4c9e-9f65-756cadaed555" />

3. Open receiver.py, you'll find configuration settings relating to window mode (number of packets determining 0 bit or 1 bit, and the time window duration) and threshold mode (interpacket time threshold). You'll also find network connection settings, a debug mode which shows additional timing information, and the deterministic random number generator's initialization. Customize these settings to change the behavior of the receiver.

<img width="912" height="565" alt="image" src="https://github.com/user-attachments/assets/1d63999e-9898-49e3-bb29-1d77e49e1491" />

## Channel Usage
1. Using the covert channel is simple. First, start the receiver with _python3 receiver.py_.

<img width="458" height="40" alt="image" src="https://github.com/user-attachments/assets/9e03ea1d-c329-4311-b8f6-cb878eb1d074" />

2. Ensure that secretdata.txt and sender.py are in the same directory. Run sender.py with _python3 sender.py_ and it will begin to send data from secretdata.txt over to the receiver.

<img width="501" height="405" alt="image" src="https://github.com/user-attachments/assets/f99fefaf-7370-4a69-b005-e61a186084e5" />

3. The receiver will measure the packet timing information to receive bits, displaying the message one byte at a time as it receives it.

<img width="468" height="455" alt="image" src="https://github.com/user-attachments/assets/a081efce-3837-4d31-99b0-396642229278" />

## Next Steps (for when I have more time)
1. Use the pseudo-random number generator to randomize window mode and threshold mode configuration settings.
2. Use the pseudo-random number generator to randomize the protocol used for communication. It's not ideal to stick with just HTTP.
3. Use the pseudo-random number generator to randomize the actual packet contents being sent. Right now, we send exactly the same packet through the network, which could be suspicious.
