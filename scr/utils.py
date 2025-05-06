import re

def parse_airline_res_db(file_path):
    """
    Parse the AirlineResDB.txt file into structured data.

    Args:
    - file_path: Path to the AirlineResDB.txt file.

    Returns:
    - A dictionary containing parsed data.
    """
    data = {}
    current_section = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            # Detect section headers
            match = re.match(r"(\w+)\s*=\s*{", line)
            if match:
                current_section = match.group(1)
                data[current_section] = []
                continue

            # Detect section end
            if line == "}":
                current_section = None
                continue

            # Parse section content
            if current_section:
                data[current_section].append(line)

    # Convert lists of strings into structured dictionaries
    for section, lines in data.items():
        if section == "Airport":
            data[section] = [
                dict(zip(["Airport_code", "Name", "City", "State"], line.split(", ")))
                for line in lines
            ]
        elif section == "Flight":
            data[section] = [
                dict(zip(["Flight_number", "Airline", "Weekdays"], line.split(", ")))
                for line in lines
            ]
        elif section == "Seat_reservation":
            data[section] = [
                dict(zip(
                    ["Flight_number", "Leg_number", "Date", "Seat_number", "Customer_name", "Customer_phone"],
                    line.split(", ")
                ))
                for line in lines
            ]
        # Add parsing logic for other sections as needed

    return data