import string
from typing import Optional

class Theater:
    def __init__(self, movie_name, rows, seats_per_row):
        self.movie_name = movie_name
        self.rows = rows
        self.seats_per_row = seats_per_row
        self.seating_map = [[None for _ in range(seats_per_row)] for _ in range(rows)]
        self.next_booking_id = 1
        
    def get_available_seats(self):
        return sum(row.count(None) for row in self.seating_map)
        
    def generate_booking_id(self):
        booking_id = f"HKG{self.next_booking_id:04d}"
        self.next_booking_id += 1
        return booking_id

def display_seating_map(seating_map, selected_seats=None):
    seats_per_row = len(seating_map[0])
    # Calculate width based on actual dots display (2 spaces per seat)
    total_width = 2 * seats_per_row  # Each seat takes 2 spaces (" •")
    
    # Center the word "SCREEN" with spaces between letters
    print("\n" + " ".join("SCREEN").center(total_width + 2))
    # Match exactly: 2 for "A ", then 2 per seat for " •"
    print("-" * (total_width + 2))  # Total width plus row letter and space
    
    # Display seats
    for row_idx in range(len(seating_map)-1, -1, -1):
        row = seating_map[row_idx]
        row_letter = chr(65 + row_idx)
        seats = []
        for col_idx in range(len(row)):
            if selected_seats and (row_idx, col_idx) in selected_seats:
                seats.append(" #")  # Selected seats
            elif row[col_idx] is not None:
                seats.append(" o")  # Booked seats
            else:
                seats.append(" •")  # Available seats
        print(f"{row_letter} {''.join(seats)}")
    
    # Print column numbers aligned with seats
    first_line = "  "  # Space for row letter and first space
    second_line = "  "  # Space for row letter and first space
    has_double_digits = False
    
    for i in range(seats_per_row):
        num = i + 1
        if num < 10:
            first_line += f" {num}"  # Single digits on first line
            second_line += "  "  # Skip second line for single digits
        else:
            has_double_digits = True
            first_line += f" {num//10}"  # Tens on first line
            second_line += f" {num%10}"  # Ones on second line
    
    print(first_line.rstrip())
    if has_double_digits:
        print(second_line.rstrip())

def parse_seat_position(position, rows, seats_per_row):
    if not position:
        return None
    if len(position) < 2:
        return None
    
    row = ord(position[0].upper()) - ord('A')
    try:
        col = int(position[1:]) - 1
    except ValueError:
        return None
        
    if 0 <= row < rows and 0 <= col < seats_per_row:
        return (row, col)
    return None

def find_consecutive_seats(seating_map, current_row, num_tickets):
    """Find best consecutive sequence of seats in a row"""
    seats_per_row = len(seating_map[0])
    middle = (seats_per_row - 1) // 2
    best_seats = []
    
    # Try sequences starting from each position around middle
    for start in range(max(0, middle - num_tickets), seats_per_row - num_tickets + 1):
        consecutive_seats = []
        for col in range(start, start + num_tickets):
            if col >= seats_per_row or seating_map[current_row][col] is not None:
                consecutive_seats = []
                break
            consecutive_seats.append((current_row, col))
        
        if len(consecutive_seats) == num_tickets:
            # If it's closer to middle than current best, use it
            if not best_seats or abs(middle - start) < abs(middle - best_seats[0][1]):
                best_seats = consecutive_seats
    
    return best_seats

def find_seats_from_middle(seating_map, current_row, num_tickets):
    """Find seats by filling from middle outwards"""
    seats_per_row = len(seating_map[0])
    middle = (seats_per_row - 1) // 2
    seats = []
    
    # Fill right side first
    col = middle
    while col < seats_per_row and len(seats) < num_tickets:
        if seating_map[current_row][col] is None:
            seats.append((current_row, col))
        col += 1
    
    # Then fill left side if needed
    col = middle - 1
    while col >= 0 and len(seats) < num_tickets:
        if seating_map[current_row][col] is None:
            seats.append((current_row, col))
        col -= 1
    
    return seats

