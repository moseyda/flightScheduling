from cl.graph import Node as Node
from sceduling.sorters import merge_sort, quick_sort, radix_sort


class RedBlackNode:
    def __init__(self, key, value):
        """
        Initialize a Red-Black Tree node.
        Args:
        - key: The key for the node (e.g., flight_number).
        - value: The value associated with the key (e.g., flight details).
        """
        self.key = key
        self.value = value
        self.color = "red"
        self.left = None
        self.right = None
        self.parent = None


class RedBlackTree:
    def __init__(self):
        self.TNULL = RedBlackNode(None, None)
        self.TNULL.color = "black"
        self.root = self.TNULL

    def insert(self, key, value):
        """
        Insert a key-value pair into the Red-Black Tree.
        Args:
        - key: The key to insert (e.g., flight_number).
        - value: The value associated with the key (e.g., flight details).
        """
        new_node = RedBlackNode(key, value)
        new_node.left = self.TNULL
        new_node.right = self.TNULL
        new_node.parent = None

        parent = None
        current = self.root

        while current != self.TNULL:
            parent = current
            if new_node.key < current.key:
                current = current.left
            else:
                current = current.right

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif new_node.key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        new_node.color = "red"
        self._fix_insert(new_node)

    def _fix_insert(self, node):
        """
        Fix the Red-Black Tree after insertion to maintain balance.
        """
        while node.parent and node.parent.color == "red":
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == "red":
                    uncle.color = "black"
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate(node)
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    self._right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == "red":
                    uncle.color = "black"
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate(node)
                    node.parent.color = "black"
                    node.parent.parent.color = "red"
                    self._left_rotate(node.parent.parent)
        self.root.color = "black"

    def _left_rotate(self, node):
        """
        Perform a left rotation on the tree.
        """
        right_child = node.right
        node.right = right_child.left
        if right_child.left != self.TNULL:
            right_child.left.parent = node
        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child
        right_child.left = node
        node.parent = right_child

    def _right_rotate(self, node):
        """
        Perform a right rotation on the tree.
        """
        left_child = node.left
        node.left = left_child.right
        if left_child.right != self.TNULL:
            left_child.right.parent = node
        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child
        left_child.right = node
        node.parent = left_child

    def search(self, key):
        """
        Search for a key in the Red-Black Tree.
        Args:
        - key: The key to search for (e.g., flight_number).
        Returns:
        - The value associated with the key, or None if not found.
        """
        current = self.root
        while current != self.TNULL:
            if key == current.key:
                return current.value
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def search_by_condition(self, condition):
        """
        Search for all nodes that satisfy a given condition.
        Args:
        - condition: A function that takes a node's value and returns True or False.
        Returns:
        - A list of values that satisfy the condition.
        """
        results = []
        self._inorder_traversal(self.root, condition, results)
        return results

    def _inorder_traversal(self, node, condition, results):
        """
        Perform an in-order traversal of the tree.
        """
        if node != self.TNULL:
            self._inorder_traversal(node.left, condition, results)
            if condition(node.value):
                results.append(node.value)
            self._inorder_traversal(node.right, condition, results)


class FlightRedBlackTree:
    def __init__(self):
        self.tree = RedBlackTree()

    def insert(self, flight):
        """
        Insert a flight into the Red-Black Tree.
        Args:
        - flight: A list containing flight details (e.g., flight number, departure, arrival, airline, weekdays).
        """
        key = flight[0] 
        self.tree.insert(key, flight)

    def search_by_flight_number(self, flight_number):
        """
        Search for a flight by flight number.
        """
        result = self.tree.search(flight_number)
        return [result] if result else []

    def search_by_departure_airport(self, departure_airport):
        """
        Search for flights by departure airport.
        """
        return self.tree.search_by_condition(lambda flight: flight[1] == departure_airport)

    def search_by_arrival_airport(self, arrival_airport):
        """
        Search for flights by arrival airport.
        """
        return self.tree.search_by_condition(lambda flight: flight[2] == arrival_airport)

    def search_by_airline(self, airline):
        """
        Search for flights by airline.
        """
        return self.tree.search_by_condition(lambda flight: len(flight) > 3 and flight[3] == airline)

    def search_by_weekday(self, weekday):
        """
        Search for flights by weekday.
        """
        return self.tree.search_by_condition(lambda flight: len(flight) > 4 and weekday in flight[4])

    def get_all_flights(self):
        """
        Return a list of all flights in the Red-Black Tree.
        """
        return self.tree.search_by_condition(lambda _: True)

    def get_sorted_flights(self, sort_by="Flight Number"):
        """
        Retrieve all flights sorted by a given attribute.
        Args:
        - sort_by: The attribute to sort by (e.g., "Flight Number", "Departure Airport").
        """
        flights = self.get_all_flights()
        if sort_by == "Flight Number":
            return radix_sort(flights, get_attribute=lambda x: x[0])  # Use Radix Sort
        elif sort_by == "Departure Airport":
            return merge_sort(flights, key=lambda x: x[1])  # Use Merge Sort
        elif sort_by == "Arrival Airport":
            return merge_sort(flights, key=lambda x: x[2])  # Use Merge Sort
        elif sort_by == "Available Seats":
            return quick_sort(flights, key=lambda x: x[4])  # Use Quick Sort
        return flights
    



# Binary search tree for searching through passengers
class Node:
    def __init__(self, data):
        """
        Initialize a Node with data.
        Args:
        - data: A list containing passenger details (e.g., [passenger_id, passenger_name]).
        """
        self.data = data
        self.left = None
        self.right = None


class PassengerBST:
    def __init__(self):
        self.root = None

    def insert(self, passenger):
        """
        Insert a passenger into the binary search tree.
        Args:
        - passenger: A list containing passenger details (e.g., [passenger_id, passenger_name]).
        """
        if not self.root:
            self.root = Node(passenger)
        else:
            self._insert(self.root, Node(passenger))

    def _insert(self, node, passenger_node):
        """
        Helper method to recursively insert a passenger node into the tree.
        """
        if passenger_node.data[0] < node.data[0]:
            if node.left is None:
                node.left = passenger_node
            else:
                self._insert(node.left, passenger_node)
        else:
            if node.right is None:
                node.right = passenger_node
            else:
                self._insert(node.right, passenger_node)