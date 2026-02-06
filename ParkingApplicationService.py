from BillManager import ExitBillingService
from ChargerController import ChargerController
from vehicle_factory import VehicleFactory
from collections import deque

class ParkingApplicationService:
    def __init__(self, parking_lot):
        """Initialize the application service with billing, charger controller, and parking lot."""
        self.billing_service = ExitBillingService()
        self.charger_controller = ChargerController()
        self.parking_lot = parking_lot
        # self.charger_controller.parking_lot = ParkingLot()

    def make_lot(self, num_regular, num_ev, level_number, site_name, city_name, chargers=0):
        """Create a parking lot with given specifications and add levels to the site."""
        # Use ParkingLot method to get or create city
        city = self.parking_lot.get_or_create_city(city_name)

        # Use City method to get or create site
        site = city.get_or_create_site(site_name)

        added_levels = []
        for level_no in range(1, level_number + 1):
            success, msg = site.add_level(
                level_no,
                num_regular=num_regular,
                num_ev=num_ev,
                chargers=chargers
            )
            if success:
                added_levels.append(level_no)
            else:
                print(f"Warning: {msg}")

        return True, f"Lot created: City={city_name}, Site={site_name}, Levels added={added_levels}"

    def exit_bill(self, vehicle, start_time, end_time, kwh_delivered):
        """Calculate the total billing for a vehicle's parking and charging session."""
        return self.billing_service.calculate_total(vehicle, start_time, end_time, kwh_delivered)

    def get_charger_status(self, charger_id):
        """Return the status of a specific charger."""
        return self.charger_controller.get_charger_status(charger_id)

    def get_charger_usage(self, charger_id):
        """Return the charging session usage data for a specific charger."""
        return self.charger_controller.charger_usage.get(charger_id)

    def park_vehicle_and_assign(self, city_name, site_name, level_number,
                                reg, make, model, color, ev_car=False, motor=False):
        """
        Application-level parking method.
        Handles vehicle creation and EV charger assignment.
        """
        # Step 1: Create vehicle via factory
        vehicle = VehicleFactory.create_vehicle(
            reg=reg,
            make=make,
            model=model,
            color=color,
            ev=ev_car,
            motor=motor
        )

        # Step 2: Call domain method to park vehicle
        success, msg, assigned_slot = self.parking_lot.park_vehicle(
            city_name, site_name, level_number, vehicle
        )

        # Step 3: Handle EV charger assignment (delegated)
        if success and vehicle.is_ev():
            level = self.parking_lot.get_level(city_name, site_name, level_number)
            charger_id = level.ev_slot_chargers.get(assigned_slot - 1)
            if charger_id:
                status_info = self.charger_controller.get_charger_status(charger_id)
                if status_info["charger_status"] == "available":
                    self.ev_status_update(charger_id, vehicle, assigned_slot)
                else:
                    # Add to waiting queue if not already present
                    queue = level.charger_waiting_queue[charger_id]
                    if assigned_slot not in queue:
                        queue.append(assigned_slot)

        return success, msg, assigned_slot

    def remove_vehicle_and_process(self, city_name, site_name, level_number, slot_number, is_ev=False):
        """
        Orchestrates:
        - Remove vehicle from domain (ParkingLot)
        - Stop & release charger (if EV)
        - Assign charger to waiting vehicle
        - Calculate billing
        """
        success, msg, vehicle_info = self.parking_lot.remove_vehicle(city_name, site_name, level_number, slot_number, is_ev)
        if not success:
            return False, msg, None

        vehicle = vehicle_info["vehicle"]
        kwh_delivered = vehicle_info.get("charge_kwh")

        # Handle EV charger
        if is_ev:
            level = self.parking_lot.get_level(city_name, site_name, level_number)
            idx = slot_number - 1
            charger_id = level.ev_slot_chargers.get(idx)
            if charger_id:
                # Stop and release charger
                self.charger_controller.stop_charging(charger_id)
                self.charger_controller.release_charger(charger_id)
                # Assign to waiting vehicle
                self.auto_assign_waiting_vehicle(charger_id)

                # If vehicle was fully charged, take battery capacity
                if vehicle.ev_behavior.is_fully_charged():
                    kwh_delivered = vehicle.ev_behavior.battery_capacity_kwh
                else:
                    session = self.charger_controller.charger_usage.get(charger_id)
                    if session and session.get("vehicle_reg") == vehicle.get_regnum():
                        self.charger_controller.update_kwh(charger_id)
                        kwh_delivered = session.get("kwh_delivered", 0.0)

        # Calculate billing
        billing_summary = self.exit_bill(
            vehicle,
            vehicle_info.get("start_time"),
            vehicle_info.get("end_time"),
            kwh_delivered
        )

        return True, msg, billing_summary

    def ev_status_update(self, charger_id, vehicle, slot_number):
        """
        Assign EV to a charger if available, or put in waiting queue.
        """
        # Get level from ParkingLot
        level = self.parking_lot._find_level_by_charger(charger_id)
        if not level:
            return False, f"Charger {charger_id} not found"

        # Check charger status via ChargerController
        status_info = self.charger_controller.get_charger_status(charger_id)

        if status_info["charger_status"] == "available":
            # Start charging
            self.charger_controller.start_charging(charger_id, vehicle, slot_number)
            return True, f"Started charging {vehicle.get_regnum()} on {charger_id}"
        else:
            # Add to waiting queue
            queue = level.charger_waiting_queue[charger_id]
            if slot_number not in queue:
                queue.append(slot_number)
            return False, f"Charger busy, added {vehicle.get_regnum()} (slot {slot_number}) to waiting queue"

    def auto_assign_waiting_vehicle(self, charger_id):
        """Assign first waiting EV to the charger if available."""
        level = self.parking_lot._find_level_by_charger(charger_id)
        if not level:
            return

        queue = level.charger_waiting_queue.get(charger_id, deque())
        # Check if charger is already available before popping
        status_info = self.charger_controller.get_charger_status(charger_id)
        if status_info["charger_status"] != "available":
            return

        while queue:
            slot_number = queue.popleft()
            vehicle = self.parking_lot.get_vehicle_in_ev_slot(
                level.city_name,
                level.site_name,
                level.level_number,
                slot_number
            )
            if vehicle:
                # Delegate to charger controller
                self.ev_status_update(charger_id, vehicle, slot_number)
                break
            # skip empty slots automatically

    def get_ev_charge_status(self, city_name, site_name, level_number):
        """Return the charge status of all EVs in a level."""
        # Proper attribute access
        city = self.parking_lot.cities.get(city_name)
        if not city:
            return []

        site = city.sites.get(site_name)
        if not site:
            return []

        level = site.levels.get(level_number)
        if not level:
            return []

        charge_list = []
        for idx, vehicle in enumerate(level.ev_slots):
            if vehicle == -1:
                continue
            slot = idx + 1
            charger_id = self.get_charger_for_slot(vehicle, city_name, site_name, level_number, slot)
            session = self.charger_controller.charger_usage.get(charger_id) if charger_id else None

            if session and session.get("vehicle_reg") == vehicle.get_regnum():
                prev_status = session.get("status")
                self.charger_controller.update_kwh(charger_id)

                # Automatically assign waiting EV if charging just completed
                if prev_status == "charging" and session.get("status") == "full":
                    self.auto_assign_waiting_vehicle(charger_id)

                status = session.get("status")
                kwh = session.get("kwh_delivered", 0.0)
                start_time = session.get("start_time")
            else:
                # Vehicle not currently in a session
                if vehicle.ev_behavior.is_fully_charged():
                    status = "full"
                    kwh = vehicle.ev_behavior.charge_kwh
                    start_time = None
                else:
                    status = "waiting"
                    kwh = 0.0
                    start_time = None

            battery_capacity = vehicle.ev_behavior.battery_capacity_kwh
            charge_percent = min(100, round((kwh / battery_capacity) * 100, 2)) if battery_capacity > 0 else 0.0

            charge_list.append({
                "slot": slot,
                "regnum": vehicle.get_regnum(),
                "charge_status": status,
                "charger_id": charger_id,
                "kwh_delivered": kwh,
                "charge_percent": charge_percent,
                "start_time": start_time
            })

        return charge_list

    def get_charger_for_slot(self, vehicle, city_name, site_name, level_number, slot_number):
        """Return charger_id assigned to the given EV slot"""
        try:
            level = self.parking_lot.get_level(city_name, site_name, level_number)
            idx = slot_number - 1
            return level.ev_slot_chargers.get(idx)
        except KeyError:
            return None

    def get_all_cities(self):
        """Return a list of all city names in the parking lot."""
        return list(self.parking_lot.cities.keys())

    def get_sites_in_city(self, city_name):
        """Return a list of site names in the given city."""
        city = self.parking_lot.cities.get(city_name)
        if city:
            return list(city.sites.keys())
        return []

    def get_levels_in_site(self, city_name, site_name):
        """Return a list of level numbers in the given site."""
        city = self.parking_lot.cities.get(city_name)
        if city and site_name in city.sites:
            return list(city.sites[site_name].levels.keys())
        return []
