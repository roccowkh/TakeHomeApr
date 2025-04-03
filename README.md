# Theater Booking System

A command-line theater ticket booking system that allows users to book movie tickets and manage seat allocations.

## Features

- Theater setup with configurable rows (A-Z) and seats per row (1-50)
- Smart seat allocation prioritizing center seats and consecutive seating
- Booking management with unique booking IDs
- Visual seating map display
- Booking status check functionality

## Requirements

- Python 3.13.2 or higher
- macOS 15.4 or higher (may work on other platforms)

- ## Usage

Run the program: python3 theater_booking.py
Run the unit test: python3 -m test_theater_booking

## Assumption
- When overflowing to the next row, start from middle
- When filling the current row, if there's space ont the left, fill them after the spaces on the right are occupied
- columns indicator  with 2 digits will affect the layout, modified to use two lines to display for better looking
- I made up all the error messages
- There's no need to save the record after the program exit
- Booking Id always starts with  HKG and 4 digits, there's no need to handle the case of 10000 orders as there will never be 10000 seats
- middle of 50 is 25 not 24
