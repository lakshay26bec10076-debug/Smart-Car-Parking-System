from datetime import datetime
from enum import Enum
import json
import os


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


# what we charge per hour, by vehicle type
RATES_PER_HOUR = {
    VehicleType.BIKE: 10,
    VehicleType.CAR: 20,
    VehicleType.TRUCK: 30,
}


class Slot:
    """One parking spot. Belongs to a floor and only fits one type of vehicle."""

    def __init__(self, slot_id, floor, slot_type: VehicleType):
        self.slot_id = slot_id
        self.floor = floor
        self.slot_type = slot_type
        self.is_free = True
        self.vehicle_number = None
        self.entry_time = None

    def occupy(self, vehicle_number, entry_time):
        self.is_free = False
        self.vehicle_number = vehicle_number
        self.entry_time = entry_time

    def vacate(self):
        self.is_free = True
        self.vehicle_number = None
        self.entry_time = None

    def __str__(self):
        status = "FREE" if self.is_free else f"OCCUPIED by {self.vehicle_number}"
        return f"[Floor {self.floor} | Slot {self.slot_id} | {self.slot_type.value.upper()}] {status}"


class Ticket:
    """A parking session - created at check-in, filled in at check-out."""

    def __init__(self, ticket_id, vehicle_number, vehicle_type, slot, entry_time):
        self.ticket_id = ticket_id
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type
        self.slot = slot
        self.entry_time = entry_time
        self.exit_time = None
        self.fee = None

    def close(self, exit_time, fee):
        self.exit_time = exit_time
        self.fee = fee

    def to_dict(self):
        # flatten everything down so it can be dumped to JSON
        return {
            "ticket_id": self.ticket_id,
            "vehicle_number": self.vehicle_number,
            "vehicle_type": self.vehicle_type.value,
            "slot": f"F{self.slot.floor}-S{self.slot.slot_id}",
            "entry_time": self.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "exit_time": self.exit_time.strftime("%Y-%m-%d %H:%M:%S") if self.exit_time else None,
            "fee": self.fee,
        }


class ParkingLot:
    """Owns all the slots and keeps track of who's parked where."""

    def __init__(self, floors, slots_per_floor):
        """
        floors: how many floors the lot has
        slots_per_floor: e.g. {VehicleType.BIKE: 5, VehicleType.CAR: 10, VehicleType.TRUCK: 3}
        """
        # build out every slot up front - floor 1's slots first, then floor 2's, etc.
        self.slots = []
        slot_counter = 1
        for floor in range(1, floors + 1):
            for vtype, count in slots_per_floor.items():
                for _ in range(count):
                    self.slots.append(Slot(slot_counter, floor, vtype))
                    slot_counter += 1

        self.active_tickets = {}   # vehicle_number -> Ticket, for whoever's currently parked
        self.ticket_history = []   # everything that's been checked out so far
        self._ticket_counter = 1

    # ---------- check-in / check-out ----------

    def find_available_slot(self, vehicle_type: VehicleType):
        # just grabs the first free slot of the right type - since slots are
        # stored floor by floor, this naturally favors lower floors
        for slot in self.slots:
            if slot.is_free and slot.slot_type == vehicle_type:
                return slot
        return None

    def check_in(self, vehicle_number, vehicle_type: VehicleType):
        # don't let the same vehicle check in twice
        if vehicle_number in self.active_tickets:
            print(f"⚠️  Vehicle {vehicle_number} is already parked.")
            return None

        slot = self.find_available_slot(vehicle_type)
        if not slot:
            print(f"🚫 No available slot for {vehicle_type.value}.")
            return None

        # claim the slot and open a ticket for this visit
        entry_time = datetime.now()
        slot.occupy(vehicle_number, entry_time)

        ticket = Ticket(self._ticket_counter, vehicle_number, vehicle_type, slot, entry_time)
        self.active_tickets[vehicle_number] = ticket
        self._ticket_counter += 1

        print(f"✅ Vehicle {vehicle_number} parked at Floor {slot.floor}, Slot {slot.slot_id}. "
              f"Ticket ID: {ticket.ticket_id}")
        return ticket

    def check_out(self, vehicle_number):
        ticket = self.active_tickets.get(vehicle_number)
        if not ticket:
            print(f"⚠️  No active ticket found for vehicle {vehicle_number}.")
            return None

        # work out how long they were here and what they owe
        exit_time = datetime.now()
        duration_hours = max(1, self._hours_between(ticket.entry_time, exit_time))
        fee = duration_hours * RATES_PER_HOUR[ticket.vehicle_type]

        ticket.close(exit_time, fee)
        ticket.slot.vacate()

        # not active anymore, just history now
        del self.active_tickets[vehicle_number]
        self.ticket_history.append(ticket)

        print(f"🏁 Vehicle {vehicle_number} checked out. "
              f"Duration: {duration_hours}h | Fee: ₹{fee}")
        return ticket

    @staticmethod
    def _hours_between(t1, t2):
        # always round up - 61 minutes still counts as 2 hours for billing
        seconds = (t2 - t1).total_seconds()
        return int(seconds // 3600) + (1 if seconds % 3600 > 0 else 0)

    # ---------- reports ----------

    def display_availability(self):
        # tally up free vs. total slots, grouped by floor + vehicle type
        print("\n--- Parking Availability ---")
        summary = {}
        for slot in self.slots:
            key = (slot.floor, slot.slot_type)
            summary.setdefault(key, [0, 0])   # [free, total]
            summary[key][1] += 1
            if slot.is_free:
                summary[key][0] += 1

        for (floor, vtype), (free, total) in sorted(summary.items(), key=lambda item: (item[0][0], item[0][1].value)):
            print(f"Floor {floor} | {vtype.value.upper():6s} | Free: {free}/{total}")
        print("-----------------------------\n")

    def display_all_slots(self):
        for slot in self.slots:
            print(slot)

    def export_history(self, filepath="parking_history.json"):
        data = [t.to_dict() for t in self.ticket_history]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"📄 History exported to {filepath}")


# ---------------------------------------------------------------------
# CLI Demo
# ---------------------------------------------------------------------

def main():
    # a small 2-floor lot to play around with
    lot = ParkingLot(
        floors=2,
        slots_per_floor={
            VehicleType.BIKE: 3,
            VehicleType.CAR: 5,
            VehicleType.TRUCK: 2,
        },
    )

    menu = """
==== Smart Car Parking System ====
1. Check-in vehicle
2. Check-out vehicle
3. Show availability
4. Show all slots
5. Export history
6. Exit
Choose an option: """

    while True:
        choice = input(menu).strip()

        if choice == "1":
            number = input("Vehicle number: ").strip().upper()
            print("Vehicle type: 1) Bike  2) Car  3) Truck")
            t = input("Choose type: ").strip()
            vtype_map = {"1": VehicleType.BIKE, "2": VehicleType.CAR, "3": VehicleType.TRUCK}
            vtype = vtype_map.get(t)
            if vtype:
                lot.check_in(number, vtype)
            else:
                print("Invalid vehicle type.")

        elif choice == "2":
            number = input("Vehicle number to check-out: ").strip().upper()
            lot.check_out(number)

        elif choice == "3":
            lot.display_availability()

        elif choice == "4":
            lot.display_all_slots()

        elif choice == "5":
            lot.export_history()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
