from typing import Dict, List


class Graph:
    def __init__(self, first_node_id: int):
        self.vertices_list: Dict[int, Dict[int, float]] = {first_node_id: {}}

        # destination vertex id -> neighborhood (with which there is a connection) shorted path vertex id
        self.destination_list: Dict[int, int] = {}
        self.base_node_id = first_node_id

    def add_vertex(self, new_vertex_id: int, vertex_list: Dict[int, float]):
        # added new vertex to vertices in list
        for v_id in vertex_list.keys():
            self.vertices_list[v_id][new_vertex_id] = vertex_list[v_id]

        # added new vertex to vertices_list
        self.vertices_list[new_vertex_id] = vertex_list

        self._rebuild_track()

    def _rebuild_track(self):
        track_dict = self._dijkstra_tracks(self.base_node_id)
        track_dict.pop(self.base_node_id)
        for id_v in track_dict.keys():
            if track_dict[id_v]:  # not empty
                new_dist = track_dict[id_v][0]
            else:
                new_dist = -1
            self.destination_list[id_v] = new_dist

    def _dijkstra_tracks(self, start_vertex_id) -> Dict[int, List[int]]:  # returns tracks for each node
        # initialization
        distance_dict: Dict[int, float] = {}
        track_dict: Dict[int, List[int]] = {}
        for id_v in self.vertices_list.keys():
            distance_dict[id_v] = float("InF")
            track_dict[id_v] = []
        distance_dict[start_vertex_id] = 0

        while len(distance_dict) > 0:
            # find next node
            browsed_node_dist = min(distance_dict.values())
            browsed_node: int
            for id_v, dist in distance_dict.items():
                if dist == browsed_node_dist:
                    browsed_node = id_v
                    break
            distance_dict.pop(browsed_node)

            # find next neighborhood node
            for node in self.vertices_list[browsed_node].keys():
                if distance_dict.get(node) is None:  # visited
                    continue

                # calc new length (cost)
                new_cost = browsed_node_dist + self.vertices_list[browsed_node][node]
                if new_cost < distance_dict[node]:
                    distance_dict[node] = new_cost

                    # update track
                    track_dict[node] = track_dict[browsed_node].copy()
                    track_dict[node].append(node)

        return track_dict