import os
import signal
import socket
import time

import importlib

script_directory = os.path.dirname(__file__)
print("rxq script_directory: ", script_directory)

module_path = "./message_queue"
absolute_module_path = os.path.abspath(os.path.join(script_directory, module_path))
relative_module_path = os.path.relpath(absolute_module_path, os.path.abspath(os.getcwd()))
relative_rxq_module_path_for_importlib = relative_module_path.replace(os.path.sep, ".").lstrip(".")
relative_rxq_module_path_for_importlib += ".manager"
print("relative_rxq_module_path_for_importlib: ", relative_rxq_module_path_for_importlib)

rxq_module = importlib.import_module(relative_rxq_module_path_for_importlib)

#from receiver.message_queue.manager import ReceiverResponseQueue

from datetime import datetime as dt


class Receiver:
    def __init__(self):
        print("Receiver Constructor")
        self.receiver_response_queue = rxq_module.ReceiverResponseQueue()

    def receive_response(self, client_socket, client_address, pid_queue):
        print("receive_response client_address: ", client_address)
        pid_queue.put(("rx", os.getpid()))

        def sigint_receiver_handler(signum, frame):
            print("RX Received SIGINT")
            client_socket.close()
            #self.server_socket = None
            print("Finish to process SIGINT")

        signal.signal(signal.SIGINT, sigint_receiver_handler)

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print("Client disconnected!")
                    client_socket.close()
                    break

                response_str = data.decode().strip()
                print('{} command received [{}] from {}'.format(dt.now(), response_str, client_address[0]))

                self.receiver_response_queue.put(response_str)
                time.sleep(0.5)

            except socket.error:
                time.sleep(0.5)
