import string

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
    total_width = len(seating_map[0]) * 2  # Calculate width based on seats
    
    # Center the word "SCREEN"
    print("\n" + "SCREEN".center(total_width + 2))  # +2 for the row letter and space
    print("—" + "-" * total_width)
    
    # Display seats
    for row_idx in range(len(seating_map)-1, -1, -1):
        row = seating_map[row_idx]
        row_letter = chr(65 + row_idx)
        seats = []
        for col_idx in range(len(row)):
            if selected_seats and (row_idx, col_idx) in selected_seats:
                seats.append("#")  # Selected seats
            elif row[col_idx] is not None:
                seats.append("o")  # Booked seats
            else:
                seats.append("•")  # Available seats
        print(f"{row_letter} {' '.join(seats)}")
    
    # Print column numbers aligned with seats
    print("  " + ' '.join(str(i+1) for i in range(len(seating_map[0]))))

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

def find_default_seats(seating_map, num_tickets, start_pos=None):
    rows = len(seating_map)
    seats_per_row = len(seating_map[0])
    seats = []
    
    if start_pos:
        current_row, start_col = start_pos
    else:
        # Start from furthest row from screen (row 0, which is A)
        current_row = 0
        # Start from middle of row
        middle = (seats_per_row - 1) // 2
        start_col = middle - ((num_tickets - 1) // 2)
    
    while current_row < rows and len(seats) < num_tickets:
        middle = (seats_per_row - 1) // 2
        remaining_tickets = num_tickets - len(seats)
        
        # Check if row is empty
        is_empty_row = all(seat is None for seat in seating_map[current_row])
        
        if is_empty_row:
            # For empty rows, center the remaining tickets
            left = middle - ((remaining_tickets - 1) // 2)
            right = left + remaining_tickets - 1
            
            # Adjust if we go out of bounds
            if left < 0:
                left = 0
                right = min(seats_per_row - 1, remaining_tickets - 1)
            elif right >= seats_per_row:
                right = seats_per_row - 1
                left = max(0, right - remaining_tickets + 1)
                
            # Try filling the current row with available seats
            for col in range(left, right + 1):
                if col >= 0 and col < seats_per_row and len(seats) < num_tickets:
                    if seating_map[current_row][col] is None:
                        seats.append((current_row, col))
        else:
            # For partially filled rows, fill right side first
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
        
        # Move to next row if we still need more seats
        if len(seats) < num_tickets:
            current_row += 1
            
    # Sort seats within each row to maintain left-to-right order
    seats.sort()
    
    return seats if len(seats) == num_tickets else []

def book_tickets(theater):
    print()
    print("Enter the number of tickets to book, or enter blank to go back to")
    print("the main menu:")
    print("> ", end="")
    tickets_input = input()
    print()  # Add empty line after input
    
    if not tickets_input:
        return
        
    try:
        num_tickets = int(tickets_input)
        if num_tickets <= 0:
            print("Please enter a positive number of tickets.")
            print()  # Add empty line after error message
            return
        if num_tickets > theater.get_available_seats():
            print(f"Sorry, only {theater.get_available_seats()} seats available.")
            print()  # Add empty line after error message
            return
    except ValueError:
        print("Please enter a valid number.")
        print()  # Add empty line after error message
        return
    
    booking_id = theater.generate_booking_id()
    selected_seats = find_default_seats(theater.seating_map, num_tickets)
    
    while True:
        print(f"Booking id: {booking_id}")
        print("Selected seats:")
        display_seating_map(theater.seating_map, selected_seats)
        
        print("Enter blank to accept seat selection, or enter a new seating")
        print("position")
        print("> ", end="")
        new_pos = input()
        
        if not new_pos:
            break
            
        start_pos = parse_seat_position(new_pos, theater.rows, theater.seats_per_row)
        if not start_pos:
            print("Invalid position. Please try again.")
            print()
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
            print("Please define movie title and seating map in")
            print("[Title][Row][SeatsPerRow] format:")
            print("> ", end="")
            setup = input().split()
            
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
    print("Welcome to Rocket Cinemas")
    
    # Get initial theater setup
    title, rows, seats_per_row = get_theater_setup()
    theater = Theater(title, rows, seats_per_row)
    
    while True:
        print(f"[1] Book tickets for {theater.movie_name} ({theater.get_available_seats()} seats available)")
        print("[2] Check bookings")
        print("[3] Exit")
        print("Please enter your selection:")
        print("> ", end="")
        choice = input()
        
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