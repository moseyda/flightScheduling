class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, key, data=None):
        if key not in self.nodes:
            self.nodes[key] = Node(key, data)

    def add_edge(self, src, dest, weight=1):
        if src in self.nodes and dest in self.nodes:
            self.nodes[src].add_neighbor((self.nodes[dest], weight))  # Store neighbor and weight

    def get_node(self, key):
        return self.nodes.get(key, None)

    def remove_node(self, key):
        if key in self.nodes:
            del self.nodes[key]
            for node in self.nodes.values():
                node.remove_neighbor(key)

    def update_node(self, key, data_key, data_value):
        node = self.nodes.get(key)
        if node and isinstance(node.data, dict):
            node.data[data_key] = data_value

    def find_node_by_data(self, data_key, data_value):
        for node in self.nodes.values():
            if isinstance(node.data, dict) and node.data.get(data_key) == data_value:
                return node
        return None


class Node:
    def __init__(self, key, data=None):
        self.key = key
        self.data = data if data else {}
        self.neighbors = set()  # Use a set for faster lookups and uniqueness

    def add_data(self, data_key, data_value):
        self.data[data_key] = data_value

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)  # Automatically handles duplicates

    def remove_neighbor(self, key):
        self.neighbors = {neighbor for neighbor in self.neighbors if neighbor[0].key != key}

    def remove_data(self, data_key):
        if data_key in self.data:
            del self.data[data_key]