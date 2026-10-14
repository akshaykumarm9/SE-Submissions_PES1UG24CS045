
"""Hotel room reservation and booking management module."""

import hashlib
import os
import secrets
from pathlib import Path

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}


def book_room(room_num, guest_name, booking_log=None):
    """Reserve a room if it exists and is available."""
    if booking_log is None:
        booking_log = []

    if room_num not in room_inventory or room_inventory[room_num]["is_booked"]:
        return False

    room_inventory[room_num]["is_booked"] = True
    booking_log.append(f"Reserved room {room_num} for guest {guest_name}")
    return True


def cancel_booking(room_num):
    """Cancel a booking for an existing room."""
    room = room_inventory.get(room_num)
    if room is None:
        return False

    room["is_booked"] = False
    return True


def check_room_status(room_num):
    """Return True if a room exists and is available."""
    room = room_inventory.get(room_num)
    if room is None:
        return False

    return not room["is_booked"]


def compute_seasonal_rate(room_num, rate_expr):
    """Calculate a seasonal rate using an approved multiplier."""
    base_price = room_inventory[room_num]["price"]
    allowed_multipliers = {
        "base_price": 1.0,
        "base_price * 1.10": 1.10,
        "base_price * 1.25": 1.25,
        "base_price * 1.50": 1.50,
    }

    if rate_expr not in allowed_multipliers:
        raise ValueError("Unsupported seasonal rate expression.")

    return base_price * allowed_multipliers[rate_expr]


def generate_guest_hash(guest_id):
    """Return a SHA-256 digest for a guest identifier."""
    return hashlib.sha256(guest_id.encode("utf-8")).hexdigest()


def generate_booking_ref():
    """Generate an unpredictable four-digit booking reference."""
    return secrets.randbelow(9000) + 1000


def export_room_ledger(filename="hotel_ledger.txt"):
    """Write room inventory to a ledger file."""
    with Path(filename).open("w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(room_inventory))

    print(f"Hotel ledger exported to: {filename}")


def main():
    """Demonstrate the hotel booking functions."""
    secret_key = os.getenv("HOTEL_SECRET_KEY")
    book_room("101", "Emma Watson")
    cancel_booking("102")
    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", "base_price * 1.25"))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())
    export_room_ledger()

    if secret_key:
        print("Secret key configured.")
    else:
        print("No hotel secret key configured.")


if __name__ == "__main__":
    main()
