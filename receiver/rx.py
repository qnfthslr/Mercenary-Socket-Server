import os
import signal
import socket
import time

from receiver.message_queue.manager import ReceiverResponseQueue

from datetime import datetime as dt


class Receiver:
    def __init__(self):
        print("Receiver Constructor")
        self.receiver_response_queue = ReceiverResponseQueue()

    def receive_response(self, client_socket, client_address, pid_queue):
        print("receive_response client_address: ", client_address)
        pid_queue.put(("rx", os.getpid()))

        def sigint_receiver_handler(signum, frame):
            print("RX Received SIGINT")
            client_socket.close()
            #self.server_socket = None
            print("Finish to process SIGINT")

        signal.signal(signal.SIGINT, sigint_receiver_handler)

        with client_socket:
            try:
                data = client_socket.recv(1024)
                response_str = data.decode().strip()
                print('{} command received [{}] from {}'.format(dt.now(), response_str, client_address[0]))

                self.receiver_response_queue.put(response_str)

            except socket.error:
                #client_socket.close()
                print("Receiver Socket closed due to error")
