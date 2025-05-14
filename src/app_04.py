import streamlit as st
from collections import deque
from booking_manager_03 import BookingManager
from cl.graph import Graph
from algorithms.searchers import FlightRedBlackTree, PassengerBST
from utils import parse_airline_res_db
import pandas as pd
import re 
from streamlit.components.v1 import html
from algorithms.sorters import merge_sort, quick_sort, radix_sort


# Path to the AirlineResDB.txt file
airline_res_db_path = "../AirlineResDB.txt"

# Parse the AirlineResDB.txt file
airline_res_db = parse_airline_res_db(airline_res_db_path)

# Extract relevant data
airport_data = {entry["Airport_code"]: entry for entry in airline_res_db["Airport"]}
flight_data = {entry["Flight_number"]: entry for entry in airline_res_db["Flight"]}
seat_reservations = airline_res_db["Seat_reservation"]
leg_instance_data = airline_res_db["Leg_instance"]

# Initialize data structures
flights_graph = Graph()  # Graph to store flight information
passengers_graph = Graph()  # Graph to store passenger information
flights_table = FlightRedBlackTree()  # RedBlackTree table to quickly search flights
passengers_tree = PassengerBST()  # Binary search tree to quickly search passengers
flights_stack = []  # Stack to store flights
confirmed_passengers_stack = []  # Stack to store confirmed passengers
waitlisted_passengers_queue = deque()  # Queue to store waitlisted passengers

# Populate flights from the parsed data
for flight in flight_data.values():
    flight_number = flight["Flight_number"]
    departure = flight.get("Departure_airport", "Unknown")
    arrival = flight.get("Arrival_airport", "Unknown")
    flight_leg = next(
        (leg for leg in airline_res_db["Flight_leg"] if leg["Flight_number"] == flight_number),
        None
    )
    if flight_leg:
        departure = flight_leg["Departure_airport_code"]
        arrival = flight_leg["Arrival_airport_code"]
    else:
        departure = "Unknown"
        arrival = "Unknown"
        
    weekdays = flight.get("Weekdays", "Unknown")
    seating_list = {
        "First": [1, 5, 9, 11, 21],
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
        airport_data,
        flight_data,
        leg_instance_data
    )
else:
    manager = st.session_state['manager']


def book_passenger():
    if st.session_state.booking_passenger_name and st.session_state.booking_passenger_id and st.session_state.booking_flight_number and st.session_state.seat_class:
        passenger_id = st.session_state.booking_passenger_id

        if not re.match(r"^555-\d{4}$", passenger_id):
            return "PassengerID must be in the format '555-xxxx' (e.g., 555-1234)."

        flight_number = st.session_state.booking_flight_number

        # Check if the flight has "Unknown" departure or arrival
        flight = next((f for f in st.session_state['manager'].flights_stack if f[0] == flight_number), None)
        if flight and (flight[1] == "Unknown" or flight[2] == "Unknown"):
            # Validate and update departure and arrival airports
            departure = st.session_state.get('booking_departure_airport', '').strip()
            arrival = st.session_state.get('booking_arrival_airport', '').strip()

            if not departure or not arrival:
                return "Please enter both departure and arrival airports."

            if departure not in st.session_state['manager'].airport_data or arrival not in st.session_state['manager'].airport_data:
                return "Invalid airport codes. Please check and try again."

            # Update the flight details
            flight[1] = departure
            flight[2] = arrival

        # Proceed with booking
        result = st.session_state['manager'].book_passenger(
            [passenger_id, st.session_state.booking_passenger_name],
            flight_number,
            st.session_state.seat_class
        )

        return result
    return "Please enter all the details."




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
        passenger_id = st.session_state.status_passenger_id

        # Validate PassengerID format (555-xxxx)
        if not re.match(r"^555-\d{4}$", passenger_id):
            st.error("PassengerID must be in the format '555-xxxx' (e.g., 555-1234).")
            return

        # Check the passenger status
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

        

