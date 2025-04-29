import unittest
from collections import deque
from booking_manager_03 import BookingManager
from cl.graph import Graph
from sceduling.searchers import FlightHashTable, PassengerBST
import pandas as pd

class TestBookingManager(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by initializing the BookingManager with mock data
        based on the new datasets.
        """
        # Create graphs for flights and passengers
        flights_graph = Graph()
        passengers_graph = Graph()

        # Create a hash table for flights and a binary search tree for passengers
        flights_table = FlightHashTable()
        passengers_tree = PassengerBST()

        # Create stacks and queues for flights, confirmed passengers, and waitlisted passengers
        flights_stack = []
        confirmed_passengers_stack = []
        waitlisted_passengers_queue = deque()

        # Load mock data from the new datasets
        # Mock Kaggle dataset
        kaggle_data = [
            {"FlightNumber": 1024, "Departure": "JFK", "Arrival": "LAX", "Passengers": [
                {"PassengerID": 1, "PassengerName": "John Doe"},
                {"PassengerID": 2, "PassengerName": "Jane Smith"}
            ]},
            {"FlightNumber": 2048, "Departure": "LAX", "Arrival": "ORD", "Passengers": []}
        ]

        # Mock cities.csv data
        cities_data = [
            {"City": "JFK", "Destinations": "LAX,ORD"},
            {"City": "LAX", "Destinations": "ORD,JFK"}
        ]

        # Populate the flights graph and other structures from Kaggle dataset
        for flight in kaggle_data:
            flight_number = flight["FlightNumber"]
            departure = flight["Departure"]
            arrival = flight["Arrival"]
            passengers = flight["Passengers"]

            # Add flight to flights_stack and flights_graph
            flights_stack.append([flight_number, departure, arrival])
            flights_graph.add_node(flight_number, [flight_number, departure, arrival])
            flights_table.insert([flight_number, departure, arrival])

            # Add passengers to passengers_graph and passengers_tree
            for passenger in passengers:
                passenger_id = passenger["PassengerID"]
                passenger_name = passenger["PassengerName"]
                confirmed_passengers_stack.append([passenger_id, passenger_name, "Economy-1", "Economy", flight_number])
                passengers_graph.add_node(passenger_id, [passenger_id, passenger_name])
                passengers_tree.insert([passenger_id, passenger_name])

        # Populate the flights graph with cities.csv data
        for city in cities_data:
            city_name = city["City"]
            destinations = city["Destinations"].split(",")
            flights_graph.add_node(city_name, {"destinations": destinations})

        # Initialize the BookingManager
        self.manager = BookingManager(
            flights_graph,
            passengers_graph,
            flights_table,
            passengers_tree,
            flights_stack,
            confirmed_passengers_stack,
            waitlisted_passengers_queue
        )

    def test_book_passenger_success(self):
        """
        Test booking a passenger successfully.
        """
        result = self.manager.book_passenger([3, "Alice Johnson", "Pending"], 1024, "Economy")
        self.assertIn("booked on flight 1024", result)
        self.assertEqual(len(self.manager.confirmed_passengers_stack), 3)

    def test_book_passenger_waitlist(self):
        """
        Test adding a passenger to the waitlist when the flight is full.
        """
        # Fill up the Economy class
        for _ in range(68):  # Assuming 70 seats in Economy, 2 already booked
            self.manager.book_passenger([100 + _, f"Test Passenger {_}", "Pending"], 1024, "Economy")

        result = self.manager.book_passenger([4, "Charlie Davis", "Pending"], 1024, "Economy")
        self.assertIn("added to waitlist", result)
        self.assertEqual(len(self.manager.waitlisted_passengers_queue), 1)

    def test_cancel_booking_success(self):
        """
        Test canceling a booking successfully.
        """
        result = self.manager.cancel_booking(1, 1024)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.confirmed_passengers_stack), 1)

    def test_cancel_booking_failure(self):
        """
        Test attempting to cancel a booking that does not exist.
        """
        result = self.manager.cancel_booking(99, 1024)
        self.assertFalse(result)

    def test_manage_waitlist(self):
        """
        Test managing the waitlist after a seat becomes available.
        """
        # Add a passenger to the waitlist
        self.manager.waitlisted_passengers_queue.append([5, "Eve Adams", "Waitlisted", 1024, "Economy"])

        # Cancel a booking to free up a seat
        self.manager.cancel_booking(2, 1024)

        # Manage the waitlist
        messages = self.manager.manage_waitlist(1024)
        self.assertEqual(len(messages), 1)
        self.assertIn("booked on flight 1024", messages[0])
        self.assertEqual(len(self.manager.waitlisted_passengers_queue), 0)

    def test_get_flight_info(self):
        """
        Test retrieving flight information.
        """
        info = self.manager.get_flight_info(1024)
        self.assertIn("Flight Number: 1024", info)
        self.assertIn("Passenger ID: 1, Name: John Doe", info)

    def test_get_flight_info_not_found(self):
        """
        Test retrieving flight information for a non-existent flight.
        """
        info = self.manager.get_flight_info(9999)
        self.assertEqual(info, "Flight 9999 not found.")

    def test_get_passenger_status_booked(self):
        """
        Test retrieving the status of a booked passenger.
        """
        status = self.manager.get_passenger_status(1)
        self.assertIn("is booked on Flight 1024", status)

    def test_get_passenger_status_waitlisted(self):
        """
        Test retrieving the status of a waitlisted passenger.
        """
        self.manager.waitlisted_passengers_queue.append([6, "Frank Green", "Waitlisted", 1024, "Economy"])
        status = self.manager.get_passenger_status(6)
        self.assertIn("is on the waitlist for Flight 1024", status)

    def test_get_passenger_status_not_found(self):
        """
        Test retrieving the status of a passenger who does not exist.
        """
        status = self.manager.get_passenger_status(99)
        self.assertEqual(status, "Passenger 99 is not booked on any flight or on any waitlist.")

    def test_is_passenger_booked_or_waitlisted(self):
        """
        Test checking if a passenger is booked or waitlisted for a flight.
        """
        self.assertTrue(self.manager.is_passenger_booked_or_waitlisted(1, 1024))
        self.assertFalse(self.manager.is_passenger_booked_or_waitlisted(99, 1024))

    def test_is_seat_class_available(self):
        """
        Test checking if a seat class is available for a flight.
        """
        self.assertTrue(self.manager.is_seat_class_available(1024, "Economy"))
        # Fill up the Economy class
        for _ in range(68):  # Assuming 70 seats in Economy, 2 already booked
            self.manager.book_passenger([100 + _, f"Test Passenger {_}", "Pending"], 1024, "Economy")
        self.assertFalse(self.manager.is_seat_class_available(1024, "Economy"))


if __name__ == "__main__":
    unittest.main()