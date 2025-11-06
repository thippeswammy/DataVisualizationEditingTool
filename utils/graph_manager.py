class GraphManager:
    """
    Manages the graph structure of the lanes.
    Note: The connections are currently only visual and are not yet fully integrated with the data model.
    """
    def __init__(self):
        self.adjacency_list = {}

    def add_node(self, node):
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []

    def add_edge(self, node1, node2):
        if node1 in self.adjacency_list and node2 in self.adjacency_list:
            self.adjacency_list[node1].append(node2)
            self.adjacency_list[node2].append(node1)

    def get_neighbors(self, node):
        return self.adjacency_list.get(node, [])

    def build_graph(self, data):
        for i in range(len(data)):
            self.add_node(i)

        unique_lane_ids = np.unique(data[:, -1])
        for lane_id in unique_lane_ids:
            lane_indices = np.where(data[:, -1] == lane_id)[0]
            for i in range(len(lane_indices) - 1):
                self.add_edge(lane_indices[i], lane_indices[i+1])
