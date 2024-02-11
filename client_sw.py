import argparse, sys, socket
import pickle
import time


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

def sendPackets(packets):
    pass

def makePackets(content, packetSize=500):                     # 500 bytes of data in a packet which will be sent to the server
    packets = list()
    for i in range(0, len(content), packetSize):
        packets.append(content[i:i + packetSize])
    return packets

args = getOptions(sys.argv[1:])
content = readFile(args.file)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)
maxTransmissions = 5
retransmissionCounter = 0

packets = makePackets(content)
numberOfPackets = len(packets)

packetCounter = 0
print("Start of transmission")

start_time = time.time()
while packetCounter < numberOfPackets:
    try:
        sock.sendto(pickle.dumps([packetCounter, packets[packetCounter], 0]), (args.address, args.port))
        data, addr = sock.recvfrom(1024)

        if pickle.loads(data)[0] == packetCounter:
            print(f"Packet {packetCounter} has been received by server")
            packetCounter += 1
            retransmissionCounter = 0
    except socket.timeout:
        if retransmissionCounter == maxTransmissions:
            print(f"Packet {packetCounter} has not been received by server")
            print("Max retransmissions reached")
            break
        else:
            print(f"Packet {packetCounter} has not been received by server. Retransmission {retransmissionCounter + 1} of {maxTransmissions}")
            sock.sendto(packets[packetCounter], (args.address, args.port))
            retransmissionCounter += 1

# Send end of transmission flag
sock.sendto(pickle.dumps([None, None, 1]), (args.address, args.port))
print("End of transmission")
end_time = time.time()
print(f"Time taken for transmisssion is {end_time-start_time}")
sock.close()







