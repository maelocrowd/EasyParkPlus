class Vehicle:
    def __init__(self, regnum: str, make: str, model: str, color: str):
        self.regnum = regnum
        self.make = make
        self.model = model
        self.color = color

    # Getters
    def get_make(self):
        return self.make

    def get_model(self):
        return self.model

    def get_color(self):
        return self.color

    def get_regnum(self):
        return self.regnum

    # Polymorphic behavior
    def is_ev(self):
        return False

    def is_motorbike(self):
        return False

    def get_type(self):
        return self.__class__.__name__

class Car(Vehicle):
    def getType(self):
        return self.__class__.__name__

class Truck(Vehicle):

    def getType(self):
        return self.__class__.__name__


class Motorcycle(Vehicle):

    def getType(self):
        return self.__class__.__name__
    def is_motorbike(self):
        return True

class Bus(Vehicle):

    def getType(self):
        return self.__class__.__name__