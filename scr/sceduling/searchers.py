from cl.graph import Node as Node

# Hash table for searching through flights by flight number, departure airport, arrival airport, airline, and weekdays
class FlightHashTable:
    def __init__(self):
        self.table = {}

    def insert(self, flight):
        """
        Insert a flight into the hash table.
        Args:
        - flight: A list containing flight details (e.g., flight number, departure, arrival, airline, weekdays).
        """
        key = (flight[0], flight[1], flight[2])  # Flight number, departure, arrival
        self.table[key] = flight

    def search_by_flight_number(self, flight_number):
        """
        Search for flights by flight number.
        """
        return [flight for flight in self.table.values() if flight[0] == flight_number]

    def search_by_departure_airport(self, departure_airport):
        """
        Search for flights by departure airport.
        """
        return [flight for flight in self.table.values() if flight[1] == departure_airport]

    def search_by_arrival_airport(self, arrival_airport):
        """
        Search for flights by arrival airport.
        """
        return [flight for flight in self.table.values() if flight[2] == arrival_airport]

    def search_by_airline(self, airline):
        """
        Search for flights by airline.
        """
        return [flight for flight in self.table.values() if len(flight) > 3 and flight[3] == airline]

    def search_by_weekday(self, weekday):
        """
        Search for flights by weekday.
        """
        return [flight for flight in self.table.values() if len(flight) > 4 and weekday in flight[4]]

    def get_all_flights(self):
        """
        Return a list of all flights in the hash table.
        """
        return list(self.table.values())


# Binary search tree for searching through passengers
class Node:
    def __init__(self, data):
        """
        Initialize a Node with data.
        Args:
        - data: A list containing passenger details (e.g., [passenger_id, passenger_name]).
        """
        self.data = data  # Ensure data is stored as a list
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
        if passenger_node.data[0] < node.data[0]:  # Compare by passenger ID
            if node.left is None:
                node.left = passenger_node
            else:
                self._insert(node.left, passenger_node)
        else:
            if node.right is None:
                node.right = passenger_node
            else:
                self._insert(node.right, passenger_node)