def find_seats_in_empty_row(seating_map, current_row, num_tickets):
    """Find centered seats in an empty row"""
    seats_per_row = len(seating_map[0])
    middle = (seats_per_row - 1) // 2
    seats = []
    
    left = middle - ((num_tickets - 1) // 2)
    right = left + num_tickets - 1
    
    # Adjust if we go out of bounds
    if left < 0:
        left = 0
        right = min(seats_per_row - 1, num_tickets - 1)
    elif right >= seats_per_row:
        right = seats_per_row - 1
        left = max(0, right - num_tickets + 1)
    
    # Try filling the row
    for col in range(left, right + 1):
        if col >= 0 and col < seats_per_row and len(seats) < num_tickets:
            if seating_map[current_row][col] is None:
                seats.append((current_row, col))
    
    return seats

def find_seats_from_position(seating_map, start_pos, num_tickets):
    """Find seats starting from a specific position"""
    current_row, start_col = start_pos
    seats_per_row = len(seating_map[0])
    seats = []
    
    # Fill right from start position
    col = start_col
    while col < seats_per_row and len(seats) < num_tickets:
        if seating_map[current_row][col] is None:
            seats.append((current_row, col))
        col += 1
    
    # Fill left if needed
    col = start_col - 1
    while col >= 0 and len(seats) < num_tickets:
        if seating_map[current_row][col] is None:
            seats.append((current_row, col))
        col -= 1
    
    return seats

def find_default_seats(seating_map, num_tickets, start_pos=None):
    """Main function to find best available seats"""
    rows = len(seating_map)
    seats = []
    
    if start_pos:
        current_row, _ = start_pos
        seats = find_seats_from_position(seating_map, start_pos, num_tickets)
        if len(seats) < num_tickets:
            current_row += 1
    else:
        current_row = 0
    
    # Continue with remaining rows if needed
    while current_row < rows and len(seats) < num_tickets:
        remaining_tickets = num_tickets - len(seats)
        is_empty_row = all(seat is None for seat in seating_map[current_row])
        
        if is_empty_row:
            new_seats = find_seats_in_empty_row(seating_map, current_row, remaining_tickets)
        else:
            # Try consecutive seats first
            new_seats = find_consecutive_seats(seating_map, current_row, remaining_tickets)
            if not new_seats:
                new_seats = find_seats_from_middle(seating_map, current_row, remaining_tickets)
        
        seats.extend(new_seats)
        current_row += 1
    
    # Sort seats within each row
    seats.sort()
    
    return seats if len(seats) == num_tickets else []

def validate_ticket_quantity(tickets_input: str, available_seats: int) -> Optional[int]:
    """
    Validate the ticket quantity input.
    Returns the number of tickets if valid, None otherwise.
    """
    if not tickets_input:
        return None
        
    try:
        num_tickets = int(tickets_input)
        if num_tickets <= 0:
            print("Please enter a positive number of tickets.")
            print()
            return None
        if num_tickets > available_seats:
            print(f"Sorry, only {available_seats} seats available.")
            print()
            return None
        return num_tickets
    except ValueError:
        print("Please enter a valid number.")
        print()
        return None

def validate_seat_position(position: str, theater, seating_map) -> Optional[tuple]:
    """
    Validate the seat position input.
    Returns (row, col) tuple if valid, None otherwise.
    """
    start_pos = parse_seat_position(position, theater.rows, theater.seats_per_row)
    if not start_pos:
        print("Invalid position. Please try again.")
        print()
        return None
    
    # Check if seat is already taken
    row, col = start_pos
    if seating_map[row][col] is not None:
        print("Sorry, this position is already taken. Please select another position.")
        print()
        return None
        
    return start_pos

def book_tickets(theater):
    print("Enter the number of tickets to book, or enter blank to go back to the main menu:")
    print("> ", end="")
    tickets_input = input()
    print()
    
    num_tickets = validate_ticket_quantity(tickets_input, theater.get_available_seats())
    if num_tickets is None:
        return
    
    booking_id = theater.generate_booking_id()
    selected_seats = find_default_seats(theater.seating_map, num_tickets)
    
    while True:
        print(f"Booking id: {booking_id}")
        print("Selected seats:")
        display_seating_map(theater.seating_map, selected_seats)
        
        print("Enter blank to accept seat selection, or enter a new seating position")
        print("> ", end="")
        new_pos = input()
        print()
        
        if not new_pos:
            break
            
        start_pos = validate_seat_position(new_pos, theater, theater.seating_map)
        if start_pos is None:
            continue
            
        new_seats = find_default_seats(theater.seating_map, num_tickets, start_pos)
        if not new_seats:
            print("Cannot allocate seats from that position. Please try again.")
            continue
            
        selected_seats = new_seats
    
    # Confirm booking
    for row, col in selected_seats:
        theater.seating_map[row][col] = booking_id
    
    print(f"Successfully reserved {num_tickets} {theater.movie_name} tickets.")
    print(f"Booking id: {booking_id} confirmed")
    print()

def check_booking(theater):
    while True:
        print()
        print("Enter booking id, or enter blank to go back to the main menu:")
        print("> ", end="")
        booking_id = input().strip()
        print()  # Add empty line after input
        
        if not booking_id:
            return
            
        # Find all seats with this booking ID
        booked_seats = []
        for row_idx, row in enumerate(theater.seating_map):
            for col_idx, seat in enumerate(row):
                if seat == booking_id:
                    booked_seats.append((row_idx, col_idx))
        
        if not booked_seats:
            print(f"No booking found with id: {booking_id}")
            print()
            continue  # Changed from return to continue to keep loop going
        
        print(f"Booking id: {booking_id}:")
        print("Selected seats:")
        display_seating_map(theater.seating_map, booked_seats)
        print()

def get_theater_setup():
    while True:
        try:
            print()
            print("Please define movie title and seating map in")
            print("[Title][Row][SeatsPerRow] format:")
            print("> ", end="")
            setup = input().split()
            print()
            
            if len(setup) != 3:
                print("Error: Please provide all three values (Title, Rows, Seats per Row)")
                continue
            
            title = setup[0]
            rows = int(setup[1])
            seats_per_row = int(setup[2])
            
            if not (1 <= rows <= 26):
                print("Error: Number of rows must be between 1 and 26")
                continue
                
            if not (1 <= seats_per_row <= 50):
                print("Error: Seats per row must be between 1 and 50")
                continue
                
            return title, rows, seats_per_row
            
        except ValueError:
            print("Error: Row and seats per row must be numbers")

def main():
    
    # Get initial theater setup
    title, rows, seats_per_row = get_theater_setup()
    theater = Theater(title, rows, seats_per_row)
    
    while True:
        print("Welcome to Rocket Cinemas")
        print(f"[1] Book tickets for {theater.movie_name} ({theater.get_available_seats()} seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        print("Please enter your selection:")
        print("> ", end="")
        choice = input()
        print()
        
        if choice == "1":
            book_tickets(theater)
        elif choice == "2":
            check_booking(theater)
        elif choice == "3":
            print()
            print("Thank you for using Rocket Cinemas system. Bye!")
            break
        else:
            print("Invalid selection. Please try again.")
            print()

if __name__ == "__main__":
    main() 