import socket


class UDPServer:
    def __init__(self, address, port, buffer_size):
        self.address = address
        self.port = port
        self.buffer_size = buffer_size

    def listen(self):
        try:
            # Create a datagram socket
            udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            # Bind to address
            udp_socket.bind((self.address, self.port))

            print("UDP server up and listening")

            # Listen for incoming datagrams
            while True:
                message, address = udp_socket.recvfrom(self.buffer_size)

                print("Message from Client: {}".format(message))
                print("Client IP Address: {}".format(address))
        except KeyboardInterrupt:
            exit()
