import multiprocessing as mp


class TransmitterCommandDataQueue:
    def __init__(self):
        self.message_queue = mp.Queue()

    def put(self, response):
        self.message_queue.put(response)

    def get(self):
        return self.message_queue.get()

    # 자원 해제
    def close(self):
        self.message_queue.close()

    # 태스크 동작을 보장
    def join(self):
        self.message_queue.join()


if __name__ == "__main__":
    transmitter_command_data_queue = TransmitterCommandDataQueue()

    transmitter_command_data_queue.put(333)
    print("receiver response queue data: ", transmitter_command_data_queue.get())

    transmitter_command_data_queue.close()
