class EVBehavior:
    """Encapsulates Electric Vehicle characteristics."""
    def __init__(self, battery_capacity_kwh: float):
        self.battery_capacity_kwh = battery_capacity_kwh
        self.charge_kwh = 0.0
        self.kwh_delivered_this_session = 0.0

    def get_charge(self) -> float:
        return self.charge_kwh

    def set_charge(self, charge_kwh: float):
        self.charge_kwh = min(charge_kwh, self.battery_capacity_kwh)

    def add_charge(self, kwh: float) -> float:
        """Adds charge and returns actual kWh accepted."""
        available_capacity = self.battery_capacity_kwh - self.charge_kwh
        accepted = min(kwh, available_capacity)
        self.charge_kwh += accepted
        self.kwh_delivered_this_session += accepted
        return accepted

    def is_fully_charged(self) -> bool:
        return self.charge_kwh >= self.battery_capacity_kwh
