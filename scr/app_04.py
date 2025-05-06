import streamlit as st
from collections import deque
from booking_manager_03 import BookingManager
from cl.graph import Graph
from sceduling.searchers import FlightHashTable, PassengerBST
from utils import parse_airline_res_db  # Import the parsing function
import pandas as pd

# Path to the AirlineResDB.txt file
airline_res_db_path = "../AirlineResDB.txt"

# Parse the AirlineResDB.txt file
airline_res_db = parse_airline_res_db(airline_res_db_path)

# Extract relevant data
airport_data = {entry["Airport_code"]: entry for entry in airline_res_db["Airport"]}
flight_data = {entry["Flight_number"]: entry for entry in airline_res_db["Flight"]}
seat_reservations = airline_res_db["Seat_reservation"]

# Initialize data structures
flights_graph = Graph()  # Graph to store flight information
passengers_graph = Graph()  # Graph to store passenger information
flights_table = FlightHashTable()  # Hash table to quickly search flights
passengers_tree = PassengerBST()  # Binary search tree to quickly search passengers
flights_stack = []  # Stack to store flights
confirmed_passengers_stack = []  # Stack to store confirmed passengers
waitlisted_passengers_queue = deque()  # Queue to store waitlisted passengers

# Populate flights from the parsed data
for flight in flight_data.values():
    flight_number = flight["Flight_number"]
    departure = flight.get("Departure_airport", "Unknown")
    arrival = flight.get("Arrival_airport", "Unknown")
    weekdays = flight.get("Weekdays", "Unknown")
    seating_list = {
        "First": [1, 5, 9, 11, 21],  # Example arbitrary ranges
        "Business": list(range(6, 16)),
        "Economy": list(range(16, 36))
    }
    flights_stack.append([flight_number, departure, arrival, weekdays, seating_list])
    flights_graph.add_node(flight_number, {
        "departure": departure,
        "arrival": arrival,
        "weekdays": weekdays,
        "seating_list": seating_list
    })
    flights_table.insert([flight_number, departure, arrival, weekdays])

# Populate seat reservations
for reservation in seat_reservations:
    passenger_id = reservation["Customer_phone"]
    passenger_name = reservation["Customer_name"]
    flight_number = reservation["Flight_number"]
    seat_number = reservation["Seat_number"]
    # Infer seat class from seat number (e.g., "1A" → "First")
    seat_class = "First" if seat_number[0] in ["1", "F"] else "Business" if seat_number[0] in ["2", "B"] else "Economy"
    confirmed_passengers_stack.append([passenger_id, passenger_name, flight_number, seat_number, seat_class])

# Create the BookingManager and store it in the session state
if 'manager' not in st.session_state:
    st.session_state['manager'] = BookingManager(
        flights_graph,
        passengers_graph,
        flights_table,
        passengers_tree,
        flights_stack,
        confirmed_passengers_stack,
        waitlisted_passengers_queue,
        airport_data,  # Pass airport data
        flight_data    # Pass flight data
    )
else:
    manager = st.session_state['manager']


def book_passenger():
    # Check if all the required details are entered
    if st.session_state.booking_passenger_name and st.session_state.booking_passenger_id and st.session_state.booking_flight_number and st.session_state.seat_class:
        passenger_id = st.session_state.booking_passenger_id  # Keep PassengerID as a string
        flight_number = st.session_state.booking_flight_number

        # Attempt to book the passenger
        result = st.session_state['manager'].book_passenger(
            [passenger_id, st.session_state.booking_passenger_name],
            flight_number,
            st.session_state.seat_class
        )
        if "already booked or is waitlisted" in result:
            st.error(result)
        else:
            st.success(result)
    else:
        st.error("Please enter all the details.")


def cancel_passenger():
    # Check if all the required details are entered
    if st.session_state.cancellation_passenger_id and st.session_state.cancellation_flight_number:
        passenger_id = st.session_state.cancellation_passenger_id
        flight_number = st.session_state.cancellation_flight_number
        # Attempt to cancel the booking
        success = st.session_state['manager'].cancel_booking(passenger_id, flight_number)
        if success:
            st.success(f"Passenger {passenger_id} cancelled from flight {flight_number}.")
            # Check if there are passengers on the waitlist for the flight
            messages = st.session_state['manager'].manage_waitlist(flight_number)
            if messages:
                for message in messages:
                    st.success(message)
            else:
                st.info("No waitlisted passengers for this flight.")
        else:
            st.error(f"Could not cancel booking for passenger {passenger_id} from flight {flight_number}.")
    else:
        st.error("Please enter all the details.")


def check_passenger_status():
    # Check if the passenger ID is entered
    if st.session_state.status_passenger_id:
        passenger_id = st.session_state.status_passenger_id  # Keep passenger_id as a string
        status = st.session_state['manager'].get_passenger_status(passenger_id)
        if status:
            st.success(status)
        else:
            st.error(f"Passenger {passenger_id} not found.")
    else:
        st.error("Please enter the passenger ID.")


def check_flight_info():
    flight_number = st.session_state.get('flight_number')
    if flight_number:
        flight_info = st.session_state['manager'].get_flight_info(flight_number)
        if "not found" not in flight_info:
            st.success(f"Flight {flight_number} found.")
            st.text_area("Flight Info", flight_info, height=200)
        else:
            st.error(flight_info)
    else:
        st.error("Please enter the flight number.")


def main():
    st.title("Flight Booking System")

    with st.expander("Book a Passenger"):
        st.text_input("Enter Passenger Name", value=st.session_state.get('booking_passenger_name', ''), key='booking_passenger_name')
        st.text_input("Enter Passenger ID", value=st.session_state.get('booking_passenger_id', ''), key='booking_passenger_id')
        st.text_input("Enter Flight Number", value=st.session_state.get('booking_flight_number', ''), key='booking_flight_number')
        seat_classes = ["First", "Business", "Economy"]
        st.selectbox("Choose a Class", seat_classes, index=seat_classes.index(st.session_state.get('seat_class', seat_classes[0])), key='seat_class')
        st.button("Book Passenger", on_click=book_passenger)

    with st.expander("Cancel a Booking"):
        st.text_input("Enter Passenger ID", value=st.session_state.get('cancellation_passenger_id', ''), key='cancellation_passenger_id')
        st.text_input("Enter Flight Number", value=st.session_state.get('cancellation_flight_number', ''), key='cancellation_flight_number')
        st.button("Cancel Booking", on_click=cancel_passenger)

    with st.expander("Check Passenger Status"):
        st.text_input("Enter Passenger ID", value=st.session_state.get('status_passenger_id', ''), key='status_passenger_id')
        st.button("Check Status", on_click=check_passenger_status)

    with st.expander("Check Flight Information"):
        st.text_input("Enter Flight Number", value=st.session_state.get('flight_number', ''), key='flight_number')
        st.button("Check Flight Info", on_click=check_flight_info)


if __name__ == "__main__":
    main()