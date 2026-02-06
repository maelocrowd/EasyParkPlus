from ParkingUI import ParkingLotUI
import tkinter as tk
from datetime import datetime, timezone, timedelta
from ParkingApplicationService import ParkingApplicationService
from ParkingEntities import City

# ---------------- Main ParkingLot class ----------------
class ParkingLot:
    """Aggregate root representing the parking lot containing multiple cities."""

    def __init__(self):
        """Initialize an empty parking lot with no cities."""
        self.cities = {}  # key: city_name -> City object

    def get_or_create_city(self, city_name):
        """
        Retrieve an existing city or create a new one if not present.

        Args:
            city_name (str): Name of the city.

        Returns:
            City: City object corresponding to the name.
        """
        if city_name not in self.cities:
            self.cities[city_name] = City(city_name)
        return self.cities[city_name]

    def _find_level_by_charger(self, charger_id):
        """
        Find the Level entity that contains the specified charger.

        Args:
            charger_id (str): Charger identifier.

        Returns:
            Level or None: Level object containing the charger, or None if not found.
        """
        for city in self.cities.values():
            for site in city.sites.values():
                for level in site.levels.values():
                    if charger_id in level.charger_ids:
                        return level
        return None

    def get_level(self, city_name: str, site_name: str, level_number: int):
        """
        Returns the Level entity for the given city, site, and level number.

        Args:
            city_name (str): Name of the city.
            site_name (str): Name of the site.
            level_number (int): Level number within the site.

        Raises:
            KeyError: If city, site, or level does not exist.

        Returns:
            Level: The Level object for the specified identifiers.
        """
        city = self.cities.get(city_name)
        if not city:
            raise KeyError(f"City '{city_name}' not found")

        site = city.sites.get(site_name)
        if not site:
            raise KeyError(f"Site '{site_name}' not found in city '{city_name}'")

        level = site.levels.get(level_number)
        if not level:
            raise KeyError(f"Level {level_number} not found in site '{site_name}', city '{city_name}'")

        return level

    # ---------------- Parking ----------------
    def park_vehicle(self, city_name, site_name, level_number, vehicle):
        """
        Application-facing delegation method for parking a vehicle.

        Responsibilities:
        - Load the Level aggregate.
        - Delegate parking logic to Level.
        - Translate domain errors into user-friendly responses.

        Returns:
            tuple: (success (bool), message (str), assigned_slot (int or None))
        """
        try:
            level = self.get_level(city_name, site_name, level_number)
        except KeyError as e:
            return False, str(e), None

        try:
            assigned_slot = level.park_vehicle(vehicle)
            return (
                True,
                f"Parked {'EV' if vehicle.is_ev() else 'vehicle'} "
                f"at slot {assigned_slot} on level {level_number}",
                assigned_slot
            )
        except ValueError as e:
            return False, str(e), None

    # ---------------- Removing ----------------
    def remove_vehicle(self, city_name, site_name, level_number, slot_number, is_ev=False):
        """
        Application-facing delegation method for removing a vehicle.

        Responsibilities:
        - Load the Level aggregate.
        - Delegate removal logic to Level.
        - Enrich the returned domain data with location info.

        Returns:
            tuple: (success (bool), message (str), removal_info (dict or None))
        """
        try:
            level = self.get_level(city_name, site_name, level_number)
        except KeyError as e:
            return False, str(e), None

        try:
            removal_info = level.remove_vehicle(slot_number, is_ev)

            # Enrich domain result with location context
            removal_info.update({
                "city_name": city_name,
                "site_name": site_name,
                "level_number": level_number
            })

            return (
                True,
                f"Removed {'EV' if is_ev else 'vehicle'} from slot {slot_number}",
                removal_info
            )
        except ValueError as e:
            return False, str(e), None

    # ---------------- Status ----------------
    def get_ev_slots_info(self, city_name, site_name, level_number):
        """
        Return list of parked EVs with their slot number and vehicle object.

        Returns:
            list of dict: Each dict contains 'slot' and 'vehicle' keys.
        """
        try:
            level = self.get_level(city_name, site_name, level_number)
        except KeyError:
            return []

        return [
            {"slot": idx + 1, "vehicle": vehicle}
            for idx, vehicle in enumerate(level.ev_slots)
            if vehicle != -1
        ]

    def get_parking_status(self, city_name, site_name, level_number):
        """
        Returns current parking status for regular and EV slots.

        Returns:
            dict: {'regular': [...], 'ev': [...]}, each with vehicle details.
        """
        try:
            level = self.get_level(city_name, site_name, level_number)
        except KeyError:
            return {"regular": [], "ev": []}
        status = {"regular": [], "ev": []}

        # Regular slots
        for idx, vehicle in enumerate(level.regular_slots):
            if vehicle != -1:
                vehicle_info = {
                    "slot": idx + 1,
                    "regnum": vehicle.get_regnum(),
                    "make": vehicle.get_make(),
                    "model": vehicle.get_model(),
                    "color": vehicle.get_color(),
                    "type": vehicle.get_type()
                }
                status["regular"].append(vehicle_info)

        # EV slots
        for idx, vehicle in enumerate(level.ev_slots):
            if vehicle != -1:
                vehicle_info = {
                    "slot": idx + 1,
                    "regnum": vehicle.get_regnum(),
                    "make": vehicle.get_make(),
                    "model": vehicle.get_model(),
                    "color": vehicle.get_color(),
                    "type": vehicle.get_type()
                }
                status["ev"].append(vehicle_info)

        return status

    def get_vehicle_in_ev_slot(self, city_name, site_name, level_number, slot_number):
        """
        Retrieve the vehicle object occupying a specific EV slot.

        Returns:
            Vehicle or None: Vehicle object if occupied, None if empty or invalid slot.
        """
        try:
            level = self.get_level(city_name, site_name, level_number)
        except KeyError:
            return None
        idx = slot_number - 1
        if 0 <= idx < len(level.ev_slots):
            vehicle = level.ev_slots[idx]
            return vehicle if vehicle != -1 else None
        return None

    # ---------------- Searching ----------------
    def find_slots_by_regnum(self, city_name, site_name, level_number, regnum):
        """
        Find slots occupied by vehicles with the given registration number.

        Returns:
            tuple: (reg_slots, ev_slots) lists of slot numbers.
        """
        try:
            level = self.get_level(city_name, site_name, int(level_number))
        except KeyError as e:
            return False, str(e)

        reg_slots = [i + 1 for i, v in enumerate(level.regular_slots) if v != -1 and v.regnum.lower() == regnum.lower()]
        ev_slots = [i + 1 for i, v in enumerate(level.ev_slots) if v != -1 and v.regnum == regnum]
        return reg_slots, ev_slots

    def find_slots_by_color(self, city_name, site_name, level_number, color):
        """
        Find slots occupied by vehicles of a given color.

        Returns:
            tuple: (reg_slots, ev_slots) lists of slot numbers.
        """
        try:
            level = self.get_level(city_name, site_name, int(level_number))
        except KeyError as e:
            return False, str(e)

        reg_slots = [i + 1 for i, v in enumerate(level.regular_slots) if v != -1 and v.color.lower() == color.lower()]
        ev_slots = [i + 1 for i, v in enumerate(level.ev_slots) if v != -1 and v.color.lower() == color.lower()]
        return reg_slots, ev_slots

    def find_slots_by_model(self, city_name, site_name, level_number, model):
        """
        Find slots occupied by vehicles of a given model.

        Returns:
            tuple: (reg_slots, ev_slots) lists of slot numbers.
        """
        try:
            level = self.get_level(city_name, site_name, int(level_number))
        except KeyError as e:
            return False, str(e)

        reg_slots = [i + 1 for i, v in enumerate(level.regular_slots) if v != -1 and v.model.lower() == model.lower()]
        ev_slots = [i + 1 for i, v in enumerate(level.ev_slots) if v != -1 and v.model.lower() == model.lower()]
        return reg_slots, ev_slots

    def find_slots_by_make(self, city_name, site_name, level_number, make):
        """
        Find slots occupied by vehicles of a given make.

        Returns:
            tuple: (reg_slots, ev_slots) lists of slot numbers.
        """
        try:
            level = self.get_level(city_name, site_name, int(level_number))
        except KeyError as e:
            return False, str(e)

        reg_slots = [i + 1 for i, v in enumerate(level.regular_slots) if v != -1 and v.make.lower() == make.lower()]
        ev_slots = [i + 1 for i, v in enumerate(level.ev_slots) if v != -1 and v.make.lower() == make.lower()]
        return reg_slots, ev_slots

    def simulate_charging_hours(self, charger_id, hours, charger_controller):
        """
        !!! THIS IS ADDED TO SIMULATE THE CHARGING HARDWARE (ONLY FOR TESTING PURPOSE)
        Simulate elapsed charging hours for a charger session.

        Adjusts last_update and updates kWh delivered.

        Args:
            charger_id (str): Charger identifier.
            hours (float): Number of hours to simulate.
            charger_controller (ChargerController): Controller managing charger sessions.
        """

        level = self._find_level_by_charger(charger_id)
        if not level:
            return

        session = charger_controller.charger_usage.get(charger_id)

        if not session:
            # Check first vehicle in queue or first slot
            queue = level.charger_waiting_queue.get(charger_id)
            if queue and len(queue) > 0:
                slot_number = queue.popleft()
                vehicle = level.ev_slots[slot_number - 1]
            else:
                vehicle = level.ev_slots[0]
                if vehicle == -1:
                    return
                slot_number = 1

            charger_controller.start_charging(charger_id, vehicle, slot_number)
            session = charger_controller.charger_usage.get(charger_id)

        # Rewind last_update
        session["last_update"] = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        charger_controller.update_kwh(charger_id)


