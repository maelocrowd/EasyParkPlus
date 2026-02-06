from datetime import datetime, timezone
from collections import deque

class Level:
    def __init__(self, city_name, site_name, level_number, num_regular_slots, num_ev_slots, num_chargers):
        """Initialize a Level with EV and regular slots and chargers."""
        self.city_name = city_name
        self.site_name = site_name
        self.level_number = level_number
        self.ev_slots = [-1] * num_ev_slots
        self.regular_slots = [-1] * num_regular_slots
        self.num_occupied_ev = 0
        self.num_occupied_regular = 0
        self.parked_vehicles = {}

        # Generate ChargerIDs
        city_code = city_name[:3] if len(city_name) >= 3 else city_name
        site_code = site_name[:2] if len(site_name) >= 2 else site_name
        level_code = str(level_number)
        self.charger_ids = [
            f"{city_code}{site_code}{level_code}{str(seq).zfill(3)}"
            for seq in range(1, num_chargers + 1)
        ]
        if self.charger_ids:
            self.ev_slot_chargers = {
                i: self.charger_ids[i % len(self.charger_ids)]
                for i in range(len(self.ev_slots))
            }
        else:
            self.ev_slot_chargers = {}

        self.charger_waiting_queue = {cid: deque() for cid in self.charger_ids}

    def park_vehicle(self, vehicle):
        """Park a vehicle in the appropriate slot and return the assigned slot number."""
        assigned_slot = None

        if vehicle.is_ev():
            for i, slot in enumerate(self.ev_slots):
                if slot == -1:
                    self.ev_slots[i] = vehicle
                    self.num_occupied_ev += 1
                    assigned_slot = i + 1
                    break
            if assigned_slot is None:
                raise ValueError("No EV slots available")
        else:
            for i, slot in enumerate(self.regular_slots):
                if slot == -1:
                    self.regular_slots[i] = vehicle
                    self.num_occupied_regular += 1
                    assigned_slot = i + 1
                    break
            if assigned_slot is None:
                raise ValueError("No regular slots available")

        # --- FIX: use tuple key with slot number and is_ev for uniqueness ---
        key = (assigned_slot, vehicle.is_ev())
        self.parked_vehicles[key] = {
            "vehicle": vehicle,
            "start_time": datetime.now(timezone.utc),
            "slot_number": assigned_slot
        }

        return assigned_slot

    def remove_vehicle(self, slot_number, is_ev=False):
        """Remove a vehicle from a slot and return removal info including timestamps."""
        idx = slot_number - 1

        # Determine if vehicle is EV if not provided
        if is_ev is None:
            if idx < len(self.ev_slots) and self.ev_slots[idx] != -1:
                is_ev = True
            elif idx < len(self.regular_slots) and self.regular_slots[idx] != -1:
                is_ev = False
            else:
                raise ValueError("Slot empty or invalid")

        # Select the vehicle from the appropriate slot
        if is_ev:
            if 0 <= idx < len(self.ev_slots) and self.ev_slots[idx] != -1:
                vehicle = self.ev_slots[idx]
            else:
                raise ValueError("Invalid EV slot number or empty")
        else:
            if 0 <= idx < len(self.regular_slots) and self.regular_slots[idx] != -1:
                vehicle = self.regular_slots[idx]
            else:
                raise ValueError("Invalid regular slot number or empty")

        # --- lookup using the tuple key ---
        key = (slot_number, is_ev)
        record = self.parked_vehicles.get(key)
        if not record:
            raise ValueError("Vehicle record not found")

        start_time = record["start_time"]
        end_time = datetime.now(timezone.utc)

        # Free the slot
        if is_ev:
            self.ev_slots[idx] = -1
            self.num_occupied_ev = max(0, self.num_occupied_ev - 1)
        else:
            self.regular_slots[idx] = -1
            self.num_occupied_regular = max(0, self.num_occupied_regular - 1)

        # Remove the record
        del self.parked_vehicles[key]

        return {
            "vehicle": vehicle,
            "start_time": start_time,
            "end_time": end_time,
            "slot_number": slot_number,
            "is_ev": is_ev
        }


class Site:
    def __init__(self, site_name, city_name):
        """Initialize a Site with a name, city, and levels dictionary."""
        self.site_name = site_name
        self.city_name = city_name
        self.levels = {}

    def add_level(self, level_number, num_regular, num_ev, chargers):
        """Add a Level to this Site."""
        if level_number in self.levels:
            return False, f"Level {level_number} already exists in site {self.site_name}"
        self.levels[level_number] = Level(
            city_name=self.city_name,
            site_name=self.site_name,
            level_number=level_number,
            num_regular_slots=num_regular,
            num_ev_slots=num_ev,
            num_chargers=chargers
        )
        return True, f"Level {level_number} added to site {self.site_name}"


class City:
    def __init__(self, city_name):
        """Initialize a City with a name and dictionary of Sites."""
        self.city_name = city_name
        self.sites = {}

    def add_site(self, site_name):
        """Add a Site to this City."""
        if site_name in self.sites:
            return False, f"Site {site_name} already exists in city {self.city_name}"
        self.sites[site_name] = Site(site_name, self.city_name)
        return True, f"Site {site_name} added to city {self.city_name}"

    def get_or_create_site(self, site_name):
        """Return the Site by name, creating it if it does not exist."""
        if site_name not in self.sites:
            self.add_site(site_name)
        return self.sites[site_name]

    def get_all_site_names(self):
        """Return list of site names in this city."""
        return list(self.sites.keys())

    def get_site(self, site_name):
        """Return a Site object by name, or None if not found."""
        return self.sites.get(site_name)
