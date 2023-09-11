import socket as sk
import multiprocessing as mp
from datetime import datetime as dt
import logging

import socket
from time import sleep

import os
import importlib

script_directory = os.path.dirname(__file__)
print("socket_server script_directory: ", script_directory)

module_path = "./receiver"
absolute_module_path = os.path.abspath(os.path.join(script_directory, module_path))
relative_module_path = os.path.relpath(absolute_module_path, os.path.abspath(os.getcwd()))
relative_rx_module_path_for_importlib = relative_module_path.replace(os.path.sep, ".").lstrip(".")
relative_rx_module_path_for_importlib += ".rx"
print("relative_rx_module_path_for_importlib: ", relative_rx_module_path_for_importlib)

receiver_module = importlib.import_module(relative_rx_module_path_for_importlib)
#socket_server_module = importlib.import_module(relative_module_path_for_importlib)
#from receiver.rx import Receiver

module_path = "./transmitter"
absolute_module_path = os.path.abspath(os.path.join(script_directory, module_path))
relative_module_path = os.path.relpath(absolute_module_path, os.path.abspath(os.getcwd()))
relative_tx_module_path_for_importlib = relative_module_path.replace(os.path.sep, ".").lstrip(".")
relative_tx_module_path_for_importlib += ".tx"
print("relative_tx_module_path_for_importlib: ", relative_tx_module_path_for_importlib)

transmitter_module = importlib.import_module(relative_tx_module_path_for_importlib)
#from transmitter.tx import Transmitter

import signal
import time


class SocketServer:
    def __init__(self, host, port):
        print("SocketServer Constructor")
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None

        self.receiver = None
        self.receiver_process = None
        self.receiver_pid = None

        self.transmitter = None
        self.transmit_process = None
        self.transmitter_pid = None
        self.logger = self.setup_logging()

        self.pid = None
        print("Finish SocketServer Constructor")

    def get_receiver(self):
        return self.receiver

    def get_receiver_process(self):
        return self.receiver_process

    def get_receiver_pid(self):
        return self.receiver_pid

    def get_transmitter(self):
        return self.transmitter

    def get_transmit_process(self):
        return self.transmit_process

    def get_transmitter_pid(self):
        return self.transmitter_pid

    def get_main_socket_pid(self):
        return self.pid

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        return logging.getLogger(__name__)

    def start(self, fastapi_queue, socket_server_queue, pid_queue):
        print('server started {}'.format(dt.now()))
        #self.logger.debug('server started {}'.format(dt.now()))

        if self.server_socket:
            try:
                fileno = self.server_socket.fileno()
                print(f"Socket is open with fileno: {fileno}")
            except socket.error:
                print("Socket is closed")
        else:
            print("Socket is not initialized")

        def sigint_socket_handler(signum, frame):
            print("Main Socket Received SIGINT")
            #self.receiver_process.terminate()
            #self.transmit_process.terminate()
            self.server_socket.close()
            #self.client_socket.close()
            #self.server_socket = None
            print("Finish to process SIGINT")

        signal.signal(signal.SIGINT, sigint_socket_handler)

        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as self.server_socket:
            self.server_socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

            try:
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(1)

                self.receiver = receiver_module.Receiver()
                self.transmitter = transmitter_module.Transmitter()

                self.pid = os.getpid()

                print('{} created main socket process {}'.format(dt.now(), self.pid))
                #self.logger.debug('{} created main socket process {}'.format(dt.now(), self.pid))
                self.server_socket.setblocking(False)

                while True:
                    try:
                        self.client_socket, client_address = self.server_socket.accept()
                        self.client_socket.setblocking(False)
                        print('{} received data from {}'.format(dt.now(), client_address[0]))
                        #self.logger.debug('{} received data from {}'.format(dt.now(), client_address[0]))
                        # TODO: 현재 여기 부분 소켓 생성 이후 루프 돌면서 지속적으로 생성됨 (개선 필요함)
                        self.receiver_process = mp.Process(target=self.receiver.receive_response,
                                                           args=(self.client_socket, client_address, pid_queue, ))
                        #self.receiver_pid = self.receiver_process.pid
                        self.receiver_process.daemon = False
                        self.receiver_process.start()
                        self.receiver_pid = self.receiver_process.pid

                        print('{} created receiver process {}'.format(dt.now(), self.receiver_process.pid))
                        #self.logger.debug('{} created receiver process {}'.format(dt.now(), self.receiver_process.pid))

                        self.transmit_process = mp.Process(target=self.transmitter.transmit_command,
                                                           args=(self.client_socket, client_address, pid_queue, ))
                        #self.transmitter_pid = self.transmitter.get_pid()
                        #self.transmitter_pid = self.transmit_process.pid
                        self.transmit_process.daemon = False
                        self.transmit_process.start()
                        self.transmitter_pid = self.transmit_process.pid

                        print('{} created transmitter process {}'.format(dt.now(), self.transmit_process.pid))
                        #self.logger.debug('{} created transmitter process {}'.format(dt.now(), self.transmit_process.pid))

                    except socket.error:
                        sleep(0.5)

            except Exception as e:
                self.logger.debug(e)
                self.kill_all_process()
            except KeyboardInterrupt:
                print('server stopped')
                #self.logger.debug('server stopped')
                self.kill_all_process()
            finally:
                self.kill_all_process()

    def kill_all_process(self):
        for p in mp.active_children():
            print('pid : {} terminated'.format(p.pid))
            #self.logger.debug('pid : {} terminated'.format(p.pid))
            p.terminate()
            p.join()

if __name__ == '__main__':
    server = SocketServer('0.0.0.0', 33333)
    server.start()
