import socket


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
                callback(message.decode())

        except KeyboardInterrupt:
            exit()


class UDPClient:
    """UDP client sending messages to the stats visualization"""
    def __init__(self, remote_address, remote_port):
        self.address = remote_address
        self.port = remote_port

        # Create a datagram socket
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_message(self, message):
        self.udp_socket.sendto(str.encode(message), (self.address, self.port))
