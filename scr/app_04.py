import streamlit as st
from collections import deque
from booking_manager_03 import BookingManager
from cl.graph import Graph
from sceduling.searchers import FlightHashTable, PassengerBST
import pandas as pd

# Load the flights dataset
file_path = "../flights.csv"
df = pd.read_csv(file_path)

# Load cities.csv
cities_file_path = "../cities.csv"
cities_df = pd.read_csv(cities_file_path)

# Mock AirlineResDB data (aligned with the structure in AirlineResDB.txt)
airline_res_db = {
    "Airport": {
        "JFK": {"Name": "John F. Kennedy International Airport", "City": "New York", "State": "NY"},
        "LAX": {"Name": "Los Angeles International Airport", "City": "Los Angeles", "State": "CA"},
        "ORD": {"Name": "O'Hare International Airport", "City": "Chicago", "State": "IL"},
    },
    "Flight": {
        "DL5841": {"Airline": "Delta Airlines", "Weekdays": "Mon, Wed, Fri"},
        "AA1522": {"Airline": "American Airlines", "Weekdays": "Tue, Thu, Sat"},
        "UA560": {"Airline": "United Airlines", "Weekdays": "Mon, Tue, Wed, Thu, Fri"},
    },
    "Seat_reservation": [
        {"Flight_number": "DL5841", "Leg_number": 1, "Date": "2018-02-09", "Seat_number": "7A", "Customer_name": "Edgar", "Customer_phone": "555-0003"},
        {"Flight_number": "DL5841", "Leg_number": 1, "Date": "2018-02-09", "Seat_number": "7F", "Customer_name": "Mitchell", "Customer_phone": "555-0005"},
        {"Flight_number": "AA1522", "Leg_number": 1, "Date": "2018-08-05", "Seat_number": "6A", "Customer_name": "Dorothy", "Customer_phone": "555-0016"},
        {"Flight_number": "AA1522", "Leg_number": 1, "Date": "2018-08-05", "Seat_number": "7E", "Customer_name": "Max", "Customer_phone": "555-0017"},
    ],
}

# Process the flights dataset into flights and passengers
flights_graph = Graph()  # Graph to store flight information
passengers_graph = Graph()  # Graph to store passenger information
flights_table = FlightHashTable()  # Hash table to quickly search flights
passengers_tree = PassengerBST()  # Binary search tree to quickly search passengers
flights_stack = []  # Stack to store flights
confirmed_passengers_stack = []  # Stack to store confirmed passengers
waitlisted_passengers_queue = deque()  # Queue to store waitlisted passengers

# Populate flights from the flights dataset
for _, row in df.iterrows():
    flight_number = int(row['index'])  # Extract flight number as integer
    if 0 <= flight_number <= 999:  # Validate flight number range
        departure = row['Source']
        arrival = row['Destination']
        departure_date = row['Date_of_Journey']
        seating_list = {
            "First": [1, 5, 9, 11, 21],  # Example arbitrary ranges
            "Business": list(range(6, 16)),
            "Economy": list(range(16, 36))
        }
        flights_stack.append([flight_number, departure, arrival, departure_date, seating_list])
        flights_graph.add_node(flight_number, {
            "departure": departure,
            "arrival": arrival,
            "date": departure_date,
            "seating_list": seating_list
        })
        flights_table.insert([flight_number, departure, arrival, departure_date])

# Replace the existing Seat_reservation processing loop with:
for reservation in airline_res_db["Seat_reservation"]:
    passenger_id = str(reservation["Customer_phone"])
    passenger_name = reservation["Customer_name"]
    flight_number = reservation["Flight_number"]
    seat_number = reservation["Seat_number"]
    # Infer seat class from seat number (e.g., "1A" → "First")
    seat_class = "First" if seat_number[0] in ["1", "F"] else "Business" if seat_number[0] in ["2", "B"] else "Economy"
    confirmed_passengers_stack.append([passenger_id, passenger_name, flight_number, seat_number, seat_class])

# Process cities.csv for additional flight connections
cities_df['Destinations'] = cities_df['Destinations'].fillna('')  # Handle missing values

for _, row in cities_df.iterrows():
    city = row['City']
    destinations = str(row['Destinations']).split(',')  # Convert to string and split
    flights_graph.add_node(city, {"destinations": destinations})

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
        airline_res_db["Airport"],  # Pass airport data
        airline_res_db["Flight"]   # Pass flight data
    )
else:
    manager = st.session_state['manager']


def book_passenger():
    # Check if all the required details are entered
    if st.session_state.booking_passenger_name and st.session_state.booking_passenger_id and st.session_state.booking_flight_number and st.session_state.seat_class:
        passenger_id = st.session_state.booking_passenger_id  # Keep passenger_id as a string
        flight_number = st.session_state.booking_flight_number

        # Check if the passenger is already booked or waitlisted
        if st.session_state['manager'].is_passenger_booked_or_waitlisted(passenger_id, flight_number):
            st.error(f"Passenger {st.session_state.booking_passenger_name} ({passenger_id}) is already booked or waitlisted for flight {flight_number}.")
        else:
            # Attempt to book the passenger
            result = st.session_state['manager'].book_passenger(
                [passenger_id, st.session_state.booking_passenger_name, "Pending"],
                flight_number,
                st.session_state.seat_class
            )
            if isinstance(result, str):
                st.success(result)
            else:
                # If booking failed, add the passenger to the waitlist
                st.session_state['manager'].waitlisted_passengers_queue.append(
                    [passenger_id, st.session_state.booking_passenger_name, "Waitlisted", flight_number, st.session_state.seat_class]
                )
                st.success(f"Passenger {st.session_state.booking_passenger_name} ({passenger_id}) added to waitlist for flight {flight_number} in {st.session_state.seat_class} class.")
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