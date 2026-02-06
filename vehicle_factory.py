# domain/factories/vehicle_factory.py
from Vehicle import Car, Motorcycle
from ElectricVehicle import ElectricCar, ElectricBike

class VehicleFactory:
    @staticmethod
    def create_vehicle(reg, make, model, color, ev=False, motor=False):
        """
        Factory method to create a Vehicle entity.

        Args:
            reg (str): Vehicle registration number
            make (str): Vehicle make
            model (str): Vehicle model
            color (str): Vehicle color
            ev (bool): True if EV, False if regular
            motor (bool): True if motorcycle, False if car

        Returns:
            Vehicle object (Car, Motorcycle, ElectricCar, ElectricBike)
        """
        if ev:
            if motor:
                return ElectricBike(reg, make, model, color)
            else:
                return ElectricCar(reg, make, model, color)
        else:
            if motor:
                return Motorcycle(reg, make, model, color)
            else:
                return Car(reg, make, model, color)
