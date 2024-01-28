import socket, pickle, argparse, time, signal
import sys
import hashlib

WINDOW_SIZE = 10

hasher = hashlib.md5()


# parser for receiving network parameters
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


# function to calculate checksum. Note that the data has to be encoded before hashing
def findCheckSum(data):
    hasher.update(data)
    return hasher.hexdigest()


# function to handle signals
def signal_handler(signal_number, frame):
    print(f" Received signal{signal_number}. Exiting")
    sys.exit(1)


# Starting the server to receive data
def startServer(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.address, args.port))
    print("Server is listening")
    return sock

# Receiving data from the client
def receiveData(sock):
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
        print(f"Received packet {data[0]} from window")
        # Send Acknowledgement
        sock.sendto(pickle.dumps([data[0], 'ACK']), address)

        # To do
        # Reorder packets in case of packet loss
        # ....

        # Write to file
        with open('/home/prapul/client_server/read_file', 'ab+') as f:
            f.write(message)
        return end






# Main function
def main(cmd_args):
    args = getOptions(cmd_args)
    sock = startServer(args)
    end = False
    while end == False:
        end = receiveData(sock)
    sock.close()

if __name__ == "__main__":
    main(sys.argv[1:])
