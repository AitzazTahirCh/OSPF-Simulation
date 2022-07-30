from router import Router, MetaRouter
from typing import Dict, List
from messages import AddRouterMessage, PingMessage
import multiprocessing as mp


class Server:
    def __init__(self, queues_list: List[mp.Queue]):
        self.routers_info: Dict[int, MetaRouter] = {}
        self.queues_list: List[mp.Queue] = queues_list

    def turn_on_router(self, router: Router):
        router.start()  # Run the process

        new_router_meta = router.meta

        message = AddRouterMessage(new_router_meta)
        for current_router_meta in self.routers_info.values():
            self.queues_list[current_router_meta.id].put(message)

        self.routers_info[new_router_meta.id] = new_router_meta

    def ping_routers(self, id_start_node: int, id_finish_node: int):
        message = PingMessage(id_start_node, id_finish_node)
        self.queues_list[id_start_node].put(message)

    def turn_out_router(self):
        pass