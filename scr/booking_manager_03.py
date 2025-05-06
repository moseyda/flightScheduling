from collections import deque
from sceduling.sorters import quick_sort, radix_sort

class BookingManager:
    def __init__(self, flights_graph, passengers_graph, flights_table, passengers_tree, flights_stack, confirmed_passengers_stack, waitlisted_passengers_queue, airport_data, flight_data):
        self.flights_graph = flights_graph
        self.passengers_graph = passengers_graph
        self.flights_table = flights_table
        self.passengers_tree = passengers_tree
        self.flights_stack = flights_stack
        self.confirmed_passengers_stack = confirmed_passengers_stack
        self.waitlisted_passengers_queue = waitlisted_passengers_queue or {
            "First": deque(),
            "Business": deque(),
            "Economy": deque()
        }
        self.airport_data = airport_data  # Use parsed airport data
        self.flight_data = flight_data  # Use parsed flight data

    def book_passenger(self, passenger, flight_number, seat_class):
        """
        Attempt to book a passenger on a specific flight in a specific class.

        Args:
        - passenger: List containing passenger information [PassengerID, Passenger_name].
        - flight_number: Flight number to book the passenger on.
        - seat_class: Class of the seat to book.

        Returns:
        - A string indicating the booking status.
        """
        # Check if the PassengerID is already booked or waitlisted
        if self.is_passenger_booked_or_waitlisted(passenger[0], flight_number):
            return f"Passenger with ID {passenger[0]} has already booked or is waitlisted for flight {flight_number}."

        # Check if there are available seats in the specified class
        if not self.is_seat_number_available(flight_number, seat_class):
            # No seats available, add to the waitlist
            waitlisted_passenger = [passenger[0], passenger[1], flight_number, seat_class]
            self.waitlisted_passengers_queue[seat_class].append(waitlisted_passenger)
            return f"Passenger {passenger[1]} added to waitlist for flight {flight_number} in {seat_class} class."

        # Seats are available, generate a seat number
        seat_number = self.generate_seat_number(flight_number, seat_class)
        if seat_number == "No available seats in this class.":
            return f"Seat already taken or no available seats for flight {flight_number} in {seat_class} class."

        # Book the passenger
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
            if passenger[0] == passenger_id and passenger[2] == flight_number:
                found = True
                break
            temp_stack.append(passenger)

        while temp_stack:
            self.confirmed_passengers_stack.append(temp_stack.pop())

        if found:
            # Manage the waitlist for the flight
            self.manage_waitlist(flight_number)
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
        for seat_class, queue in self.waitlisted_passengers_queue.items():
            temp_queue = deque()
            while queue:
                passenger = queue.popleft()
                if passenger[2] == flight_number:
                    if self.is_seat_number_available(flight_number, seat_class):
                        self.book_passenger(passenger, flight_number, seat_class)
                        messages.append(f"Waitlisted passenger {passenger[1]} booked on flight {flight_number} in {seat_class} class.")
                    else:
                        temp_queue.append(passenger)
                else:
                    temp_queue.append(passenger)
            self.waitlisted_passengers_queue[seat_class] = temp_queue
        return messages

    def get_flight_info(self, flight_number):
        """
        Retrieve detailed information about a flight.

        Args:
        - flight_number: The flight number to retrieve information for.

        Returns:
        - A string containing the flight's information or an error message if not found.
        """
        flight_node = self.flights_graph.get_node(flight_number)
        if flight_node:
            flight_data = flight_node.data
            departure_airport = self.airport_data.get(flight_data["departure"], {})
            arrival_airport = self.airport_data.get(flight_data["arrival"], {})
            airline = self.flight_data.get(flight_number, {}).get("Airline", "Unknown")
            info_lines = [
                f"Flight Number: {flight_number}",
                f"Airline: {airline}",
                f"Departure Airport: {departure_airport.get('Name', flight_data['departure'])} ({flight_data['departure']})",
                f"Arrival Airport: {arrival_airport.get('Name', flight_data['arrival'])} ({flight_data['arrival']})",
                f"Weekdays: {flight_data.get('weekdays', 'Unknown')}",
                "Seating Information:"
            ]
            for passenger in self.confirmed_passengers_stack:
                # Ensure the passenger data structure is valid
                if len(passenger) >= 5 and passenger[2] == flight_number:
                    info_lines.append(f"Seat: {passenger[3]}, Passenger: {passenger[1]}, Class: {passenger[4]}")
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
        flight_node = self.flights_graph.get_node(flight_number)
        if not flight_node:
            return False

        seating_list = flight_node.data["seating_list"].get(seat_class, [])
        occupied_seats = [
            passenger[3] for passenger in self.confirmed_passengers_stack
            if passenger[2] == flight_number and passenger[4] == seat_class
        ]
        return len(occupied_seats) < len(seating_list)

    def generate_seat_number(self, flight_number, seat_class):
        """
        Generate the next available seat number for a specific class on a flight.

        Args:
        - flight_number: Flight number to generate the seat for.
        - seat_class: Class of the seat.

        Returns:
        - The next available seat number as a string, or a message if no seats are available.
        """
        flight_node = self.flights_graph.get_node(flight_number)
        if not flight_node:
            return None

        seating_list = flight_node.data["seating_list"].get(seat_class, [])
        occupied_seats = [
            passenger[3] for passenger in self.confirmed_passengers_stack
            if passenger[2] == flight_number and passenger[4] == seat_class
        ]

        for seat in seating_list:
            seat_number = f"{seat}{seat_class[0]}"  # Format seat number as "6B" for Business, "16E" for Economy, etc.
            if seat_number not in occupied_seats:
                return seat_number

        return "No available seats in this class."

    def get_passenger_status(self, passenger_id):
        """
        Get the status of a passenger.

        Args:
        - passenger_id: The ID of the passenger (Customer_phone).

        Returns:
        - A string containing the passenger's status.
        """
        for passenger in self.confirmed_passengers_stack:
            if passenger[0] == passenger_id:
                return f"Passenger {passenger[1]} is booked on flight {passenger[2]} with seat {passenger[3]} in {passenger[4]} class."

        for seat_class, queue in self.waitlisted_passengers_queue.items():
            for position, passenger in enumerate(queue):
                if passenger[0] == passenger_id:
                    return f"Passenger {passenger[1]} is waitlisted for flight {passenger[2]} in {seat_class} class at position {position + 1}."

        return f"Passenger {passenger_id} has no bookings or waitlists."
    

    def is_passenger_booked_or_waitlisted(self, passenger_id, flight_number):
        """
        Check if a passenger is already booked or waitlisted for a specific flight.

        Args:
        - passenger_id: The ID of the passenger (Customer_phone).
        - flight_number: The flight number to check.

        Returns:
        - True if the passenger is booked or waitlisted for the flight, False otherwise.
        """
        # Check if the passenger is already booked
        for passenger in self.confirmed_passengers_stack:
            if passenger[0] == passenger_id and passenger[2] == flight_number:
                return True

        # Check if the passenger is waitlisted
        for seat_class, queue in self.waitlisted_passengers_queue.items():
            for waitlisted_passenger in queue:
                if waitlisted_passenger[0] == passenger_id and waitlisted_passenger[2] == flight_number:
                    return True

        return False