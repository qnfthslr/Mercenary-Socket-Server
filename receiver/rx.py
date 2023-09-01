from receiver.message_queue.manager import ReceiverResponseQueue

from datetime import datetime as dt


class Receiver:
    def __init__(self):
        print("Receiver Constructor")
        self.receiver_response_queue = ReceiverResponseQueue()

    def receive_response(self, client_socket, client_address):
        print("receive_response client_address: ", client_address)
        with client_socket:
            data = client_socket.recv(1024)
            response_str = data.decode().strip()
            print('{} command received [{}] from {}'.format(dt.now(), response_str, client_address[0]))

            self.receiver_response_queue.put(response_str)
