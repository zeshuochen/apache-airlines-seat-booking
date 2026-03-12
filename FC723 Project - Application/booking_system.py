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

    def __init__(self) -> None:
        self.seats = self._create_seat_map()

    def _create_seat_map(self) -> dict[str, str]:
        """Create the initial seating plan using F for free and S for storage."""
        seat_map: dict[str, str] = {}
        for row in self.rows:
            for column in self.columns:
                seat_code = f"{row}{column}"
                seat_map[seat_code] = "F" if seat_code not in self.storage_seats else "S"
        return seat_map

    def normalise_seat_code(self, seat_code: str) -> str:
        """Standardise user input before validation."""
        return seat_code.strip().upper()

    def is_valid_seat_code(self, seat_code: str) -> bool:
        """Check whether the supplied seat code exists in the cabin seating plan."""
        return seat_code in self.seats

    def check_availability(self, seat_code: str) -> str:
        """Return a human-readable description of the selected seat state."""   
        if not self.is_valid_seat_code(seat_code):
            return "Invalid seat code. Please enter a seat such as 12A."

        status = self.seats[seat_code]
        if status == "F":
            return f"Seat {seat_code} is available."
        if status == "R":
            return f"Seat {seat_code} is already booked."
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be booked."

    def book_seat(self, seat_code: str) -> str:
        """Book a free seat if it is valid and not restricted."""
        if not self.is_valid_seat_code(seat_code):
            return "Invalid seat code. Please enter a seat such as 12A."

        status = self.seats[seat_code]
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be booked."
        if status == "R":
            return f"Seat {seat_code} is already booked."
        if status == "F":
            self.seats[seat_code] = "R"
            return f"Seat {seat_code} has been booked successfully."

    def free_seat(self, seat_code: str) -> str:
        """Release a booked seat and mark it as free again."""
        if not self.is_valid_seat_code(seat_code):
            return "Invalid seat code. Please enter a seat such as 12A."

        status = self.seats[seat_code]
        if status == "S":
            return f"Seat {seat_code} is a storage area and cannot be freed."
        if status == "F":
            return f"Seat {seat_code} is already free."
        if status == "R":
            self.seats[seat_code] = "F"
            return f"Seat {seat_code} has been released successfully."

    def show_booking_status(self) -> str:
        """Build a formatted view of the current cabin seats."""
        lines = []
        lines.append("Legend: F = Free, R = Reserved, S = Storage, X = Aisle")
        lines.append("-" * 57)

        for row in self.rows:
            left_side = " ".join(self.seats[f"{row}{column}"] for column in ("A", "B", "C"))
            right_side = " ".join(self.seats[f"{row}{column}"] for column in ("D", "E", "F"))
            lines.append(f"Row {row:>2}: {left_side} X X {right_side}")

        free_count = sum(1 for status in self.seats.values() if status == "F")
        reserved_count = sum(1 for status in self.seats.values() if status == "R")
        storage_count = sum(1 for status in self.seats.values() if status == "S")

        lines.append("-" * 57)
        lines.append(
            f"Summary: Free = {free_count}, Reserved = {reserved_count}, Storage = {storage_count}"
        )
        return "\n".join(lines)


def prompt_for_seat(system: BookingSystem) -> str:
    """Read and normalise a seat code from the keyboard."""
    return system.normalise_seat_code(input("Enter seat code: "))


def run_menu() -> None:
    """Display the menu continuously until the user chooses to exit."""
    system = BookingSystem()

    while True:
        print("\nApache Airlines Seat Booking System")
        print("1. Check availability of seat")
        print("2. Book a seat")
        print("3. Free a seat")
        print("4. Show booking status")
        print("5. Exit program")

        choice = input("Select an option: ").strip()

        if choice == "1":
            seat_code = prompt_for_seat(system)
            print(system.check_availability(seat_code))
        elif choice == "2":
            seat_code = prompt_for_seat(system)
            print(system.book_seat(seat_code))
        elif choice == "3":
            seat_code = prompt_for_seat(system)
            print(system.free_seat(seat_code))
        elif choice == "4":
            print(system.show_booking_status())
        elif choice == "5":
            print("Program terminated.")
            break
        else:
            print("Invalid option. Please choose a number from 1 to 5.")


if __name__ == "__main__":
    run_menu()
