from Vehicle import Car, Motorcycle
from EVBehavior import EVBehavior


class ElectricVehicle:
    """Base class for EV capability"""
    def __init__(self, battery_capacity_kwh: float):
        self.ev_behavior = EVBehavior(battery_capacity_kwh)

    def is_ev(self):
        return True


class ElectricCar(ElectricVehicle, Car):
    def __init__(self, regnum, make, model, color, battery_capacity_kwh=60):
        Car.__init__(self, regnum, make, model, color)
        ElectricVehicle.__init__(self, battery_capacity_kwh)


class ElectricBike(ElectricVehicle, Motorcycle):
    def __init__(self, regnum, make, model, color, battery_capacity_kwh=15):
        Motorcycle.__init__(self, regnum, make, model, color)
        ElectricVehicle.__init__(self, battery_capacity_kwh)
