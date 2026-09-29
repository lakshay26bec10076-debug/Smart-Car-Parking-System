# Smart Car Parking System — Project Statement

## 1. Overview

The **Smart Car Parking System** is a command-line application written in Python that manages a multi-floor parking lot. It automates slot allocation, vehicle check-in and check-out, fee calculation, availability reporting, and exporting of parking history. It is built entirely with the Python standard library and follows an object-oriented design.

## 2. Problem Statement

Manual parking management is slow and error-prone. Attendants have to track which slots are free, remember which vehicle is parked where, calculate fees by hand, and keep records of past visits. This leads to wasted time, billing disputes, poor slot utilisation, and no reliable history.

This project addresses these problems by providing a software system that:

- Assigns a suitable slot automatically when a vehicle arrives.
- Prevents invalid operations such as the same vehicle checking in twice.
- Calculates the parking fee automatically at check-out.
- Shows live availability by floor and vehicle type.
- Keeps a record of completed parking sessions that can be exported.

## 3. Objectives

1. Model a parking lot with multiple floors and different slot types (bike, car, truck).
2. Allocate the first available slot matching the vehicle type, favouring lower floors.
3. Issue a ticket at check-in and close it at check-out with exit time and fee.
4. Bill fairly and consistently using per-hour rates by vehicle type.
5. Provide clear reports on slot availability and occupancy.
6. Persist completed sessions to a JSON file for record keeping.
7. Offer a simple, menu-driven CLI for operators.

## 4. Features

| Feature | Description |
|---|---|
| Multi-floor lot | Configurable number of floors and slots per vehicle type per floor |
| Vehicle types | Bike, Car, Truck, each with its own slot type and hourly rate |
| Automatic slot allocation | First free slot of the matching type; lower floors are filled first |
| Duplicate check-in guard | A vehicle that is already parked cannot check in again |
| Ticketing | Each visit gets a unique incrementing ticket ID |
| Automatic billing | Fee computed from parked duration and vehicle rate |
| Availability report | Free/total slots grouped by floor and vehicle type |
| Slot listing | Shows every slot with its status and current occupant |
| History export | Completed tickets exported to `parking_history.json` |

## 5. Pricing Rules

| Vehicle Type | Rate (₹ per hour) |
|---|---|
| Bike | 10 |
| Car | 20 |
| Truck | 30 |

- Duration is **rounded up** to the next full hour (for example, 61 minutes is billed as 2 hours).
- A **minimum of 1 hour** is always charged.
- Fee = billed hours × hourly rate for the vehicle type.

## 6. System Design

The system is split into four main components plus a CLI.

### 6.1 `VehicleType` (Enum)
Defines the supported vehicle categories: `BIKE`, `CAR`, `TRUCK`. Used both for slot types and for looking up rates in `RATES_PER_HOUR`.

### 6.2 `Slot`
Represents one parking spot.
- Attributes: `slot_id`, `floor`, `slot_type`, `is_free`, `vehicle_number`, `entry_time`
- Methods: `occupy()`, `vacate()`, and a readable `__str__` representation

### 6.3 `Ticket`
Represents one parking session.
- Created at check-in with ticket ID, vehicle details, assigned slot, and entry time
- Closed at check-out with exit time and fee via `close()`
- `to_dict()` flattens the ticket into a JSON-friendly format (slot shown as `F<floor>-S<slot_id>`)

### 6.4 `ParkingLot`
The core controller that owns all slots and tracks sessions.
- Builds all slots up front, floor by floor
- `active_tickets`: dictionary of currently parked vehicles (vehicle number → ticket)
- `ticket_history`: list of completed tickets
- Key methods: `find_available_slot()`, `check_in()`, `check_out()`, `_hours_between()`, `display_availability()`, `display_all_slots()`, `export_history()`

### 6.5 CLI (`main()`)
A menu-driven loop that lets an operator check vehicles in and out, view availability and slots, export history, and exit. The demo lot has 2 floors, each with 3 bike, 5 car, and 2 truck slots (20 slots in total).

## 7. Workflow

**Check-in**
1. Operator enters the vehicle number and type.
2. System rejects the request if the vehicle is already parked.
3. System finds the first free slot of the matching type; if none is free, the request is declined.
4. The slot is marked occupied, a ticket is created, and the slot location and ticket ID are shown.

**Check-out**
1. Operator enters the vehicle number.
2. System looks up the active ticket; if none exists, it reports an error.
3. Duration is calculated and rounded up, and the fee is computed.
4. The ticket is closed, the slot is freed, and the ticket moves to history.

**Export**
Completed tickets are written to `parking_history.json` as a list of records.

## 8. Sample Exported Record

```json
{
  "ticket_id": 1,
  "vehicle_number": "MP09AB1234",
  "vehicle_type": "car",
  "slot": "F1-S4",
  "entry_time": "2026-09-30 10:15:00",
  "exit_time": "2026-09-30 12:40:00",
  "fee": 60
}
```

## 9. Technology Stack

- **Language:** Python 3
- **Libraries:** standard library only (`datetime`, `enum`, `json`, `os`)
- **Interface:** command-line (terminal)
- **Storage:** in-memory during runtime; JSON file for exported history

## 10. How to Run

```bash
python smart_parking_system.py
```

Then choose from the menu:

```
1. Check-in vehicle
2. Check-out vehicle
3. Show availability
4. Show all slots
5. Export history
6. Exit
```

## 11. Limitations

- All state is held in memory, so active parkings and history are lost when the program exits unless history is exported. Active tickets are not saved.
- There is no input validation on vehicle number format.
- Only hourly billing is supported, with no daily caps, grace periods, or discounts.
- Single-operator CLI only, with no concurrency handling or user authentication.
- The `os` module is imported but not currently used.

## 12. Future Scope

- Persist the full lot state (slots and active tickets) to a database or file.
- Add a web or GUI front end, and possibly a REST API.
- Support reservations, monthly passes, and EV or handicapped slots.
- Add flexible pricing such as daily caps, peak-hour rates, and grace periods.
- Add vehicle number validation and license plate recognition.
- Provide analytics such as occupancy trends and revenue reports.
- Add automated unit tests for billing and allocation logic.

## 13. Conclusion

The Smart Car Parking System demonstrates a clean, object-oriented solution to a common real-world problem. It covers the full parking lifecycle (allocation, ticketing, billing, reporting, and record keeping) in a compact and readable codebase, and it provides a solid foundation for extension into a production-grade system.
