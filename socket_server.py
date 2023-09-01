import socket as sk
import multiprocessing as mp
from datetime import datetime as dt
import logging

from receiver.rx import Receiver
from transmitter.tx import Transmitter


class SocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None

        self.receiver = None
        self.receiver_process = None

        self.transmitter = None
        self.transmit_process = None
        self.logger = self.setup_logging()

    def get_receiver(self):
        return self.receiver

    def get_receiver_process(self):
        return self.receiver_process

    def get_transmitter(self):
        return self.transmitter

    def get_transmit_process(self):
        return self.transmit_process

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        return logging.getLogger(__name__)

    def handler(self, conn, address):
        with conn:
            data = conn.recv(1024)
            command_str = data.decode().strip()
            self.logger.debug('{} command received [{}] from {}'.format(dt.now(), command_str, address[0]))
            if len(data) > 0:
                resp = 'server: {} message received [{}] from {}'.format(dt.now(), command_str, address[0])
                conn.sendall(resp.encode())
                return

    def start(self):
        self.logger.debug('server started {}'.format(dt.now()))
        with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as self.server_socket:
            try:
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(1)

                self.receiver = Receiver()
                self.transmitter = Transmitter()
                while True:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.debug('{} received data from {}'.format(dt.now(), client_address[0]))
                    # TODO: 현재 여기 부분 소켓 생성 이후 루프 돌면서 지속적으로 생성됨 (개선 필요함)
                    self.receiver_process = mp.Process(target=self.receiver.receive_response, args=(client_socket, client_address))
                    self.receiver_process.daemon = True
                    self.receiver_process.start()

                    self.logger.debug('{} created process {}'.format(dt.now(), self.receiver_process.pid))

                    self.transmit_process = mp.Process(target=self.transmitter.transmit_command, args=(client_socket, client_address))
                    self.transmit_process.daemon = True
                    self.transmit_process.start()

                    self.logger.debug('{} created process {}'.format(dt.now(), self.transmit_process.pid))

            except Exception as e:
                self.logger.debug(e)
                self.kill_all_process()
            except KeyboardInterrupt:
                self.logger.debug('server stopped')
                self.kill_all_process()
            finally:
                self.kill_all_process()

    def kill_all_process(self):
        for p in mp.active_children():
            self.logger.debug('pid : {} terminated'.format(p.pid))
            p.terminate()
            p.join()

if __name__ == '__main__':
    server = SocketServer('0.0.0.0', 33333)
    server.start()
