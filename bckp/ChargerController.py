from datetime import datetime, timezone


class ChargerController:
    def __init__(self):
        # charger_id -> session dict
        self.charger_usage = {}

    def get_charger_status(self, charger_id):
        session = self.charger_usage.get(charger_id)

        if not session:
            return {
                "charger_ID": charger_id,
                "charger_status": "available",
                "current_session": None
            }

        charger_status = (
            "charging" if session["status"] == "charging"
            else "occupied"   # full or stopped but still plugged
        )

        return {
            "charger_ID": charger_id,
            "charger_status": charger_status,
            "current_session": session
        }

    def start_charging(self, charger_id, vehicle, slot_number):
        if charger_id in self.charger_usage:
            raise Exception(f"Charger {charger_id} already in use")

        now = datetime.now(timezone.utc)

        session = {
            "session_id": f"S-{vehicle.get_regnum()}",
            "vehicle": vehicle,                     # 🔥 required
            "vehicle_reg": vehicle.get_regnum(),
            "slot": slot_number,
            "start_time": now.isoformat(),
            "last_update": now.isoformat(),
            "kwh_delivered": 0.0,
            "status": "charging"                    # charging | full | stopped
        }

        self.charger_usage[charger_id] = session

    def update_kwh(self, charger_id, rate_kw=7):
        session = self.charger_usage.get(charger_id)
        if not session or session["status"] != "charging":
            return

        last_update = datetime.fromisoformat(session["last_update"])
        now = datetime.now(timezone.utc)

        elapsed_hours = (now - last_update).total_seconds() / 3600
        if elapsed_hours <= 0:
            return

        added_kwh = elapsed_hours * rate_kw

        # EV decides how much energy it can accept
        accepted = session["vehicle"].ev_behavior.add_charge(added_kwh)

        session["kwh_delivered"] = round(
            session["kwh_delivered"] + accepted, 3
        )
        session["last_update"] = now.isoformat()

        # Auto stop when full
        if session["vehicle"].ev_behavior.is_fully_charged():
            session["status"] = "full"
            session["end_time"] = now.isoformat()
            charger_id_copy = charger_id  # safety

            # 🔥 RELEASE charger so it becomes AVAILABLE
            self.release_charger(charger_id_copy)

            # 🔥 AUTO ASSIGN waiting EV
            if hasattr(self, "parking_lot"):
                self.parking_lot.auto_assign_waiting_vehicle(charger_id_copy)

    def stop_charging(self, charger_id):
        session = self.charger_usage.get(charger_id)
        if not session:
            return

        if session["status"] == "charging":
            session["status"] = "stopped"
            session["end_time"] = datetime.now(timezone.utc).isoformat()

    def release_charger(self, charger_id):
        """
        Called when the vehicle unplugs / exits parking.
        Billing should already be done before this.
        """
        if charger_id in self.charger_usage:
            del self.charger_usage[charger_id]