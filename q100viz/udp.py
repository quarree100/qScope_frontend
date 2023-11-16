import socket
from q100viz.devtools import devtools as devtools


class UDPServer:
    """UDP server receiving messages from the Cityscope scanner"""
    def __init__(self, address, port, buffer_size):
        self.address = address
        self.port = port
        self.buffer_size = buffer_size

    def listen(self, callback):
        try:
            # Create a datagram socket
            udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            # Bind to address
            udp_socket.bind((self.address, self.port))

            print("UDP server up and listening")

            # Listen for incoming datagrams
            while True:
                message, _ = udp_socket.recvfrom(self.buffer_size)

                if len(message) == self.buffer_size:
                    print("Warning: the UDP message may have been truncated")

                callback(message.decode())

                # print("receiving message at", self.port)
                # devtools.print_verbose(message, devtools.VERBOSE_MODE)

        except KeyboardInterrupt:
            exit()
