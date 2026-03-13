"""Apache Airlines seat booking system for Part A.

This program provides a simple console menu with the core operations
required by the brief:
1. Check availability of a seat
2. Book a seat
3. Free a seat
4. Show booking status
5. Exit the program
"""
from __future__ import annotations


class BookingSystem:
    """Manage the Burak757 seating plan and booking operations."""


    rows = range(1, 81)
    columns = ("A", "B", "C", "D", "E", "F")
    storage_seats = {f"{row}{column}"for row in (77, 78)for column in ("D", "E", "F")}


    def __init__(self):
        self.seats = self._create_seat_map()


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
            print("6. Exit program")

            choice = input("Select an option: ").strip()

            if choice == "1":
                seat_code = self.prompt_for_seat()
                print(self.check_availability(seat_code))
            elif choice == "2":
                seat_code = self.prompt_for_seat()
                print(self.book_seat(seat_code))
            elif choice == "3":
                seat_codes = self.prompt_for_multiple_seats()
                if seat_codes:
                    results = self.book_multiple_seats(seat_codes)
                    for message in results:
                        print(message)
            elif choice == "4":
                seat_code = self.prompt_for_seat()
                print(self.free_seat(seat_code))
            elif choice == "5":
                print(self.show_booking_status())
            elif choice == "6":
                print("Program terminated.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 6.")


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
            self.run_menu()
            return None
        else:
            return seat_code


    def check_availability(self, seat_code):
        """Return a human-readable description of the selected seat state."""
        status = self.seats[seat_code]
        if status == "F":
            return f"Seat {seat_code} is available."
        if status == "R":
            return f"Seat {seat_code} is already booked."
        # status == "S":
        return f"Seat {seat_code} is a storage area and cannot be booked."


    def book_seat(self, seat_code):
        """Book a free seat if it is valid and not restricted."""
        status = self.seats[seat_code]
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be booked."
        if status == "R":
            return f"Seat {seat_code} is already booked."
        # status == "F":
        self.seats[seat_code] = "R"
        return f"Seat {seat_code} has been booked successfully."


    def prompt_for_multiple_seats(self):
        """Read multiple seat codes from the keyboard."""
        try:
            count = int(input("How many seats would you like to book? ").strip())
        except ValueError:
            print("Invalid number.")
            return []
        if count <= 0:
            print("Please enter a number greater than 0.")
            return []

        seat_codes = []
        for i in range(count):
            seat_code = input(f"Enter seat code {i + 1}: ")
            seat_code = self.normalise_seat_code(seat_code)
            if not self.is_valid_seat_code(seat_code):
                print("Invalid seat code. Please enter a seat such as 12A.")
                self.run_menu()
                return None
            else:
                seat_codes.append(seat_code)
        return seat_codes


    def book_multiple_seats(self, seat_codes):
        """Book multiple seats in one operation and return the result messages."""
        results = []
        for seat_code in seat_codes:
            result = self.book_seat(seat_code)
            results.append(result)
        return results


    def free_seat(self, seat_code):
        """Release a booked seat and mark it as free again."""
        status = self.seats[seat_code]
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be freed."
        if status == "F":
            return f"Seat {seat_code} is already free."
        # status == "R":
        self.seats[seat_code] = "F"
        return f"Seat {seat_code} has been released successfully."

    def show_booking_status(self):
        """Build a formatted view of the current cabin seats."""
        lines = []
        lines.append("Legend: F = Free, R = Reserved, S = Storage, | = Aisle")
        lines.append("-" * 25)
        lines.append("       A B C   D E F")

        for row in self.rows:
            left_side = " ".join(self.seats[f"{row}{column}"] for column in ("A", "B", "C"))
            right_side = " ".join(self.seats[f"{row}{column}"] for column in ("D", "E", "F"))
            lines.append(f"Row {row:>2} {left_side} | {right_side}")
        free_count = sum(1 for status in self.seats.values() if status == "F")
        reserved_count = sum(1 for status in self.seats.values() if status == "R")
        storage_count = sum(1 for status in self.seats.values() if status == "S")

        lines.append("-" * 25)
        lines.append(f"Summary: Free = {free_count}, Reserved = {reserved_count}, Storage = {storage_count}")
        return "\n".join(lines)


system = BookingSystem()
if __name__ == "__main__":
    system.run_menu()
