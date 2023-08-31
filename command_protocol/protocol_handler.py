class CommandProtocolHandler:
    def __init__(self):
        self.protocol_map = {}

    def add_protocol_map(self, protocol_number, function):
        self.protocol_map[protocol_number] = function

    def handle_protocol(self, protocol_number, data):
        if protocol_number in self.protocol_map:
            function = self.protocol_map[protocol_number]
            result = function(data)
            return result
        else:
            return "No function found for the given protocol number."


# 프로토콜 번호와 처리할 데이터 기반 동작
#protocol_number = 333
#data = "Some data"
#result = handler.handle_protocol(protocol_number, data)
#print(result)
