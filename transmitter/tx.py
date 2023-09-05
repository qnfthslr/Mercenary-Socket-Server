import multiprocessing
import os
import queue
import signal
import socket
import time

from transmitter.message_queue.manager import TransmitterCommandDataQueue

from datetime import datetime as dt

try:
    from app.system_queue.queue import socket_server_queue
except ImportError:
    socket_server_queue = multiprocessing.Queue()


class Transmitter:
    def __init__(self):
        print("Transmitter Constructor")
        self.transmitter_command_data_queue = TransmitterCommandDataQueue()

    def get_pid(self):
        return self.pid

    def transmit_command(self, client_socket, client_address, pid_queue):
        print("transmit_command client_address: ", client_address)
        pid_queue.put(("tx", os.getpid()))

        def sigint_transmit_handler(signum, frame):
            print("TX Received SIGINT")
            client_socket.close()
            #self.server_socket = None
            print("Finish to process SIGINT")

        signal.signal(signal.SIGUSR1, sigint_transmit_handler)

        while True:
            with client_socket:
                try:
                    from_fastapi_data = socket_server_queue.get()
                    print("from fastapi data: ", from_fastapi_data[0], from_fastapi_data[1])
                    # data = self.transmitter_command_data_queue.get()
                    if from_fastapi_data[0] is None:
                        time.sleep(0.5)
                        continue

                    if isinstance(from_fastapi_data, tuple):
                        string_data = ' '.join(map(str, from_fastapi_data))
                        print('{} command transmit [{}] from {}'.format(dt.now(), string_data, client_address[0]))
                        client_socket.sendall(string_data.encode())
                    else:
                        print("Something wrong in command")

                    exit()

                except queue.Empty:
                    time.sleep(0.5)

                except socket.error:
                    time.sleep(0.5)
                    # client_socket.close()
                    # print("Socket closed due to error")
                    # break

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
