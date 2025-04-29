
# Flight Scheduling Application

## Description
This Flight Scheduling Application is designed as an educational project to deepen understanding of fundamental algorithmic concepts through practical application. The primary goal is to explore the design and functionality of fundamental searching, sorting, and traversing algorithms, comprehend various methodologies for assessing the efficiency of algorithms, and compare them based on performance metrics including time and space considerations.

For this assignment, the application facilitates the booking and scheduling of flights, utilizing a variety of data structures covered in lectures. Users can schedule passengers, cancel bookings, and check passenger statuses, all while managing a realistic simulation of flight properties and seating arrangements.

## Flight Properties
Each flight in the application has several attributes:

Flight Number: Integer from 0 to 999.
Departure Airport
Departure Date
Arrival Airport
Seating List: Divided into three classes:
First Class: Example - 5 seats (Seats 1, 2, 3, 4, 5)
Business Class: Example - 10 seats (Seats 6 - 15)
Economy Class: Example - 20 seats (Seats 16 - 35)
## Features
Schedule a Passenger: Select a flight and class. If full, add to a waitlist specific to each class.
Cancel a Passenger: Remove a passenger and potentially fill the spot from the waitlist, updating the next passenger's status.
Passenger Status: Display detailed flight info for both scheduled passengers and those on waitlists.
Flight Information: Print comprehensive details including airports, date, seating, and passenger names.
Algorithm and Data Structure Requirements


## Data Structures: Queues, piles, graphs, or trees as discussed in lectures.
This project incorporates at least one of each:

Sorting Algorithms: Merge Sort, Quick Sort, Radix Sort and others
Searching Algorithms: Hash Table Searching and Binary Search Trees (BST)
The design encourages thinking about algorithmic efficiency and data handling, with potential future extensions to include more sophisticated structures and algorithms as the course progresses.

## System Structure
flight-scheduling

📁 flight-scheduling
│
├── 📁 src                  # Source files
│   ├── 📄 app_04.py           # Main application file
│   ├── 📄 booking_manager_03.py    # Configuration settings for the app
│   ├── 📄 unit_tests.py           # Unit testing
│   ├── 📁 data                 # Data files
│       └── 📄 flights_pile.py       # storing flight data
│       └── 📄 passenger_data.py       # storing passengers data
│   ├── 📁 cl                 # class files 
│       └── 📄 graph.py       # graph structure
│   ├── 📁 sceduling                 # Algorithms
│       └── 📄 searchers.py       # Searchering algorithms
│       └── 📄 sorters.py       # Sorting algorithms
└── 📄 requirements.txt     # Project dependencies
│
└── 📄 README.md     # readme file
│
└── 📄 requirements.txt     # Project dependencies
│
└── 📄 .gitignore    


## Features
- Schedule flights and manage bookings
- Assign seats to passengers based on class availability
- Handle waitlisting for full flights
- Search for flights and passenger details
- Cancel bookings and automatically update waitlisted passengers

## Getting Started

### Prerequisites
- Python 3.8 or above

### Installation
Clone the repository to your local machine:

git clone https://github.com/yourusername/flight-scheduling-system.git


Navigate to the cloned directory:

cd flight-scheduling-system


Install the required dependencies:

pip install -r requirements.txt


### Usage
Run the system with:

stremlit run dir/app_04.py

or visit: https://flightscheduling1.streamlit.app/




