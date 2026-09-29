from datetime import datetime
from enum import Enum
import json


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


# fee per hour for each vehicle type
RATES_PER_HOUR = {
    VehicleType.BIKE: 10,
    VehicleType.CAR: 20,
    VehicleType.TRUCK: 30,
}


class Slot:
    def __init__(self, slot_id, floor, slot_type):
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
        # reset everything so the slot can be reused
        self.is_free = True
        self.vehicle_number = None
        self.entry_time = None

    def __str__(self):
        if self.is_free:
            status = "FREE"
        else:
            status = "OCCUPIED by " + self.vehicle_number
        return f"[Floor {self.floor} | Slot {self.slot_id} | {self.slot_type.value.upper()}] {status}"


class Ticket:
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
        # convert to plain values so json can handle it
        fmt = "%Y-%m-%d %H:%M:%S"
        exit_str = None
        if self.exit_time:
            exit_str = self.exit_time.strftime(fmt)

        return {
            "ticket_id": self.ticket_id,
            "vehicle_number": self.vehicle_number,
            "vehicle_type": self.vehicle_type.value,
            "slot": f"F{self.slot.floor}-S{self.slot.slot_id}",
            "entry_time": self.entry_time.strftime(fmt),
            "exit_time": exit_str,
            "fee": self.fee,
        }


class ParkingLot:
    def __init__(self, floors, slots_per_floor):
        self.slots = []
        slot_id = 1

        # slots are created floor by floor, so lower floors come first in the list
        for floor in range(1, floors + 1):
            for vtype, count in slots_per_floor.items():
                for pos in range(count):
                    self.slots.append(Slot(slot_id, floor, vtype))
                    slot_id += 1

        self.active_tickets = {}   # vehicle number -> ticket, for parked vehicles
        self.ticket_history = []   # tickets of vehicles that already left
        self._ticket_counter = 1

    def find_available_slot(self, vehicle_type):
        # first free slot of the right type = nearest, because of the order above
        for s in self.slots:
            if s.is_free and s.slot_type == vehicle_type:
                return s
        return None

    def check_in(self, vehicle_number, vehicle_type):
        if vehicle_number in self.active_tickets:
            print("Wait, vehicle", vehicle_number, "is already parked here somewhere??")
            return None

        slot = self.find_available_slot(vehicle_type)
        if slot is None:
            print("Ah, sorry! No available slots left for", vehicle_type.value)
            return None

        now = datetime.now()
        slot.occupy(vehicle_number, now)

        ticket = Ticket(self._ticket_counter, vehicle_number, vehicle_type, slot, now)
        self.active_tickets[vehicle_number] = ticket
        self._ticket_counter += 1

        print(f"Success! Vehicle {vehicle_number} parked at Floor {slot.floor}, Slot {slot.slot_id}. Ticket ID: {ticket.ticket_id}")
        return ticket

    def check_out(self, vehicle_number):
        ticket = self.active_tickets.get(vehicle_number)
        if not ticket:
            print("Hmm, couldn't find an active ticket for vehicle:", vehicle_number)
            return None

        exit_time = datetime.now()
        hours = self._hours_between(ticket.entry_time, exit_time)

        # minimum charge is 1 hour
        hours = max(1, hours)
        fee = hours * RATES_PER_HOUR[ticket.vehicle_type]

        ticket.close(exit_time, fee)
        ticket.slot.vacate()

        # move the ticket from active to history
        del self.active_tickets[vehicle_number]
        self.ticket_history.append(ticket)

        print(f"Vehicle {vehicle_number} checked out. Total time: {hours} hours. Fee is: Rs {fee}")
        return ticket

    @staticmethod
    def _hours_between(t1, t2):
        seconds = (t2 - t1).total_seconds()
        hours = int(seconds // 3600)
        # any leftover minutes count as one more hour
        if seconds % 3600 > 0:
            hours += 1
        return hours

    def display_availability(self):
        print("\n--- Parking Availability Status ---")
        summary = {}
        for slot in self.slots:
            key = (slot.floor, slot.slot_type)
            if key not in summary:
                summary[key] = [0, 0]   # [free, total]
            summary[key][1] += 1
            if slot.is_free:
                summary[key][0] += 1

        for key in sorted(summary, key=lambda x: x[0]):
            free, total = summary[key]
            floor_num, vtype = key
            print(f"Floor {floor_num} | {vtype.value.upper():6s} | Free: {free}/{total}")
        print("-----------------------------------")

    def display_all_slots(self):
        for slot in self.slots:
            print(slot)

    def export_history(self, filepath="parking_history.json"):
        data = []
        for t in self.ticket_history:
            data.append(t.to_dict())

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print("Exported history to file:", filepath)


def main():
    # small lot: 2 floors, each with 3 bike, 5 car and 2 truck slots
    lot = ParkingLot(2, {
        VehicleType.BIKE: 3,
        VehicleType.CAR: 5,
        VehicleType.TRUCK: 2,
    })

    type_mapping = {
        "1": VehicleType.BIKE,
        "2": VehicleType.CAR,
        "3": VehicleType.TRUCK
    }

    while True:
        print("\n===============================")
        print("   SMART PARKING SYSTEM MENU   ")
        print("===============================")
        print("1. Check-in vehicle")
        print("2. Check-out vehicle")
        print("3. Show availability summary")
        print("4. Show all slots status")
        print("5. Export history to JSON")
        print("6. Exit program")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            number = input("Enter vehicle number plate: ").strip().upper()
            print("Select Vehicle Type:")
            print("1) Bike")
            print("2) Car")
            print("3) Truck")
            t_input = input("Choice: ").strip()
            vtype = type_mapping.get(t_input)

            if vtype:
                lot.check_in(number, vtype)
            else:
                print("Oops, invalid vehicle type selected.")

        elif choice == "2":
            number = input("Enter vehicle number plate to check-out: ").strip().upper()
            lot.check_out(number)

        elif choice == "3":
            lot.display_availability()

        elif choice == "4":
            lot.display_all_slots()

        elif choice == "5":
            lot.export_history()

        elif choice == "6":
            print("Exiting... Have a nice day!")
            break
        else:
            print("That's not a valid option, try again buddy.")


if __name__ == "__main__":
    main()
