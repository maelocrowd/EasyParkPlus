from datetime import datetime
import math
import Config

class ParkingBillingService:
    def __init__(self):
        self.hourly_rate = Config.PARKING_RATE_PER_HOUR

    def calculate(self, start_time: datetime, end_time: datetime) -> float:
        duration_seconds = (end_time - start_time).total_seconds()
        hours = math.ceil(duration_seconds / 3600)
        return hours * self.hourly_rate


class ChargingBillingService:
    def __init__(self):
        self.rate_per_kwh = Config.CHARGING_RATE_PER_KWH

    def calculate(self, kwh_delivered: float) -> float:
        return round(kwh_delivered * self.rate_per_kwh, 2)


class ExitBillingService:
    def __init__(self):
        self.parking_billing = ParkingBillingService()
        self.charging_billing = ChargingBillingService()

    def calculate_total(self, vehicle, start_time, end_time, kwh_delivered=None):
        """
        kwh_delivered: optional, if not passed for EVs, will read from vehicle.ev_behavior
        """
        parking_fee = self.parking_billing.calculate(start_time, end_time)

        charging_fee = 0.0
        if vehicle.is_ev():
            if kwh_delivered is None:
                kwh_delivered = getattr(vehicle.ev_behavior, "kwh_delivered_this_session", 0.0)
            charging_fee = self.charging_billing.calculate(kwh_delivered)

        return {
            "parking_fee": parking_fee,
            "charging_fee": charging_fee,
            "total": parking_fee + charging_fee
        }