def main():
    """Entry point for the Parking Lot Manager application with GUI."""
    root = tk.Tk()
    root.geometry("875x750")
    root.resizable(0, 0)
    root.title("Parking Lot Manager")

    parking_lot = ParkingLot()
    app_service = ParkingApplicationService(parking_lot)

    """
    Uncomment the section below to run the EV charging hardware simulation.

    Simulation assumptions:
    - A single-level parking facility located in Boston
    - Site name: BST1
    - Capacity for 4 regular vehicles and 4 electric vehicles
    - Two EV chargers with IDs: BosBS1001 and BosBS1002

    Simulation behavior:
    - A vehicle connected to charger BosBS1001 after 8.57 hours of charging
    - A vehicle connected to charger BosBS1002 after 6 hours of charging
    """
    # app_service.make_lot(4, 4, 1, 'BST1', 'Boston', 2)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'Plate123','Toyota','Camry','White',0,0)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'Plate987','Toyota','Camry','Black',0,0)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'Plate876','Toyota','Corolla','White',0,0)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'Plate876','Toyota','Corolla','Black',0,0)

    # app_service.park_vehicle_and_assign('Boston','BST1',1,'PlBBt123','BYD','Seagull','White',1,0)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'PlBBe987','BYD','Seagull','White',1,0)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'PlCCe876','BYD','e2','Gray',1,0)
    # app_service.park_vehicle_and_assign('Boston','BST1',1,'PlDDe876','BYD','e2','Gray',1,0)

    # parking_lot.simulate_charging_hours('BosBS1001', 8.57, app_service.charger_controller)
    # parking_lot.simulate_charging_hours('BosBS1002', 6, app_service.charger_controller)

   
    ParkingLotUI(root, parking_lot, app_service)
    root.mainloop()


if __name__ == '__main__':
    main()
