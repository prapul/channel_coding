import socket, pickle, argparse, time
import sys
import hashlib

hasher = hashlib.md5()

WINDOW_SIZE = 10
timeout_period = 0.5


def getOptions(cmd_args=None):
    parser = argparse.ArgumentParser(
        prog="Enter details to send"
    )
    parser.add_argument(
        '-a', type=str, default='192.168.178.64', dest='address', required=True
    )
    parser.add_argument(
        '-p', type=int, default=8888, dest='port', required=True
    )
    parser.add_argument(
        '-f', type=str, default='./text', dest='file', required=True
    )
    return parser.parse_args()


def readFile(file):
    with open(file, 'rb') as f:
        content = f.read()
        return content


# Split the bytes to packets
def makePackets(content, packetSize=500):                     # 500 bytes of data in a packet which will be sent to the server
    packets = list()
    for i in range(0, len(content), packetSize):
        packets.append(content[i:i + packetSize])
    return packets


# Group packets into a window before sending
def fillWindow(packets, WINDOW_SIZE):
    window = list()
    for i in range(WINDOW_SIZE):
        window.append(packets[i])
    return window


# Sending Packets and maintaining Dictionary of sent packets
def sendPackets(window, sock, args, max_retransmission=5):
    sent_packets = dict()  # Keep track of sent packets and their Acknowledgements

    sock.settimeout(timeout_period)  # Set timeout for the socket

    # Check if it is a list or dictionary
    if isinstance(window, list):                                            # The window is a list by default
        for i, packet in enumerate(window):
            sock.sendto(pickle.dumps([i, packet, None]), (args.address, args.port))
            print(f"Sending packet {i} in window")
            sent_packets[i] = packet

    if isinstance(window, dict):                                            # The window is a dictionary in the end when number of packets to send is less than window size
        for key, value in window.items():
            sock.sendto(pickle.dumps([key, value, None]), (args.address, args.port))
            print(f"Retransmitting packet {key} in window")
            sent_packets[key] = value

    # Wait for Acknowledgements
    while sent_packets:
        try:
            data, addr = sock.recvfrom(1024)                  # 1024 is the buffer size
            ack_seq_number = pickle.loads(data)[0]

            # Mark the corresponding packet as Acknowledged
            if ack_seq_number in sent_packets:
                sent_packets.pop(ack_seq_number)

        except socket.timeout:
            max_retransmission -= 1
            if max_retransmission > 0:
                sendPackets(sent_packets, sock, args)
            else:
                print("Maximum retransmission attempts reached. Exiting")
                break


def main(cmd_args=None):
    args = getOptions(cmd_args)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # To do: Implement timeout
    # sock.settimeout(timeout_period)

    content = readFile(args.file)
    packets = makePackets(content)

    PACKET_COUNTER = 0
    PACKET_NUMBER = len(packets)

    # Send the number of packets to the server
    sock.sendto(pickle.dumps(PACKET_NUMBER), (args.address, args.port))

    print("Sending data and starting timer")
    start_time = time.time()

    while PACKET_COUNTER < PACKET_NUMBER:
        packet_list = list()
        for i in range(PACKET_COUNTER, min(PACKET_COUNTER + WINDOW_SIZE, PACKET_NUMBER)):      # packet_counter + window_size is the upper bound except in the end when number of packets to send is less than window size
            packet_list.append(packets[i])
        sendPackets(packet_list, sock, args)
        PACKET_COUNTER += WINDOW_SIZE

    # Send the last packet
    sock.sendto(pickle.dumps([None, None, 1]), (args.address, args.port))

    print("Transmission done")

    end_time = time.time()
    print(f"Transmission time: {end_time - start_time} seconds")

if __name__ == "__main__":
    main(sys.argv[1:])
