"""Apache Airlines seat booking system for Part A.

This program provides a simple console menu with the core operations
required by the brief:
1. Check availability of a seat
2. Book a seat
3. Book multiple seats
4. Free a seat
5. Show booking status
6. Find booking by reference
7. Export seat map as an image
8. Exit the program
"""

import os
import random
import sqlite3
import string
from xml.sax.saxutils import escape


class BookingSystem:
    """Manage the Burak757 seating plan and booking operations."""

    def __init__(self, rows, columns, storage_seats):
        self.rows = tuple(rows)
        self.columns = tuple(columns)
        self.storage_seats = storage_seats
        self.seats = self._create_seat_map()
        db_path = os.path.join(os.path.dirname(__file__), "apache_airlines.db")
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.create_booking_table()

    def create_booking_table(self):
        """Create the bookings table if it does not already exist."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_reference TEXT PRIMARY KEY,
                passport_number TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                seat_row INTEGER NOT NULL,
                seat_column TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def _create_seat_map(self):
        """Create the initial seating plan using F for free and S for storage."""
        seat_map = {}
        for row in self.rows:
            for column in self.columns:
                seat_code = f"{row}{column}"
                seat_map[seat_code] = "F" if seat_code not in self.storage_seats else "S"
        return seat_map

    def run_menu(self):
        """Display the menu continuously until the user chooses to exit."""
        while True:
            print("\nApache Airlines Seat Booking System")
            print("1. Check availability of seat")
            print("2. Book a seat")
            print("3. Book multiple seats")
            print("4. Free a seat")
            print("5. Show booking status")
            print("6. Find booking by reference")
            print("7. Export seat map as an image")
            print("8. Exit program")

            choice = input("Select an option: ").strip(".")

            if choice == "1":
                seat_code = self.prompt_for_seat()
                if seat_code:
                    print(self.check_availability(seat_code))
            elif choice == "2":
                seat_code = self.prompt_for_seat()
                if seat_code:
                    print(self.book_seat(seat_code))
            elif choice == "3":
                seat_codes = self.prompt_for_multiple_seats()
                if seat_codes:
                    for message in self.book_multiple_seats(seat_codes):
                        print(message)
            elif choice == "4":
                seat_code = self.prompt_for_seat()
                if seat_code:
                    print(self.free_seat(seat_code))
            elif choice == "5":
                print(self.show_booking_status())
            elif choice == "6":
                booking_reference = input("Enter booking reference: ").strip().upper()
                print(self.find_booking_by_reference(booking_reference))
            elif choice == "7":
                output_path = self.export_seat_map_image()
                print(f"Seat map image exported successfully: {output_path}")
            elif choice == "8":
                print("Program terminated.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 8.")

    def check_availability(self, seat_code):
        """Return a human-readable description of the selected seat state."""
        status = self.seats[seat_code]
        if status == "F":
            return f"Seat {seat_code} is available."
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be booked."
        return f"Seat {seat_code} is already booked. Booking reference: {status}"

    def book_seat(self, seat_code):
        """Book a seat, generate a booking reference, and save passenger data."""
        status = self.seats[seat_code]
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be booked."
        if status != "F":
            return f"Seat {seat_code} is already booked."

        passport_number = input("Enter passport number: ").strip()
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()

        booking_reference = self.generate_booking_reference()
        self.seats[seat_code] = booking_reference
        self.save_booking_to_database(
            booking_reference, passport_number, first_name, last_name, seat_code
        )

        return (
            f"Seat {seat_code} has been booked successfully. "
            f"Booking reference: {booking_reference}"
        )

    def book_multiple_seats(self, seat_codes):
        """Book multiple seats in one operation and return the result messages."""
        results = []
        for seat_code in seat_codes:
            results.append(self.book_seat(seat_code))
        return results

    def free_seat(self, seat_code):
        """Release a booked seat and mark it as free again."""
        status = self.seats[seat_code]
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be freed."
        if status == "F":
            return f"Seat {seat_code} is already free."

        booking_reference = status
        self.cursor.execute(
            "DELETE FROM bookings WHERE booking_reference = ?",
            (booking_reference,),
        )
        self.connection.commit()

        self.seats[seat_code] = "F"
        return f"Seat {seat_code} has been released successfully."

    def show_booking_status(self):
        """Build a formatted view of the current cabin seats."""
        lines = []
        lines.append("Legend: F = Free, B = Booked, S = Storage, | = Aisle")
        lines.append("-" * 25)
        lines.append("       A B C   D E F")

        for row in self.rows:
            left_side = " ".join(
                self.get_display_status(f"{row}{column}") for column in ("A", "B", "C")
            )
            right_side = " ".join(
                self.get_display_status(f"{row}{column}") for column in ("D", "E", "F")
            )
            lines.append(f"Row {row:>2} {left_side} | {right_side}")

        free_count = sum(1 for status in self.seats.values() if status == "F")
        reserved_count = sum(
            1 for status in self.seats.values() if status not in ("F", "S")
        )
        storage_count = sum(1 for status in self.seats.values() if status == "S")

        lines.append("-" * 25)
        lines.append(
            f"Summary: Free = {free_count}, Reserved = {reserved_count}, Storage = {storage_count}"
        )
        return "\n".join(lines)

    def find_booking_by_reference(self, booking_reference):
        """Find a booking using its booking reference."""
        self.cursor.execute(
            """
            SELECT booking_reference, passport_number, first_name, last_name, seat_row, seat_column
            FROM bookings
            WHERE booking_reference = ?
            """,
            (booking_reference,),
        )

        booking = self.cursor.fetchone()
        if booking is None:
            return "No booking found for that reference."

        reference, passport_number, first_name, last_name, seat_row, seat_column = booking
        return (
            f"Booking reference: {reference}\n"
            f"Passenger name: {first_name} {last_name}\n"
            f"Passport number: {passport_number}\n"
            f"Seat number: {seat_row}{seat_column}"
        )

    @staticmethod
    def normalise_seat_code(seat_code):
        """Standardise user input before validation."""
        return seat_code.strip().upper()

    def is_valid_seat_code(self, seat_code):
        """Check whether the supplied seat code exists in the cabin seating plan."""
        return seat_code in self.seats

    def prompt_for_seat(self):
        """Read and normalise a seat code from the keyboard."""
        seat_code = input("Please enter a seat code: ")
        seat_code = self.normalise_seat_code(seat_code)
        if not self.is_valid_seat_code(seat_code):
            print("Invalid seat code. Please enter a seat such as 12A.")
            return None
        return seat_code

    def prompt_for_multiple_seats(self):
        """Read multiple seat codes from the keyboard."""
        try:
            count = int(input("How many seats would you like to book? ").strip("."))
        except ValueError:
            print("Invalid number.")
            return []

        if count <= 0:
            print("Please enter a number greater than 0.")
            return []

        seat_codes = []
        for index in range(count):
            seat_code = input(f"Enter seat code {index + 1}: ")
            seat_code = self.normalise_seat_code(seat_code)
            if not self.is_valid_seat_code(seat_code):
                print("Invalid seat code. Please enter a seat such as 12A.")
                return []
            seat_codes.append(seat_code)
        return seat_codes

    def generate_booking_reference(self):
        """Generate a unique 8-character alphanumeric booking reference."""
        characters = string.ascii_uppercase + string.digits

        while True:
            reference = "".join(random.choices(characters, k=8))
            self.cursor.execute(
                "SELECT booking_reference FROM bookings WHERE booking_reference = ?",
                (reference,),
            )
            if self.cursor.fetchone() is None:
                return reference

    def save_booking_to_database(
        self, booking_reference, passport_number, first_name, last_name, seat_code
    ):
        """Save booking details to the database."""
        seat_row = int(seat_code[:-1])
        seat_column = seat_code[-1]

        self.cursor.execute(
            """
            INSERT INTO bookings (
                booking_reference,
                passport_number,
                first_name,
                last_name,
                seat_row,
                seat_column
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                booking_reference,
                passport_number,
                first_name,
                last_name,
                seat_row,
                seat_column,
            ),
        )
        self.connection.commit()

    def export_seat_map_image(self, output_path=None):
        """Export the current cabin layout as an SVG image file."""
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), "seat_map.svg")

        seat_width = 54
        seat_height = 34
        horizontal_gap = 10
        aisle_gap = 36
        left_margin = 90
        top_margin = 70
        row_gap = 10
        right_margin = 40
        bottom_margin = 60

        total_seat_width = (seat_width * len(self.columns)) + (horizontal_gap * 4) + aisle_gap
        canvas_width = left_margin + total_seat_width + right_margin
        canvas_height = top_margin + (len(self.rows) * (seat_height + row_gap)) + bottom_margin

        seat_colors = {"F": "#D9F99D", "B": "#FCA5A5", "S": "#CBD5E1"}
        seat_labels = {"F": "Free", "B": "Booked", "S": "Storage"}
        x_positions = {}

        x = left_margin
        for index, column in enumerate(self.columns):
            x_positions[column] = x
            x += seat_width + horizontal_gap
            if index == 2:
                x += aisle_gap - horizontal_gap

        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">',
            '<rect width="100%" height="100%" fill="#F8FAFC"/>',
            '<text x="50%" y="38" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#0F172A">Apache Airlines Seat Map</text>',
            '<text x="50%" y="58" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#475569">Green = Free, Red = Booked, Grey = Storage</text>',
        ]

        legend_y = canvas_height - 28
        legend_x = left_margin
        for code in ("F", "B", "S"):
            svg_lines.append(
                f'<rect x="{legend_x}" y="{legend_y - 12}" width="18" height="18" rx="4" fill="{seat_colors[code]}" stroke="#334155"/>'
            )
            svg_lines.append(
                f'<text x="{legend_x + 26}" y="{legend_y + 2}" font-family="Arial, sans-serif" font-size="13" fill="#0F172A">{seat_labels[code]}</text>'
            )
            legend_x += 110

        aisle_x = x_positions["C"] + seat_width + (aisle_gap - horizontal_gap) / 2
        svg_lines.append(
            f'<text x="{aisle_x}" y="{top_margin - 14}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#64748B">Aisle</text>'
        )

        for column, column_x in x_positions.items():
            svg_lines.append(
                f'<text x="{column_x + seat_width / 2}" y="{top_margin - 14}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1E293B">{column}</text>'
            )

        for row_index, row in enumerate(self.rows):
            y = top_margin + row_index * (seat_height + row_gap)
            svg_lines.append(
                f'<text x="{left_margin - 18}" y="{y + 22}" text-anchor="end" font-family="Arial, sans-serif" font-size="14" fill="#1E293B">Row {row}</text>'
            )

            for column in self.columns:
                seat_code = f"{row}{column}"
                status = self.get_display_status(seat_code)
                display_text = seat_code if status != "B" else escape(str(self.seats[seat_code]))

                svg_lines.append(
                    f'<rect x="{x_positions[column]}" y="{y}" width="{seat_width}" height="{seat_height}" rx="8" fill="{seat_colors[status]}" stroke="#334155" stroke-width="1.2"/>'
                )
                svg_lines.append(
                    f'<text x="{x_positions[column] + seat_width / 2}" y="{y + 21}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#0F172A">{display_text}</text>'
                )

        svg_lines.append("</svg>")

        with open(output_path, "w", encoding="utf-8") as svg_file:
            svg_file.write("\n".join(svg_lines))

        return output_path

    def get_display_status(self, seat_code):
        """Convert internal seat value into a short display symbol."""
        status = self.seats[seat_code]
        if status == "F":
            return "F"
        if status == "S":
            return "S"
        return "B"