def get_available_flights():
    """
    Fetch and display the list of available flights with relevant details.
    """
    # Add search and sort options
    st.write("### Search and Sort Flights")
    st.markdown(
        "ℹ️ **Note:** If the flight is not scheduled yet/or has no bookings, the Departure and Arrival airport codes will be displayed as *Unknown*."
        )
    search_option = st.selectbox("Search by", ["None", "Flight Number", "Departure Airport", "Arrival Airport"], key="search_option")
    search_query = st.text_input("Enter search query", key="search_query", placeholder="E.g., A123 or SFO")
    sort_option = st.selectbox("Sort by", ["None", "Flight Number", "Departure Airport", "Arrival Airport", "Available Seats"], key="sort_option")

    flights_info = []
    for flight in st.session_state['manager'].flights_stack:
        flight_number, departure, arrival, weekdays, seating_list = flight

        # Count booked and available seats by class
        booked_seats = {cls: 0 for cls in seating_list.keys()}
        available_seats = {cls: len(seats) for cls, seats in seating_list.items()}

        for passenger in st.session_state['manager'].confirmed_passengers_stack:
            if passenger[2] == flight_number:
                seat_class = passenger[4]
                booked_seats[seat_class] += 1
                available_seats[seat_class] -= 1

        # Retrieve departure and arrival airport names
        departure_airport = st.session_state['manager'].airport_data.get(departure, {}).get("Name", departure)
        arrival_airport = st.session_state['manager'].airport_data.get(arrival, {}).get("Name", arrival)

        # Add flight details to the list
        flights_info.append({
            "Flight Number": flight_number,
            "Departure": f"{departure_airport} ({departure})",
            "Arrival": f"{arrival_airport} ({arrival})",
            "Weekdays": weekdays,
            "Booked Seats": booked_seats,
            "Available Seats": sum(available_seats.values())
        })

    # Apply search filter
    if search_option != "None" and search_query:
        if search_option == "Flight Number":
            flights_info = [flight for flight in flights_info if search_query.lower() in flight["Flight Number"].lower()]
        elif search_option == "Departure Airport":
            flights_info = [flight for flight in flights_info if search_query.lower() in flight["Departure"].lower()]
        elif search_option == "Arrival Airport":
            flights_info = [flight for flight in flights_info if search_query.lower() in flight["Arrival"].lower()]

    # Apply sorting
    if sort_option != "None":
        if sort_option == "Flight Number":
            flights_info = radix_sort(flights_info, get_attribute=lambda x: x["Flight Number"])
        elif sort_option == "Departure Airport":
            flights_info = merge_sort(flights_info, key=lambda x: x["Departure"])
        elif sort_option == "Arrival Airport":
            flights_info = merge_sort(flights_info, key=lambda x: x["Arrival"])
        elif sort_option == "Available Seats":
            flights_info = quick_sort(flights_info, key=lambda x: x["Available Seats"])

    # Display the flight information
    if flights_info:
        st.write("### Available Flights")
        for flight in flights_info:
            st.write(f"**Flight Number:** {flight['Flight Number']}")
            st.write(f"**Departure:** {flight['Departure']}")
            st.write(f"**Arrival:** {flight['Arrival']}")
            st.write(f"**Weekdays:** {flight['Weekdays']}")
            st.write("**Seats by Class:**")
            for cls, count in flight["Booked Seats"].items():
                st.write(f"- {cls}: {count} booked, {flight['Available Seats']} available")
            st.markdown("---")
    else:
        st.info("No flights available.")


