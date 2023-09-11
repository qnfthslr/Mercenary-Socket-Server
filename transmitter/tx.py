import multiprocessing
import os
import queue
import signal
import socket
import time

import importlib

script_directory = os.path.dirname(__file__)
print("txq script_directory: ", script_directory)

module_path = "./message_queue"
absolute_module_path = os.path.abspath(os.path.join(script_directory, module_path))
relative_module_path = os.path.relpath(absolute_module_path, os.path.abspath(os.getcwd()))
relative_txq_module_path_for_importlib = relative_module_path.replace(os.path.sep, ".").lstrip(".")
relative_txq_module_path_for_importlib += ".manager"
print("relative_txq_module_path_for_importlib: ", relative_txq_module_path_for_importlib)

txq_module = importlib.import_module(relative_txq_module_path_for_importlib)
#from transmitter.message_queue.manager import TransmitterCommandDataQueue

from datetime import datetime as dt

try:
    from app.system_queue.queue import socket_server_queue
except ImportError:
    socket_server_queue = multiprocessing.Queue()


class Transmitter:
    def __init__(self):
        #print("Transmitter Constructor")
        self.transmitter_command_data_queue = txq_module.TransmitterCommandDataQueue()

    def get_pid(self):
        return self.pid

    def transmit_command(self, client_socket, client_address, pid_queue):
        #print(f"transmit_command client_address: {client_address}, client_socket: {client_socket}")
        pid_queue.put(("tx", os.getpid()))

        def sigint_transmit_handler(signum, frame):
            #print("TX Received SIGINT")
            client_socket.close()
            #self.server_socket = None
            #print("Finish to process SIGINT")

        signal.signal(signal.SIGUSR1, sigint_transmit_handler)

        while True:
            try:
                from_fastapi_data = socket_server_queue.get(False)
                print("from fastapi data: ", from_fastapi_data[0], from_fastapi_data[1])

                if from_fastapi_data[0] is None:
                    time.sleep(0.5)
                    continue

                if isinstance(from_fastapi_data, tuple):
                    string_data = ' '.join(map(str, from_fastapi_data))
                    client_socket.sendall(string_data.encode())
                    print('{} command transmit [{}] from {}'.format(dt.now(), string_data, client_address[0]))
                else:
                    print("Something wrong in command")

                time.sleep(0.5)

            except socket.error as e:
                print("Socket error:", e)
                time.sleep(0.5)

            except queue.Empty:
                #print("socket_server_queue empty")
                time.sleep(0.5)

            except Exception as ex:
                print("An error occurred:", ex)

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
