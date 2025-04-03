import unittest
from theater_booking import (
    Theater, find_default_seats, parse_seat_position, 
    get_theater_setup, book_tickets, check_booking
)

class TestTheaterBooking(unittest.TestCase):
    def setUp(self):
        # This runs before each test
        self.theater = Theater("Test Movie", 5, 10)  # 5 rows, 10 seats per row

    def test_initial_available_seats(self):
        """Test that new theater has all seats available"""
        self.assertEqual(self.theater.get_available_seats(), 50)

    def test_booking_id_generation(self):
        """Test that booking IDs are generated correctly"""
        self.assertEqual(self.theater.generate_booking_id(), "HKG0001")
        self.assertEqual(self.theater.generate_booking_id(), "HKG0002")

    def test_find_default_seats_center(self):
        """Test that 3 seats are allocated in center of first row"""
        seats = find_default_seats(self.theater.seating_map, 3)
        expected = [(0, 3), (0, 4), (0, 5)]  # 3 4 5 because of the array indices
        self.assertEqual(seats, expected)

    def test_find_default_seats_multiple_rows(self):
        """Test allocation of seats across multiple rows"""
        # Book 12 seats in a 10-seat row theater
        seats = find_default_seats(self.theater.seating_map, 12)
        # First 10 seats should be in row A
        first_row = [(0, i) for i in range(10)]
        # Remaining 2 seats should be centered in row B
        second_row = [(1, 4), (1, 5)]
        self.assertEqual(seats, first_row + second_row)

    def test_parse_seat_position(self):
        """Test seat position parsing"""
        self.assertEqual(parse_seat_position("A1", 5, 10), (0, 0))
        self.assertEqual(parse_seat_position("C5", 5, 10), (2, 4))
        self.assertIsNone(parse_seat_position("Z1", 5, 10))  # Invalid row
        self.assertIsNone(parse_seat_position("A11", 5, 10))  # Invalid seat

    def test_booking_fills_seats(self):
        """Test that booking actually fills the seats"""
        # Book 3 seats
        booking_id = self.theater.generate_booking_id()
        seats = find_default_seats(self.theater.seating_map, 3)
        for row, col in seats:
            self.theater.seating_map[row][col] = booking_id
        
        # Check seats are filled
        self.assertEqual(self.theater.get_available_seats(), 47)

    def test_find_default_seats_partial_row(self):
        """Test that seats are allocated correctly in partially filled row"""
        # First book 3 seats in the middle
        first_booking = find_default_seats(self.theater.seating_map, 3)
        for row, col in first_booking:
            self.theater.seating_map[row][col] = "BOOKING1"
        
        # Then book 5 more seats
        second_booking = find_default_seats(self.theater.seating_map, 5)
        expected = [(0, 2), (0, 6), (0, 7), (0, 8), (0, 9)]  
        self.assertEqual(second_booking, expected)

    def test_find_default_seats_new_row(self):
        """Test that seats in a new row are centered"""
        # Fill first row
        for col in range(10):
            self.theater.seating_map[0][col] = "BOOKING1"
        
        # Book 3 seats in next row
        seats = find_default_seats(self.theater.seating_map, 3)
        expected = [(1, 3), (1, 4), (1, 5)]  # Centered in second row
        self.assertEqual(seats, expected)

    def test_theater_setup_validation(self):
        """Test that theater setup properly validates input"""
        from unittest.mock import patch
        
        # Patch both input and print
        with patch('builtins.input', return_value="Movie 5 10"), \
             patch('builtins.print'):  # Suppress print statements
            title, rows, seats = get_theater_setup()
            self.assertEqual(rows, 5)
            self.assertEqual(seats, 10)
        
        with patch('builtins.input', side_effect=["Movie 27 10", "Movie 5 10"]), \
             patch('builtins.print'):  # Suppress print statements
            title, rows, seats = get_theater_setup()
            self.assertEqual(rows, 5)
        
        with patch('builtins.input', side_effect=["Movie 5 51", "Movie 5 10"]), \
             patch('builtins.print'):  # Suppress print statements
            title, rows, seats = get_theater_setup()
            self.assertEqual(seats, 10)

    def test_ticket_quantity_validation(self):
        """Test validation of ticket quantities"""
        from unittest.mock import patch
        
        test_cases = [
            ("", None),                # Empty input should return None
            ("0", None),              # Zero tickets not allowed
            ("-1", None),             # Negative tickets not allowed
            ("abc", None),            # Non-numeric input not allowed
            ("51", None),             # More than available seats (50) not allowed
            ("41", None),             # More than available seats (40) not allowed
            ("40", 40),              # Exactly available seats is allowed
            ("10", 10)               # Valid number of tickets
        ]
        
        for input_val, expected in test_cases:
            # Create fresh theater for each test case
            self.theater = Theater("Test Movie", 5, 10)
            
            # Fill up some seats first (book 10 seats)
            booking_id = self.theater.generate_booking_id()
            seats = find_default_seats(self.theater.seating_map, 10)
            for row, col in seats:
                self.theater.seating_map[row][col] = booking_id
            
            # Now only 40 seats are available
            
            # Mock both the ticket number input and the seat selection input
            with patch('builtins.input', side_effect=[input_val, ""]), \
                 patch('builtins.print'):  # Suppress print statements
                result = book_tickets(self.theater)
                if expected is None:
                    self.assertIsNone(result)
                else:
                    self.assertEqual(self.theater.get_available_seats(), 
                                  40 - expected)  # 40 was available before

    def test_find_default_seats_from_position(self):
        """Test that seats are allocated from a specified position"""
        # Try to book 4 seats from position D10 (row 3, col 9)
        start_pos = (3, 9)  # D10 - within our 5-row theater
        seats = find_default_seats(self.theater.seating_map, 4, start_pos)
        
        # Should get seats starting from D10 and continuing left
        expected = [(3, 6), (3, 7), (3, 8), (3, 9)]
        self.assertEqual(sorted(seats), sorted(expected))
        
        # Test with position that requires moving to next row
        start_pos = (1, 8)  # B9
        seats = find_default_seats(self.theater.seating_map, 4, start_pos)
        # Should try to fit all seats in row B first
        expected = [(1, 6), (1, 7), (1, 8), (1, 9)]  # B7,B8,B9,B10
        self.assertEqual(sorted(seats), sorted(expected))

    def test_find_default_seats_consecutive_priority(self):
        """Test that consecutive seats are prioritized"""
        # Fill seats A8 and A9
        self.theater.seating_map[0][7] = "TAKEN"  # A8
        self.theater.seating_map[0][8] = "TAKEN"  # A9
        
        # Book 4 seats
        seats = find_default_seats(self.theater.seating_map, 4)
        # Should get A4,A5,A6,A7 instead of A5,A6,A7,A10
        expected = [(0, 3), (0, 4), (0, 5), (0, 6)]  # A4-A7
        self.assertEqual(seats, expected)
        
        # Test another scenario
        self.theater = Theater("Test Movie", 5, 10)  # Fresh theater
        # Fill A6
        self.theater.seating_map[0][5] = "TAKEN"  # A6
        
        # Book 3 seats
        seats = find_default_seats(self.theater.seating_map, 3)
        # Should get A3,A4,A5 instead of A7,A8,A9
        expected = [(0, 2), (0, 3), (0, 4)]  # A3-A5
        self.assertEqual(seats, expected)

    def test_booking_from_taken_position(self):
        """Test booking from a position where some seats are already taken"""
        from unittest.mock import patch
        
        # First book some seats (A4, A5, A6)
        booking_id = self.theater.generate_booking_id()
        first_seats = [(0, 3), (0, 4), (0, 5)]
        for row, col in first_seats:
            self.theater.seating_map[row][col] = booking_id
        
        # Try to book 4 seats starting from A5 (which is taken)
        with patch('builtins.input', side_effect=["4", "A5", "A7", ""]), \
             patch('builtins.print') as mock_print:
            result = book_tickets(self.theater)
            # Verify the error message was displayed
            mock_print.assert_any_call("Sorry, this position is already taken. Please select another position.")
            # Verify final state after successful booking from A7
            self.assertEqual(self.theater.get_available_seats(), 43)  # 50 - 3 - 4 = 43

    def test_invalid_seat_selection(self):
        """Test invalid seat selection inputs"""
        from unittest.mock import patch
        
        # Test cases for invalid seat positions
        invalid_inputs = [
            "A",        # Too short
            "AA1",      # Invalid format
            "12",       # No row letter
            "A0",       # Invalid column number
            "A-1"       # Negative column number
        ]
        
        for invalid_input in invalid_inputs:
            with patch('builtins.input', side_effect=["2", invalid_input, ""]), \
                 patch('builtins.print') as mock_print:
                result = book_tickets(self.theater)
                mock_print.assert_any_call("Invalid position. Please try again.")

    def test_check_booking(self):
        """Test checking existing and non-existing bookings"""
        from unittest.mock import patch
        
        # Make a booking first
        booking_id = self.theater.generate_booking_id()
        seats = [(0, 3), (0, 4), (0, 5)]
        for row, col in seats:
            self.theater.seating_map[row][col] = booking_id
        
        # Test valid booking check
        with patch('builtins.input', side_effect=[booking_id, ""]), \
             patch('builtins.print') as mock_print:
            check_booking(self.theater)
            mock_print.assert_any_call(f"Booking id: {booking_id}:")
        
        # Test non-existent booking
        with patch('builtins.input', side_effect=["INVALID", ""]), \
             patch('builtins.print') as mock_print:
            check_booking(self.theater)
            mock_print.assert_any_call("No booking found with id: INVALID")

if __name__ == '__main__':
    unittest.main() 