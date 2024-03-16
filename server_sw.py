import argparse, sys, socket
import os
import pickle
import hashlib


def get_options(cmd_args=None):
    parser = argparse.ArgumentParser(
        prog="Enter details to send"
    )
    parser.add_argument(
        '-a', type=str, default='0.0.0.0', dest='address', required=True
    )
    parser.add_argument(
        '-p', type=int, default=8888, dest='port', required=True
    )
    return parser.parse_args()


args = get_options(sys.argv[1:])
current_dir = os.getcwd()
file_path = os.path.join(current_dir, 'read_test')

expected_packet_number = 0
received_data = list()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((args.address, args.port))
print("Server is listening")


def add_unique(number, data):
    if len(received_data)
        received_data[number] = data


while True:
    data, address = sock.recvfrom(1024)
    data = pickle.loads(data)  # [current_packet_number,total_packets,current_data,checksum]

    received_packet_number = data[0]
    total_packets = data[1]
    current_data = data[2]
    received_checksum = data[3]

    calculated_checksum = hashlib.md5(current_data).hexdigest()

    if calculated_checksum == received_checksum:
        print("Data received intact")
        print(f"Sending Ack for packet{received_packet_number}")
        sock.sendto(pickle.dumps([received_packet_number, 'ACK']), address)
        if received_packet_number == expected_packet_number:
            if len(received_data) <= received_packet_number:
                received_data.append(current_data)
                expected_packet_number += 1
    else:
        sock.sendto(pickle.dumps([received_packet_number, 'BIT ERROR']), address)

    if expected_packet_number == total_packets:
        break

print("Server has received all the packets")
sock.close()

with open(file_path, 'ab') as f:
    for data in received_data:
        f.write(data)