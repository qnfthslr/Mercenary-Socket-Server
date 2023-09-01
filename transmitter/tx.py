import time

from transmitter.message_queue.manager import TransmitterCommandDataQueue

from datetime import datetime as dt


class Transmitter:
    def __init__(self):
        print("Transmitter Constructor")
        self.transmitter_command_data_queue = TransmitterCommandDataQueue()

    def transmit_command(self, client_socket, client_address):
        print("transmit_command client_address: ", client_address)
        while True:
            with client_socket:
                data = self.transmitter_command_data_queue.get()
                if data is None:
                    time.sleep(0.05)
                    continue

                if isinstance(data, tuple):
                    string_data = ' '.join(map(str, data))
                    print('{} command transmit [{}] from {}'.format(dt.now(), string_data, client_address[0]))
                    client_socket.sendall(string_data.encode())
                else:
                    print("Something wrong in command")

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
