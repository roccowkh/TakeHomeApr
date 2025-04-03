import unittest
from theater_booking import Theater, find_default_seats, parse_seat_position, get_theater_setup

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
        
        # Test valid input
        with patch('builtins.input', return_value="Movie 5 10"):
            title, rows, seats = get_theater_setup()
            self.assertEqual(rows, 5)
            self.assertEqual(seats, 10)
        
        # Test invalid rows (too many)
        with patch('builtins.input', side_effect=["Movie 27 10", "Movie 5 10"]):
            title, rows, seats = get_theater_setup()
            self.assertEqual(rows, 5)  # Should get valid input on second try
        
        # Test invalid seats (too many)
        with patch('builtins.input', side_effect=["Movie 5 51", "Movie 5 10"]):
            title, rows, seats = get_theater_setup()
            self.assertEqual(seats, 10)  # Should get valid input on second try

    def test_ticket_quantity_validation(self):
        """Test validation of ticket quantities"""
        from unittest.mock import patch
        
        # Fill up some seats first (book 10 seats)
        booking_id = self.theater.generate_booking_id()
        seats = find_default_seats(self.theater.seating_map, 10)
        for row, col in seats:
            self.theater.seating_map[row][col] = booking_id
        
        # Now only 40 seats are available
        
        # Test cases with mocked input
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
            with patch('builtins.input', return_value=input_val):
                with patch('builtins.print'):  # Suppress print statements
                    result = book_tickets(self.theater)
                    if expected is None:
                        self.assertIsNone(result)
                    else:
                        # Here we might need to check the actual booking occurred
                        self.assertEqual(self.theater.get_available_seats(), 
                                      40 - expected)  # 40 was available before

if __name__ == '__main__':
    unittest.main() 