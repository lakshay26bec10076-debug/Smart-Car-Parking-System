# Smart Car Parking System

A console-based Python application for managing a multi-floor parking lot. It handles vehicle check-in and check-out, automatic slot allocation by vehicle type, time-based fee calculation, and exportable parking history.

> **This is a pure command-line application.** It uses only Python's standard library (`input()`/`print()` for I/O) — there is no GUI, no browser, and no windowing toolkit involved. It runs entirely in a terminal on any OS with Python 3.8+ installed, including headless/CI environments.

## Features

- Multiple parking floors, each with a configurable number of slots
- Slots categorized by vehicle type: Bike, Car, Truck
- Automatic allocation of the nearest available slot on check-in
- Time-based fee calculation (billed per hour, rounded up)
- Real-time availability report by floor and vehicle type
- Export of completed parking sessions to a JSON file

## Requirements

- Python 3.8 or later (no third-party packages required — everything used is from the Python standard library)

Check your Python version:

```bash
python3 --version
```

If you don't have Python installed, download it from [python.org/downloads](https://www.python.org/downloads/).

## Project Structure

```
.
├── smart_parking_system.py   # main application file
└── README.md                 # this file
```

## Setup

1. **Clone the repository**

   ```bash
   git clone <your-repository-url>
   cd <repository-folder>
   ```

2. **(Optional but recommended) Create a virtual environment**

   ```bash
   python3 -m venv venv
   ```

   Activate it:

   - macOS / Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```

3. **Install dependencies**

   This project has no external dependencies — only the Python standard library (`datetime`, `enum`, `json`, `os`) is used, so there is nothing to install via `pip`.

4. **Configuration**

   No environment variables or config files are needed to run the app as-is. If you want to change the default lot layout (number of floors or slots per vehicle type), edit the values passed to `ParkingLot(...)` inside the `main()` function near the bottom of `smart_parking_system.py`:

   ```python
   lot = ParkingLot(
       floors=2,
       slots_per_floor={
           VehicleType.BIKE: 3,
           VehicleType.CAR: 5,
           VehicleType.TRUCK: 2,
       },
   )
   ```

   You can also adjust hourly rates by editing the `RATES_PER_HOUR` dictionary near the top of the file.

## Running the Application

From the project root, with your virtual environment activated (if you created one):

```bash
python3 smart_parking_system.py
```

You'll see an interactive menu:

```
==== Smart Car Parking System ====
1. Check-in vehicle
2. Check-out vehicle
3. Show availability
4. Show all slots
5. Export history
6. Exit
Choose an option:
```

Respond by typing a number (1–6) and pressing Enter — entirely keyboard-driven, no mouse or GUI window required.

You can also drive it non-interactively (e.g. for scripting or CI) by piping input in, one choice per line:

```bash
printf "1\nMH12AB1234\n2\n3\n6\n" | python3 smart_parking_system.py
```

### Using the menu

| Option | What it does |
|--------|---------------|
| 1 | Check in a vehicle — enter a vehicle number and select its type (Bike/Car/Truck). It's assigned the nearest free matching slot. |
| 2 | Check out a vehicle by its vehicle number — calculates the duration parked and the fee owed. |
| 3 | Show a summary of free/total slots, grouped by floor and vehicle type. |
| 4 | Show the status of every individual slot. |
| 5 | Export all completed (checked-out) sessions to `parking_history.json` in the current directory. |
| 6 | Exit the application. |

### Example session

```
Choose an option: 1
Vehicle number: MH12AB1234
Vehicle type: 1) Bike  2) Car  3) Truck
Choose type: 2
✅ Vehicle MH12AB1234 parked at Floor 1, Slot 4. Ticket ID: 1

Choose an option: 2
Vehicle number to check-out: MH12AB1234
🏁 Vehicle MH12AB1234 checked out. Duration: 1h | Fee: ₹20

Choose an option: 5
📄 History exported to parking_history.json
```

## Output Files

- `parking_history.json` — created in the working directory the first time you export history (option 5). Contains an array of completed ticket records (ticket ID, vehicle number/type, slot, entry/exit time, fee).

## Troubleshooting

- **`python3: command not found`** — try `python` instead of `python3`, or confirm Python is installed and on your PATH.
- **No available slot message** — all slots of that vehicle type are currently occupied; check out a vehicle of that type first or increase the slot count in `slots_per_floor`.
- **Nothing happens when exporting history** — history is only exported for vehicles that have been checked out (option 2); currently parked vehicles won't appear until they check out.

## License

Add your preferred license here (e.g., MIT).
