from enum import Enum


class MessageType(Enum):
    Empty = 0
    Add = 1
    Ping = 2
    ACK = 3


class Message:
    def __init__(self):
        self.type: MessageType = MessageType.Empty


class AddRouterMessage(Message):
    def __init__(self, router_info):
        super().__init__()
        self.type = MessageType.Add
        self.router_info = router_info


class PingMessage(Message):
    def __init__(self, start_node_id: int, finish_node_id: int):
        super().__init__()
        self.type = MessageType.Ping
        self.start_node = start_node_id
        self.finish_node = finish_node_id
        self.previous_node = start_node_id

    def mark(self, current_node: int):
        self.previous_node = current_node


class ACKMessage(PingMessage):
    def __init__(self, start_node_id: int, finish_node_id: int, router_info):
        super().__init__(start_node_id, finish_node_id)
        self.type = MessageType.ACK
        self.router_info = router_info

    def mark(self, current_node: int):
        self.previous_node = current_node