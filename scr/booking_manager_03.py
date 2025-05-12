from collections import deque
from sceduling.sorters import merge_sort, quick_sort 
import re

class BookingManager:
    def __init__(self, flights_graph, passengers_graph, flights_table, passengers_tree, flights_stack, confirmed_passengers_stack, waitlisted_passengers_queue, airport_data, flight_data, leg_instance_data):
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
        self.leg_instance_data = leg_instance_data # Use parsed leg instance data

    def book_passenger(self, passenger, flight_number, seat_class):
        """
        Attempt to book a passenger on a specific flight in a specific class.

        Args:
        - passenger: List containing passenger information [PassengerID, Passenger_name].
        - flight_number: Flight number to book the passenger on.
        - seat_class: Class of the seat to book.

        Returns:
        - A string indicating the booking or waitlist status.
        """
        passenger_id = passenger[0]

        # Validate PassengerID format
        if not re.match(r"^555-\d{4}$", passenger_id):
            return "PassengerID must be in the format '555-xxxx' (e.g., 555-1234)."

        # Check if the PassengerID is already booked or waitlisted
        if self.is_passenger_id_exists(passenger_id):
            return f"Passenger with ID {passenger_id} has already been booked on another flight."

        if self.is_passenger_booked_or_waitlisted(passenger_id, flight_number):
            return f"Passenger with ID {passenger_id} has already booked or is waitlisted for flight {flight_number}."

        # Check seat availability
        if not self.is_seat_number_available(flight_number, seat_class):
            # Add to waitlist if no seats are available
            return self.add_to_waitlist(passenger, flight_number, seat_class)

        # Generate a seat number and book the passenger
        seat_number = self.generate_seat_number(flight_number, seat_class)
        if seat_number == "No available seats in this class.":
            return self.add_to_waitlist(passenger, flight_number, seat_class)

        confirmed_passenger = [passenger_id, passenger[1], flight_number, seat_number, seat_class]
        self.confirmed_passengers_stack.append(confirmed_passenger)
        return f"Passenger {passenger[1]} booked on flight {flight_number} with seat number {seat_number} in {seat_class} class."
    
    
    def is_passenger_id_exists(self, passenger_id):
        """
        Check if a PassengerID exists in any confirmed bookings or waitlists.

        Args:
        - passenger_id: The PassengerID to check.

        Returns:
        - True if the PassengerID exists, False otherwise.
        """
        # Check confirmed passengers
        for passenger in self.confirmed_passengers_stack:
            if passenger[0] == passenger_id:
                return True

        # Check waitlisted passengers
        for queue in self.waitlisted_passengers_queue.values():
            for waitlisted_passenger in queue:
                if waitlisted_passenger[0] == passenger_id:
                    return True

        return False

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
        # Retrieve flight data
        flight_node = self.flights_graph.get_node(flight_number)
        if flight_node:
            flight_data = flight_node.data

            # Retrieve leg instance data for departure and arrival codes
            leg_instance = next(
                (leg for leg in self.leg_instance_data
                if leg["Flight_number"] == flight_number),
                None
            )
            if leg_instance:
                departure_code = leg_instance.get("Departure_airport_code", "Unknown")
                arrival_code = leg_instance.get("Arrival_airport_code", "Unknown")
            else:
                departure_code = "Unknown"
                arrival_code = "Unknown"

            # Retrieve airport details from airport_data
            departure_airport = self.airport_data.get(departure_code, {})
            arrival_airport = self.airport_data.get(arrival_code, {})

            airline = self.flight_data.get(flight_number, {}).get("Airline", "Unknown")
            info_lines = [
                f"Flight Number: {flight_number}",
                f"Airline: {airline}",
                f"Departure Airport: {departure_airport.get('Name', departure_code)} ({departure_code})",
                f"Arrival Airport: {arrival_airport.get('Name', arrival_code)} ({arrival_code})",
                f"Weekdays: {flight_data.get('weekdays', 'Unknown')}",
                "Seating Information:"
            ]
            for passenger in self.confirmed_passengers_stack:
                # Ensure the passenger data structure is valid
                if len(passenger) >= 5 and passenger[2] == flight_number:
                    info_lines.append(
                        f"Seat: {passenger[3]}, Passenger: {passenger[1]}, PassengerID: {passenger[0]}, Class: {passenger[4]}"
                    )
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
            seat_number = f"{seat}{seat_class[0]}" 
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
    

    def add_to_waitlist(self, passenger, flight_number, seat_class):
        """
        Add a passenger to the waitlist for a specific flight and class.

        Args:
        - passenger: List containing passenger information [PassengerID, Passenger_name].
        - flight_number: Flight number to add the passenger to the waitlist for.
        - seat_class: Class of the seat to waitlist the passenger for.

        Returns:
        - A string indicating the waitlist status.
        """
        passenger_id = passenger[0]

        # Check if the PassengerID is already waitlisted for the same flight and class
        for waitlisted_passenger in self.waitlisted_passengers_queue[seat_class]:
            if waitlisted_passenger[0] == passenger_id and waitlisted_passenger[2] == flight_number:
                return f"Passenger with ID {passenger_id} is already waitlisted for flight {flight_number} in {seat_class} class."

        # Add the passenger to the waitlist
        self.waitlisted_passengers_queue[seat_class].append([passenger_id, passenger[1], flight_number])
        return f"OOPS! No seats available for selected class. Passenger {passenger[1]} added to the waitlist for flight {flight_number} in {seat_class} class."
    

    def get_waitlist(self, flight_number):
        """
        Retrieve the waitlist for a specific flight.

        Args:
        - flight_number: The flight number to retrieve the waitlist for.

        Returns:
        - A dictionary containing the waitlist for each class.
        """
        waitlist = {}
        for seat_class, queue in self.waitlisted_passengers_queue.items():
            waitlist[seat_class] = [
                passenger for passenger in queue if passenger[2] == flight_number
            ]
        return waitlist
    
    def remove_from_waitlist(self, passenger_id, flight_number, seat_class):
        """
        Remove a passenger from the waitlist.

        Args:
        - passenger_id: The ID of the passenger to remove.
        - flight_number: The flight number to remove the passenger from.
        - seat_class: The class to remove the passenger from.

        Returns:
        - A string indicating the removal status.
        """
        queue = self.waitlisted_passengers_queue[seat_class]
        for passenger in queue:
            if passenger[0] == passenger_id and passenger[2] == flight_number:
                queue.remove(passenger)
                return f"Passenger {passenger_id} removed from the waitlist for flight {flight_number} in {seat_class} class."
        return f"Passenger {passenger_id} not found on the waitlist for flight {flight_number} in {seat_class} class."
    

    def sort_confirmed_passengers(self, sort_by="Passenger Name"):
        """
        Sort confirmed passengers by a given attribute.
        Args:
        - sort_by: The attribute to sort by (e.g., "Passenger Name", "Seat Class").
        """
        if sort_by == "Passenger Name":
            self.confirmed_passengers_stack = merge_sort(self.confirmed_passengers_stack, key=lambda x: x[1])  # Use Merge Sort
        elif sort_by == "Seat Class":
            self.confirmed_passengers_stack = quick_sort(self.confirmed_passengers_stack, key=lambda x: x[4])  # Use Quick Sort

    def sort_waitlist(self, flight_number, sort_by="Passenger Name"):
        """
        Sort the waitlist for a specific flight by a given attribute.
        Args:
        - flight_number: The flight number to sort the waitlist for.
        - sort_by: The attribute to sort by (e.g., "Passenger Name").
        """
        for seat_class, queue in self.waitlisted_passengers_queue.items():
            waitlist = [p for p in queue if p[2] == flight_number]
            if sort_by == "Passenger Name":
                sorted_waitlist = merge_sort(waitlist, key=lambda x: x[1])  # Use Merge Sort
            elif sort_by == "Position":
                sorted_waitlist = quick_sort(waitlist, key=lambda x: queue.index(x))  # Use Quick Sort
            self.waitlisted_passengers_queue[seat_class] = deque(sorted_waitlist)
