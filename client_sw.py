import argparse, sys, socket
import hashlib
import pickle
import time
from typing import List


def get_options(cmd_args=None):
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


def read_file(file, size=1400):  # Read particular number of bytes from file
    with open(file, 'rb') as f:
        data_segments = list()
        while True:
            data = f.read(size)
            if not data:
                break
            data_segments.append(data)
        return data_segments


args = get_options(sys.argv[1:])

data_segments = read_file(args.file)
total_packets = len(data_segments)
received_acks = list()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)
maxTransmissions = 10000
retransmissionCounter = 0

current_packet_number = 0

while current_packet_number < total_packets:
    current_data = data_segments[current_packet_number]
    checksum = hashlib.md5(current_data).hexdigest()

    packet_to_send = pickle.dumps([current_packet_number, total_packets, current_data, checksum])
    try:
        sock.sendto(packet_to_send, (args.address, args.port))
        print(f"Packet {current_packet_number} sent out of {total_packets - 1}. Waiting for Ack")
        ack, _ = sock.recvfrom(1504)
        ack = pickle.loads(ack)
        if "BIT ERROR" not in ack[1]:
            print(f"Data packet {ack[0]} received by Server without errors")
            current_packet_number += 1


    except socket.timeout:
        if retransmissionCounter == maxTransmissions:
            print(f"Packet {current_packet_number} has not been received by server")
            print("Max retransmissions reached")
            break
        else:
            print(
                f"Packet {current_packet_number} has not been received by server. Retransmission {retransmissionCounter + 1} of {maxTransmissions}")
            sock.sendto(packet_to_send, (args.address, args.port))
            retransmissionCounter += 1

print("Transmission complete")
