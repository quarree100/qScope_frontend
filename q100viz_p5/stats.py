import udp


class Stats:
    def __init__(self, udp_address, udp_port):
        # set up UDP client to talk to stats viz
        self.udp_client = udp.UDPClient(udp_address, udp_port)

    def send_max_values(self, max_values, min_values):
        init = "init\n" + "\n".join(map(str, max_values + min_values))
        self.udp_client.send_message(init)
