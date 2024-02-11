import argparse, sys, socket
import os
import pickle


def getOptions(cmd_args=None):
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


def startServer(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.address, args.port))
    print("Server is listening")
    return sock

def receiveData(sock, file_path):
    global expectedCounter
    end = False
    data, address = sock.recvfrom(1024)
    data = pickle.loads(data)
    endFlag = data[2]
    if endFlag == 1:
        end = True
        print("Transmission done")
        return end
    else:
        message = data[1]
        receivedCounter = data[0]                # Received counter

        if expectedCounter == receivedCounter:
            with open(file_path, 'ab+') as f:
                f.write(message)
            expectedCounter += 1

        print(f"Sending Acknowledgement for packet {receivedCounter}")
        sock.sendto(pickle.dumps([data[0], 'ACK']), address)
    return end



args = getOptions(sys.argv[1:])
current_dir = os.getcwd()
file_path = os.path.join(current_dir, 'read_test')
sock = startServer(args)

expectedCounter = 0
end = False
while end == False:
    end = receiveData(sock, file_path)
sock.close()



