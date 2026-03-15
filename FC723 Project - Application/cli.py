from booking_system import BookingSystem

rows = range(1, 81)
columns = ("A", "B", "C", "D", "E", "F")
storage_seats = {f"{row}{column}"for row in (77, 78)for column in ("D", "E", "F")}
system = BookingSystem(rows, columns, storage_seats)
if __name__ == "__main__":
    system.run_menu()
