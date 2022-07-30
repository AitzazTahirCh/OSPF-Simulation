from server import Server
from router import Router
import multiprocessing as mp


class Net:
    MAX_ROUTERS_COUNT = 15
    ROUTERS_RANGE = 0.25

    def __init__(self):

        self.routers = {}
        self.routerStates = mp.Array('i', self.MAX_ROUTERS_COUNT)
        self.edge_list = []

        self._curr_id = 0
        self.id_free_list = [True] * self.MAX_ROUTERS_COUNT
        self.queue_list = []
        for i in range(self.MAX_ROUTERS_COUNT):
            self.queue_list.append(mp.Queue())

        self._server = Server(self.queue_list)



    def add_router(self, x, y):
        free_id = self._find_free_id()
        if free_id == -1:
            print('There are no place for new routers, max count:', self.MAX_ROUTERS_COUNT)
            return

        self._curr_id = free_id
        self.id_free_list[self._curr_id] = False

        # add edge
        for router_id, router in self.routers.items():
            if router.meta.range(x, y) <= self.ROUTERS_RANGE:
                self.edge_list.append([router_id, self._curr_id])

        new_router = Router(x, y, self.ROUTERS_RANGE, self._curr_id, self.queue_list, self.routerStates)
        self.routers[self._curr_id] = new_router

        self._server.turn_on_router(new_router)

    def ping_routers(self,  id_start_node: int, id_finish_node: int):
        if not self.id_free_list[id_start_node] and not self.id_free_list[id_finish_node]:
            self._server.ping_routers(id_start_node, id_finish_node)
        else:
            print("Can not ping routers, wrong id")

    def delete_router(self):
        pass

    def _find_free_id(self) -> int:
        free_id = self._curr_id
        count = 0
        while not self.id_free_list[free_id]:
            free_id = (free_id + 1) % self.MAX_ROUTERS_COUNT
            count += 1

            if count == self.MAX_ROUTERS_COUNT:
                return -1

        return free_id

    def terminate(self):
        for router in self.routers.values():
            router.terminate()

    def update_states(self):
        for router in self.routers.values():
            router.meta.define_state(self.routerStates[router.meta.id])