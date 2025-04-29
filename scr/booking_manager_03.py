from collections import deque
from sceduling.sorters import quick_sort, radix_sort

class BookingManager:
    def __init__(self, flights_graph, passengers_graph, flights_table, passengers_tree, flights_stack, confirmed_passengers_stack, waitlisted_passengers_queue, airport_data, flight_data):
        """
        Initialize the BookingManager with the necessary data structures.
        
        Args:
        - flights_graph: Graph representing flights and their connections.
        - passengers_graph: Graph representing passengers and their flights.
        - flights_table: Hash table for efficient searching of flights.
        - passengers_tree: Binary search tree for efficient searching of passengers.
        - flights_stack: Stack to keep track of flights in LIFO order.
        - confirmed_passengers_stack: Stack to keep track of confirmed passengers in LIFO order.
        - waitlisted_passengers_queue: Queue to keep track of waitlisted passengers in FIFO order.
        - airport_data: Dictionary containing airport information from AirlineResDB.
        - flight_data: Dictionary containing flight and fare information from AirlineResDB.
        """
        self.flights_graph = flights_graph
        self.passengers_graph = passengers_graph
        self.flights_table = flights_table
        self.passengers_tree = passengers_tree
        self.flights_stack = flights_stack
        self.confirmed_passengers_stack = confirmed_passengers_stack
        self.waitlisted_passengers_queue = waitlisted_passengers_queue
        self.airport_data = airport_data  # Airport data from AirlineResDB
        self.flight_data = flight_data  # Flight and fare data from AirlineResDB

    def book_passenger(self, passenger, flight_number, seat_class):
        """
        Attempt to book a passenger on a specific flight in a specific class.

        Args:
        - passenger: List containing passenger information [Customer_phone, Customer_name].
        - flight_number: Flight number to book the passenger on.
        - seat_class: Class of the seat to book.

        Returns:
        - A string indicating the booking status.
        """
        if self.is_passenger_booked_or_waitlisted(passenger[0], flight_number):
            return f"Passenger {passenger[1]} is already booked or waitlisted for flight {flight_number}."

        if not self.is_seat_number_available(flight_number, seat_class):
            # No seats available, add to the waitlist
            waitlisted_passenger = [passenger[0], passenger[1], flight_number, seat_class]
            self.waitlisted_passengers_queue.append(waitlisted_passenger)
            return f"Passenger {passenger[1]} added to waitlist for flight {flight_number} in {seat_class} class."

        # Seats are available, book the passenger
        seat_number = f"{seat_class}-{len(self.confirmed_passengers_stack) + 1}"  # Generate a seat number
        confirmed_passenger = [passenger[0], passenger[1], flight_number, seat_number, seat_class]
        self.confirmed_passengers_stack.append(confirmed_passenger)
        return f"Passenger {passenger[1]} booked on flight {flight_number} with seat number {seat_number} in {seat_class} class."

    def cancel_booking(self, passenger_id, flight_number):
        """ 
        Cancel a booking and manage the graph.
        
        Args:
        - passenger_id: ID of the passenger to cancel the booking for.
        - flight_number: Flight number to cancel the booking for.
        
        Returns:
        - A boolean indicating whether the booking was found and cancelled.
        """
        found = False
        temp_stack = []
        while self.confirmed_passengers_stack:
            passenger = self.confirmed_passengers_stack.pop()
            if passenger[0] == passenger_id and passenger[4] == flight_number:
                found = True
                flight_node = self.flights_graph.get_node(flight_number)
                if flight_node:
                    flight_node.remove_data(passenger)
                break
            temp_stack.append(passenger)

        while temp_stack:
            self.confirmed_passengers_stack.append(temp_stack.pop())

        return found

    def manage_waitlist(self, flight_number):
        """
        Manage the waitlist for a specific flight.
        
        Args:
        - flight_number: Flight number to manage the waitlist for.
        
        Returns:
        - A list of strings indicating the booking status of waitlisted passengers.
        """
        messages = []
        temp_queue = deque()
        while self.waitlisted_passengers_queue:
            passenger = self.waitlisted_passengers_queue.popleft()
            if passenger[3] == flight_number:
                if self.is_seat_number_available(flight_number, passenger[-1]):
                    self.book_passenger(passenger, flight_number, passenger[-1])
                    messages.append(f"Waitlisted passenger {passenger[1]} booked on flight {flight_number}.")
                else:
                    temp_queue.append(passenger)
            else:
                temp_queue.append(passenger)

        self.waitlisted_passengers_queue = temp_queue
        return messages

    def get_flight_info(self, flight_number):
        """ 
        Get the information for a flight.
        
        Args:
        - flight_number: Flight number to get the information for.
        
        Returns:
        - A string containing the flight information.
        """
        flight_node = self.flights_graph.get_node(flight_number)
        if flight_node:
            flight_data = flight_node.data
            departure_airport = self.airport_data.get(flight_data[1], {})
            arrival_airport = self.airport_data.get(flight_data[2], {})
            airline = self.flight_data.get(flight_number, {}).get("Airline", "Unknown")
            info_lines = [
                f"Flight Number: {flight_data[0]}",
                f"Airline: {airline}",
                f"Departure Airport: {departure_airport.get('Name', flight_data[1])} ({flight_data[1]})",
                f"Arrival Airport: {arrival_airport.get('Name', flight_data[2])} ({flight_data[2]})",
                f"Date and Time: {flight_data[3]}",
                "Passenger Information:"
            ]
            for passenger in self.confirmed_passengers_stack:
                if passenger[4] == flight_number:
                    info_lines.append(f"Passenger ID: {passenger[0]}, Name: {passenger[1]}, Seat: {passenger[3]}, Class: {passenger[-1]}")
            return "\n".join(info_lines)
        return f"Flight {flight_number} not found."

    def is_seat_number_available(self, flight_number, seat_class):
        """
        Check if there is available space in a specific class for a flight.

        Args:
        - flight_number: Flight number to check.
        - seat_class: Class of the seat to check.

        Returns:
        - A boolean indicating whether there is available space in the class.
        """
        class_capacity = {
            "First": 10,
            "Business": 20,
            "Economy": 70
        }
        count = 0
        for passenger in self.confirmed_passengers_stack:
            if passenger[2] == flight_number and passenger[4] == seat_class:  # Correct indexing
                count += 1
        return count < class_capacity.get(seat_class, 0)

    def get_airport_info(self, airport_code):
        """ 
        Get detailed information about an airport.
        
        Args:
        - airport_code: Code of the airport to get information for.
        
        Returns:
        - A string containing the airport information.
        """
        airport = self.airport_data.get(airport_code, {})
        if airport:
            return f"Airport Code: {airport_code}\nName: {airport.get('Name')}\nCity: {airport.get('City')}\nState: {airport.get('State')}"
        return f"Airport {airport_code} not found."


    def is_passenger_booked_or_waitlisted(self, passenger_id, flight_number):
        """
        Check if a passenger is already booked or waitlisted for a specific flight.

        Args:
        - passenger_id: The ID of the passenger (Customer_phone).
        - flight_number: The flight number.

        Returns:
        - True if the passenger is booked or waitlisted, False otherwise.
        """
        # Check if the passenger is in the confirmed passengers stack
        for passenger in self.confirmed_passengers_stack:
            if passenger[0] == passenger_id and passenger[2] == flight_number:
                return True

        # Check if the passenger is in the waitlisted passengers queue
        for passenger in self.waitlisted_passengers_queue:
            if passenger[0] == passenger_id and passenger[2] == flight_number:
                return True

        return False
    
    def get_passenger_status(self, passenger_id):
        # Check confirmed passengers
        for passenger in self.confirmed_passengers_stack:
            if passenger[0] == passenger_id:
                # Handle legacy entries (e.g., missing seat/class)
                details = []
                if len(passenger) > 1: details.append(f"Name: {passenger[1]}")
                if len(passenger) > 2: details.append(f"Flight: {passenger[2]}")
                if len(passenger) > 3: details.append(f"Seat: {passenger[3]}")
                if len(passenger) > 4: details.append(f"Class: {passenger[4]}")
                return f"Passenger with ID {passenger_id} is already booked: " + ", ".join(details) if details else "Legacy entry"

        # Check waitlisted passengers
        for passenger in self.waitlisted_passengers_queue:
            if passenger[0] == passenger_id:
                return f"Passenger {passenger[1]} is waitlisted for Flight {passenger[2]} in {passenger[3]} class."

        return f"Passenger {passenger_id} has no bookings/waitlists."