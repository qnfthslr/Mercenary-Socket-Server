import time

from transmitter.message_queue.manager import TransmitterCommandDataQueue

from datetime import datetime as dt


class Transmitter:
    def __init__(self):
        print("Transmitter Constructor")
        self.transmitter_command_data_queue = TransmitterCommandDataQueue()

    def transmit_command(self, client_socket, client_address):
        print("client_address: ", client_address)
        while True:
            with client_socket:
                if self.transmitter_command_data_queue.get() is None:
                    time.sleep(0.05)
                    continue

                data = self.transmitter_command_data_queue.get()

                print('{} command transmit [{}] from {}'.format(dt.now(), data, client_address[0]))

                client_socket.sendall(data.encode())

    def put_command_data(self, command, data):
        print("put_command_data")

        message = (command, data)
        self.transmitter_command_data_queue.put(message)

    def get_command_data(self):
        print("get_command_data")

        return self.transmitter_command_data_queue.get()


if __name__ == "__main__":
    transmitter = Transmitter()

    transmitter.put_command_data(333, "화가 난다")
    print("transmitter command data queue: ", transmitter.get_command_data())