def main():
    if "nav_option" not in st.session_state:
        st.session_state.nav_option = "Book Passenger"

    st.set_page_config(page_title="Flight Dashboard", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Flight Scheduling Dashboard</h1>", unsafe_allow_html=True)

    # --- Navigation bar ---
    nav_buttons = {
        "Book Passenger": "📅 Book Passenger",
        "Cancel Booking": "🗑️ Cancel Booking",
        "Check Status": "🔍 Check Status",
        "Flight Information": "✈️ Flight Information",
        "Manage Waitlist": "🕒 Manage Waitlist",
        "Available Flights": "🛫 Available Flights"        
    }

    nav_cols = st.columns(len(nav_buttons))
    for i, (nav_key, nav_label) in enumerate(nav_buttons.items()):
        if nav_cols[i].button(nav_label, use_container_width=True):
            st.session_state.nav_option = nav_key

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Section content based on selection ---
    if st.session_state.nav_option == "Available Flights":
        with st.expander("🛫 View Available Flights", expanded=True):
            get_available_flights()

    # --- Section content based on selection ---
    if st.session_state.nav_option == "Book Passenger":
        with st.expander("📅 Book a Passenger", expanded=False):
            st.markdown(
            "ℹ️ **Note:** If the flight is not scheduled yet, you will be prompted to enter Departure and Arrival airport codes."
            )
            st.text_input("Enter Passenger Name", value=st.session_state.get('booking_passenger_name', ''), key='booking_passenger_name', placeholder="John Doe")
            st.text_input("Enter Passenger ID", value=st.session_state.get('booking_passenger_id', ''), key='booking_passenger_id', placeholder="555-xxxx")
            st.text_input("Enter Flight Number", value=st.session_state.get('booking_flight_number', ''), key='booking_flight_number', placeholder="A123")
            seat_classes = ["First", "Business", "Economy"]
            st.selectbox("Choose a Class", seat_classes, index=seat_classes.index(st.session_state.get('seat_class', seat_classes[0])), key='seat_class')

            # Check if the flight requires departure and arrival input
            flight_number = st.session_state.get('booking_flight_number', '').strip()
            flight = next((f for f in st.session_state['manager'].flights_stack if f[0] == flight_number), None)
            if flight and (flight[1] == "Unknown" or flight[2] == "Unknown"):
                st.text_input("Enter Departure Airport Code", key="booking_departure_airport", placeholder="E.g., SFO")
                st.text_input("Enter Arrival Airport Code", key="booking_arrival_airport", placeholder="E.g., JFK")

            if st.button("✈️ Book Passenger", key="book_passenger"):
                result = book_passenger()
                if result:
                    if "booked on flight" in result.lower():
                        st.success(result, icon="✅")
                    elif "waitlist" in result.lower():
                        st.warning(result, icon="⏳")
                    else: 
                        st.error(result)


    elif st.session_state.nav_option == "Cancel Booking":
        with st.expander("🗑️ Cancel a Booking", expanded=False):
            st.text_input("Enter Passenger ID", value=st.session_state.get('cancellation_passenger_id', ''), key='cancellation_passenger_id', placeholder="555-xxxx")
            st.text_input("Enter Flight Number", value=st.session_state.get('cancellation_flight_number', ''), key='cancellation_flight_number', placeholder="A123")

            if st.button("❌ Cancel Booking", key="cancel_booking"):
                passenger_id = st.session_state.get('cancellation_passenger_id')
                flight_number = st.session_state.get('cancellation_flight_number')
                if passenger_id and flight_number:
                    cancel_passenger()
                else:
                    st.error("Please enter all the details.")

    elif st.session_state.nav_option == "Check Status":
        with st.expander("🔍 Check Passenger Status", expanded=False):
            st.text_input("Enter Passenger ID", value=st.session_state.get('status_passenger_id', ''), key='status_passenger_id', placeholder="555-xxxx")

            if st.button("🧐 Check Status", key="check_status"):
                if not st.session_state.status_passenger_id:
                    st.error("Please enter the passenger ID.")
                else:
                    check_passenger_status()

    elif st.session_state.nav_option == "Flight Information":
        with st.expander("✈️ Check Flight Information", expanded=False):
            st.text_input("Enter Flight Number", value=st.session_state.get('flight_number', ''), key='flight_number', placeholder="A123")
            if st.button("📄 Check Flight Info", key="check_flight_info"):
                if not st.session_state.get("flight_number"):
                    st.error("Please enter the flight number.")
                else:
                    check_flight_info()

    elif st.session_state.nav_option == "Manage Waitlist":
        with st.expander("🕒 Manage Waitlist", expanded=False):
            # View the waitlist for a specific flight
            st.text_input("Enter Flight Number", value=st.session_state.get('waitlist_flight_number', ''), key='waitlist_flight_number', placeholder="A123")
            if st.button("📄 View Waitlist", key="view_waitlist"):
                flight_number = st.session_state.get('waitlist_flight_number')
                if flight_number:
                    waitlist = st.session_state['manager'].get_waitlist(flight_number)
                    if waitlist:
                        st.write("### Current Waitlist:")
                        for seat_class, passengers in waitlist.items():
                            st.write(f"**{seat_class} Class:**")
                            if passengers:
                                for passenger in passengers:
                                    st.write(
                                        f"- Position {passenger['position']}: {passenger['passenger_name']} "
                                        f"(ID: {passenger['passenger_id']})"
                                    )
                            else:
                                st.write("No passengers in this class.")
                    else:
                        st.info("No passengers on the waitlist for this flight.")
                else:
                    st.error("Please enter the flight number.")


            st.markdown("---")
        seat_classes = ["First", "Business", "Economy"]

        # Remove a passenger from the waitlist
        st.text_input("Enter Passenger ID to Remove", value=st.session_state.get('waitlist_remove_passenger_id', ''), key='waitlist_remove_passenger_id', placeholder="555-xxxx")
        st.text_input("Enter Flight Number", value=st.session_state.get('waitlist_remove_flight_number', ''), key='waitlist_remove_flight_number', placeholder="A123")
        st.selectbox("Choose a Class to Remove From", seat_classes, index=0, key='waitlist_remove_seat_class')

        if st.button("❌ Remove from Waitlist", key="remove_from_waitlist"):
            passenger_id = st.session_state.get('waitlist_remove_passenger_id')
            flight_number = st.session_state.get('waitlist_remove_flight_number')
            seat_class = st.session_state.get('waitlist_remove_seat_class')

            if passenger_id and flight_number and seat_class:
                result = st.session_state['manager'].remove_from_waitlist(passenger_id, flight_number, seat_class)
                if "removed from the waitlist" in result.lower():
                    st.success(result)
                else:
                    st.warning(result)
            else:
                st.error("Please enter all the details.")

    # --- Styling ---
    st.markdown("""
    <style>
        .element-container button {
            background-color: #f0f2f6;
            color: #000000;
            border-radius: 0.5rem;
            margin-right: 5px;
            height: 3em;
            font-weight: bold;
        }
        .element-container button:hover {
            background-color: #1D9BF0;
            color: white;
        }
        .stExpander > div:first-child {
            background-color: #f8f9fa;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
