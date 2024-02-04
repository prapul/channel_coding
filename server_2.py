import socket, pickle, argparse, time, signal
import sys
import hashlib

WINDOW_SIZE = 10
hasher = hashlib.md5()

RECEIVED_COUNTER = 0
GLOBAL_dict = dict()      # Dictionary to store the received packets (Buffer)
TOTAL_PACKETS = 0

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
    data, address = sock.recvfrom(1024)
    TOTAL_PACKETS = pickle.loads(data)
    print("Received total number of packets to be sent -> ", TOTAL_PACKETS)
    return sock

# Receiving data from the client
def receiveData(sock):
    end = False
    data, address = sock.recvfrom(1024)
    data = pickle.loads(data)

    endFlag = data[2]
    if endFlag == None:
        message = data[1]
        print(f"Received packet {data[0]} from window")
        # Send Acknowledgement
        sock.sendto(pickle.dumps([data[0], 'ACK']), address)

        global GLOBAL_dict                # Using the global dictionary to store the received packets
        GLOBAL_dict[data[0]] = message    # Storing the received packets in the dictionary
        global RECEIVED_COUNTER
        RECEIVED_COUNTER += 1             # Keeping track of the number of packets received

        if (RECEIVED_COUNTER == TOTAL_PACKETS) or (len(GLOBAL_dict) == WINDOW_SIZE):    # If all the packets are received or the window is full
            GLOBAL_dict = dict(sorted(GLOBAL_dict.items()))                                     # Sort the dictionary
            with open('/home/prapul/client_server/read_file', 'ab+') as f:              # Write the received packets to a file
                for i in GLOBAL_dict:
                    f.write(GLOBAL_dict[i])
            GLOBAL_dict = dict()
            return end
        return end

    else:
        end = True
        print("Transmission done")
        return end





# Main function
def main(cmd_args):
    signal.signal(signal.SIGINT, signal_handler)     # Handling signals Ctrl+C
    args = getOptions(cmd_args)
    sock = startServer(args)
    end = False
    while end == False:
        end = receiveData(sock)
    sock.close()

if __name__ == "__main__":
    main(sys.argv[1:])
