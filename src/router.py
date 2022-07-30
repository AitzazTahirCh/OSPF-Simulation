import multiprocessing as mp
from typing import Dict, List
from ospf_graph import Graph
from messages import *
from queue import Empty

class RouterStateType(Enum):
    Default = 0
    Transits = 1
    FinishNode = 2

class MetaRouter:
    def __init__(self, x: float, y: float, max_range: float, id_r: int):
        self.x = x
        self.y = y
        self.max_range = max_range
        self.id = id_r
        self.state = RouterStateType.Default

    def range(self, x_r2: float, y_r2: float) -> float:
        return ((self.x - x_r2) ** 2 + (self.y - y_r2) ** 2) ** 0.5

    def define_state(self, enum_state: int):
        if enum_state == 1:
            self.state = RouterStateType.Transits
        elif enum_state == 2:
            self.state = RouterStateType.FinishNode
        else:
            self.state = RouterStateType.Default


class Router:
    def __init__(self, x: float, y: float, max_range: float, id_r: int, queue_list: float, router_states : mp.Array):
        self.meta: MetaRouter = MetaRouter(x, y, max_range, id_r)
        self._process = mp.Process(target=self.run_process, args=(self.meta, queue_list, router_states))

    @staticmethod
    def add_new_node(
            nodes: Dict[int, MetaRouter],
            new_node: MetaRouter,
            new_node_queue: mp.Queue,
            this_router_meta: MetaRouter,
            neighbor_node_queues: Dict[int, mp.Queue],
            graph: Graph
    ):
        vertex_list: Dict[int, float] = {}
        for node in nodes.values():
            dist = new_node.range(node.x, node.y)
            if dist <= new_node.max_range:
                vertex_list[node.id] = dist

        if new_node.range(this_router_meta.x, this_router_meta.y) <= this_router_meta.max_range:
            neighbor_node_queues[new_node.id] = new_node_queue

        nodes[new_node.id] = new_node
        graph.add_vertex(new_node.id, vertex_list)

    @staticmethod
    def run_process(this_router_meta: MetaRouter, queue_list: List[mp.Queue], router_states : mp.Array):
        # initialization
        this_router_queue = queue_list[this_router_meta.id]
        graph = Graph(this_router_meta.id)
        nodes: Dict[int, MetaRouter] = {this_router_meta.id: this_router_meta}
        neighbor_node_queues: Dict[int, mp.Queue] = {}
        ack_nodes: Dict[id, bool] = {}
        print('router ' + str(this_router_meta.id) + ' runs')
        # main loop
        while True:
            try:
                message: Message = this_router_queue.get(timeout=1)
            except Empty:
                router_states[this_router_meta.id] = 0  # RouterStateType.Default
            else:
                out_str = ''.join(['node ', str(this_router_meta.id),'; ', str(message.type),'; ',])
                if message.type == MessageType.Add:
                    router_states[this_router_meta.id] = 0  # RouterStateType.Default
                    new_node: AddRouterMessage = message
                    ack_nodes[new_node.router_info.id] = False  # no acknowledgment yet
                    Router.add_new_node(nodes, new_node.router_info, queue_list[new_node.router_info.id],
                                        this_router_meta, neighbor_node_queues, graph)
                    #out_str += str(ack_nodes) + 'gh:  ' + str(graph.destination_list) + ' '
                    for ack_node_id in ack_nodes.keys():
                        if not ack_nodes[ack_node_id] and graph.destination_list[ack_node_id] != -1:
                            ack_nodes[ack_node_id] = True
                            out_str += ' '.join(['ack to', str(ack_node_id), 'throw',
                                                 str(graph.destination_list[ack_node_id]), ': '])
                            ack = ACKMessage(this_router_meta.id, ack_node_id, this_router_meta)
                            queue_list[graph.destination_list[ack_node_id]].put(ack)

                else: # MessageType.ACK or MessageType.Ping
                    transit_info: ACKMessage = message
                    if transit_info.finish_node == this_router_meta.id:  # this node is final destination node
                        if message.type == MessageType.ACK:
                            if nodes.get(transit_info.start_node) is None:
                                ack_nodes[transit_info.router_info.id] = True
                                Router.add_new_node(nodes, transit_info.router_info, queue_list[transit_info.router_info.id],
                                                    this_router_meta, neighbor_node_queues, graph)
                                out_str += ' '.join(['get ack from', str(transit_info.start_node)])
                        router_states[this_router_meta.id] = 2  # RouterStateType.FinishNode

                    else:  # this node is just a transit node
                        if not graph.destination_list or graph.destination_list.get(transit_info.finish_node) is None:
                            #  cycling transits message put while not graph built with another messages
                            queue_list[this_router_meta.id].put(transit_info)
                        else:
                            router_states[this_router_meta.id] = 1 # RouterStateType.Transits
                            transit_info.mark(this_router_meta.id)
                            out_str += ' '.join(['transits to', str(transit_info.finish_node), 'throw',
                                                 str(graph.destination_list[transit_info.finish_node])])
                            queue_list[graph.destination_list[transit_info.finish_node]].put(transit_info)
                print(out_str)


    def start(self):
        self._process.start()

    def terminate(self):
        self._process.terminate()