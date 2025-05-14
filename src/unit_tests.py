import unittest
from collections import deque
from booking_manager_03 import BookingManager
from cl.graph import Graph
from algorithms.searchers import FlightRedBlackTree, PassengerBST


class TestBookingManager(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by initializing the BookingManager with mock data.
        """
        # Create graphs for flights and passengers
        flights_graph = Graph()
        passengers_graph = Graph()

        # Create a red-black tree for flights and a binary search tree for passengers
        flights_table = FlightRedBlackTree()
        passengers_tree = PassengerBST()

        # Create stacks and queues for flights, confirmed passengers, and waitlisted passengers
        flights_stack = []
        confirmed_passengers_stack = []
        waitlisted_passengers_queue = {
            "First": deque(),
            "Business": deque(),
            "Economy": deque()
        }

        # Mock data for flights
        flights_stack.append(["HA48", "HNL", "OAK", "Yes", {
            "First": [1, 2],
            "Business": [3, 4],
            "Economy": [5, 6]
        }])
        flights_graph.add_node("HA48", {
            "departure": "HNL",
            "arrival": "OAK",
            "weekdays": "Yes",
            "seating_list": {
                "First": [1, 2],
                "Business": [3, 4],
                "Economy": [5, 6]
            }
        })
        flights_table.insert(["HA48", "HNL", "OAK", "Yes"])

        # Mock data for passengers
        confirmed_passengers_stack.append(["555-1234", "Clement", "HA48", "1F", "First"])
        confirmed_passengers_stack.append(["555-5678", "Sarah", "HA48", "3B", "Business"])

        # Initialize the BookingManager
        self.manager = BookingManager(
            flights_graph,
            passengers_graph,
            flights_table,
            passengers_tree,
            flights_stack,
            confirmed_passengers_stack,
            waitlisted_passengers_queue,
            airport_data={},
            flight_data={},
            leg_instance_data=[]
        )

    def test_get_waitlist(self):
        """
        Test retrieving the waitlist for a flight.
        """
        # Add passengers to the waitlist
        self.manager.waitlisted_passengers_queue["First"].append(["555-9876", "Ali", "HA48"])
        self.manager.waitlisted_passengers_queue["Economy"].append(["555-8765", "Bob", "HA48"])

        waitlist = self.manager.get_waitlist("HA48")
        self.assertIn("First", waitlist)
        self.assertIn("Economy", waitlist)
        self.assertEqual(len(waitlist["First"]), 1)
        self.assertEqual(len(waitlist["Economy"]), 1)
        self.assertEqual(waitlist["First"][0]["passenger_name"], "Ali")
        self.assertEqual(waitlist["Economy"][0]["passenger_name"], "Bob")

    def test_remove_from_waitlist(self):
        """
        Test removing a passenger from the waitlist.
        """
        # Add a passenger to the waitlist
        self.manager.waitlisted_passengers_queue["Economy"].append(["555-8765", "Bob", "HA48"])

        # Remove the passenger
        result = self.manager.remove_from_waitlist("555-8765", "HA48", "Economy")
        self.assertIn("removed from the waitlist", result)
        self.assertEqual(len(self.manager.waitlisted_passengers_queue["Economy"]), 0)

    def test_manage_waitlist(self):
        """
        Test managing the waitlist after a seat becomes available.
        """
        # Add a passenger to the waitlist
        self.manager.waitlisted_passengers_queue["First"].append(["555-9876", "Ali", "HA48"])

        # Verify the waitlist is not empty
        self.assertEqual(len(self.manager.waitlisted_passengers_queue["First"]), 1)

        # Cancel a booking to free up a seat
        self.manager.cancel_booking("555-1234", "HA48")

        # Manage the waitlist
        messages = self.manager.manage_waitlist("HA48")

        # Verify the passenger was moved from the waitlist to confirmed bookings
        self.assertEqual(len(messages), 1)
        self.assertIn("Ali", messages[0])
        self.assertEqual(len(self.manager.waitlisted_passengers_queue["First"]), 0)

        # Verify the passenger is now in the confirmed bookings stack
        confirmed_passenger = next(
            (p for p in self.manager.confirmed_passengers_stack if p[0] == "555-9876"), None
        )
        self.assertIsNotNone(confirmed_passenger)
        self.assertEqual(confirmed_passenger[1], "Ali")
        self.assertEqual(confirmed_passenger[2], "HA48")
        self.assertEqual(confirmed_passenger[4], "First")

    def test_get_passenger_status_waitlisted(self):
        """
        Test retrieving the status of a waitlisted passenger.
        """
        # Add a passenger to the waitlist
        self.manager.waitlisted_passengers_queue["Economy"].append(["555-8765", "Bob", "HA48"])

        status = self.manager.get_passenger_status("555-8765")
        self.assertIn("waitlisted for flight HA48", status)
        self.assertIn("Economy class at position 1", status)

    def test_get_passenger_status_booked(self):
        """
        Test retrieving the status of a booked passenger.
        """
        status = self.manager.get_passenger_status("555-1234")
        self.assertIn("booked on flight HA48", status)
        self.assertIn("seat 1F in First class", status)


if __name__ == "__main__":
    unittest.main()