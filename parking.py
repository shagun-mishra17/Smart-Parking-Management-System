from datetime import datetime
from database import get_connection

TOTAL_SLOTS = 10

class Vehicle:
    def __init__(self, number):
        self.number = number

    def get_rate(self):
        return 20

class Car(Vehicle):
    def get_rate(self):
        return 30

class Bike(Vehicle):
    def get_rate(self):
        return 15

class ParkingManager:

    def park_vehicle(self, number, vehicle_type):
        number = number.strip().upper()

        if not number:
            return False, "Vehicle number is required."

        conn = get_connection()

        existing = conn.execute(
            "SELECT id FROM parking_records WHERE vehicle_number=? AND status='Parked'",
            (number,)
        ).fetchone()

        if existing:
            conn.close()
            return False, "This vehicle is already parked."

        occupied = conn.execute(
            "SELECT slot_number FROM parking_records WHERE status='Parked'"
        ).fetchall()

        occupied_slots = [row["slot_number"] for row in occupied]

        available = [
            slot for slot in range(1, TOTAL_SLOTS + 1)
            if slot not in occupied_slots
        ]

        if not available:
            conn.close()
            return False, "Parking is full!"

        vehicle = Car(number) if vehicle_type == "Car" else Bike(number)

        conn.execute("""
            INSERT INTO parking_records
            (vehicle_number, vehicle_type, slot_number, entry_time)
            VALUES (?, ?, ?, ?)
        """, (vehicle.number, vehicle_type, available[0],
              datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return True, f"Vehicle parked successfully in Slot {available[0]}!"

    def remove_vehicle(self, number):
        conn = get_connection()

        record = conn.execute("""
            SELECT * FROM parking_records
            WHERE vehicle_number=? AND status='Parked'
        """, (number.strip().upper(),)).fetchone()

        if not record:
            conn.close()
            return False, "Vehicle not found!"

        vehicle = Car(record["vehicle_number"]) if record["vehicle_type"] == "Car" else Bike(record["vehicle_number"])

        entry = datetime.fromisoformat(record["entry_time"])
        exit_time = datetime.now()

        seconds = (exit_time - entry).total_seconds()
        hours = max(1, int(seconds / 3600) + (1 if seconds % 3600 > 0 else 0))

        amount = hours * vehicle.get_rate()

        conn.execute("""
            UPDATE parking_records
            SET exit_time=?, amount=?, status='Exited'
            WHERE id=?
        """, (exit_time.isoformat(), amount, record["id"]))

        conn.commit()
        conn.close()

        return True, f"Vehicle exited! Parking charge: Rs. {amount}"

    def get_records(self):
        conn = get_connection()
        records = conn.execute(
            "SELECT * FROM parking_records ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return records

    def get_stats(self):
        conn = get_connection()
        occupied = conn.execute(
            "SELECT COUNT(*) FROM parking_records WHERE status='Parked'"
        ).fetchone()[0]
        conn.close()

        return TOTAL_SLOTS, occupied, TOTAL_SLOTS - occupied