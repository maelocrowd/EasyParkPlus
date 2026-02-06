# ParkingUI.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import Config

class ParkingLotUI:
    def __init__(self, root, parking_lot, app_service):
        self.root = root
        self.parking_lot = parking_lot
        self.app_service = app_service

        # Variables
        self.city_name = tk.StringVar()
        self.site_name = tk.StringVar()
        self.level_value = tk.StringVar()
        self.num_regular_slots = tk.StringVar()
        self.num_ev_slots = tk.StringVar()
        self.num_EVChargers = tk.StringVar()
        self.make_value = tk.StringVar()
        self.model_value = tk.StringVar()
        self.color_value = tk.StringVar()
        self.reg_value = tk.StringVar()
        self.slot_num_for_vehicle_remove = tk.StringVar()
        self.cbx_ev_car = tk.IntVar()
        self.cbx_motor = tk.IntVar()
        self.cbx_ev_remove = tk.IntVar()
        self.seach_parameter = tk.StringVar()

        self.txt_display = tk.Text(root, width=101, height=20)
        yscroll = tk.Scrollbar(self.root, orient="vertical", command=self.txt_display.yview)
        yscroll.grid(row=13, column=6, sticky="ns")
        self.txt_display.config(yscrollcommand=yscroll.set)

        self.create_widgets()

    def create_widgets(self):
        # Heading
        tk.Label(self.root, text='Parking Lot Manager', font='Arial 14 bold').grid(row=0, column=0, columnspan=6, padx=10)
        tk.Label(self.root, text='Lot Creation', font='Arial 12 bold').grid(row=1, column=0, columnspan=6, padx=10)

        # City & Site & Level for lot creation
        tk.Label(self.root, text='City', font='Arial 12').grid(row=2, column=0)
        city_list = Config.CITY_LIST
        self.city_combo = ttk.Combobox(self.root, values=city_list,state="readonly", textvariable=self.city_name, font='Arial 12', width=12)
        self.city_combo.set('--Select city--')
        self.city_combo.grid(row=2, column=1)
        
        tk.Label(self.root, text='Site', font='Arial 12').grid(row=2, column=2)
        self.site_combo = tk.Entry(self.root, textvariable=self.site_name, font='Arial 12', width=12)
        self.site_combo.grid(row=2, column=3)
        
        tk.Label(self.root, text='Level', font='Arial 12').grid(row=2, column=4)
        self.level_combo = tk.Entry(self.root, textvariable=self.level_value, font='Arial 12', width=6)
        self.level_combo.grid(row=2, column=5)

        # Slots
        tk.Label(self.root, text='Regular Slots', font='Arial 12').grid(row=3, column=0)
        tk.Entry(self.root, textvariable=self.num_regular_slots, width=6, font='Arial 12').grid(row=3, column=1)
        tk.Label(self.root, text='EV Slots', font='Arial 12').grid(row=3, column=2)
        tk.Entry(self.root, textvariable=self.num_ev_slots, width=6, font='Arial 12').grid(row=3, column=3)
        tk.Label(self.root, text='EV Chargers', font='Arial 12').grid(row=3, column=4)
        tk.Entry(self.root, textvariable=self.num_EVChargers, width=6, font='Arial 12').grid(row=3, column=5)

        tk.Button(self.root, command=self.on_create_lot, text='Create Parking Lot', font='Arial 12',
                  bg='lightblue', fg='black', activebackground='teal').grid(row=4, column=0, padx=4, pady=4)

        # Car Management
        tk.Label(self.root, text='Car Management', font='Arial 12 bold').grid(row=5, column=0, columnspan=6, padx=10)
        tk.Label(self.root, text='Make', font='Arial 12').grid(row=6, column=0)
        tk.Entry(self.root, textvariable=self.make_value, font='Arial 12', width=12).grid(row=6, column=1)
        tk.Label(self.root, text='Model', font='Arial 12').grid(row=6, column=2)
        tk.Entry(self.root, textvariable=self.model_value, font='Arial 12', width=12).grid(row=6, column=3)
        tk.Label(self.root, text='Color', font='Arial 12').grid(row=7, column=0)
        tk.Entry(self.root, textvariable=self.color_value, font='Arial 12', width=12).grid(row=7, column=1)
        tk.Label(self.root, text='Registration #', font='Arial 12').grid(row=7, column=2)
        tk.Entry(self.root, textvariable=self.reg_value, font='Arial 12', width=12).grid(row=7, column=3)

        tk.Checkbutton(self.root, text='Electric', variable=self.cbx_ev_car, font='Arial 12').grid(row=8, column=0)
        tk.Checkbutton(self.root, text='Motorcycle', variable=self.cbx_motor, font='Arial 12').grid(row=8, column=1)

        # Parking selection for vehicle
        tk.Label(self.root, text='Select City', font='Arial 12').grid(row=9, column=0)
        self.city_park_combo = ttk.Combobox(self.root, values=city_list,state="readonly", font='Arial 12', width=12)
        self.city_park_combo.set('--Select city--')
        self.city_park_combo.grid(row=9, column=1)
        self.city_park_combo.bind("<<ComboboxSelected>>", self.update_sites_park)

        tk.Label(self.root, text='Select Site', font='Arial 12').grid(row=9, column=2)
        self.site_park_combo = ttk.Combobox(self.root, values=[],state="readonly", font='Arial 12', width=12)
        self.site_park_combo.set('--Select site--')
        self.site_park_combo.grid(row=9, column=3)
        self.site_park_combo.bind("<<ComboboxSelected>>", self.update_levels_park)

        tk.Label(self.root, text='Select Level', font='Arial 12').grid(row=9, column=4)
        self.level_park_combo = ttk.Combobox(self.root, values=[],state="readonly", font='Arial 12', width=6)
        self.level_park_combo.set('--Select level--')
        self.level_park_combo.grid(row=9, column=5)

        tk.Button(self.root, command=self.on_park_vehicle, text='Park Vehicle', font='Arial 12',
                  bg='lightgreen', fg='black', activebackground='green').grid(row=10, column=0, padx=4, pady=4)

        # Vehicle Removal
        tk.Label(self.root, text='Slot # to remove', font='Arial 12').grid(row=11, column=0)
        tk.Entry(self.root, textvariable=self.slot_num_for_vehicle_remove, font='Arial 12', width=12).grid(row=11, column=1)
        tk.Checkbutton(self.root, text='Remove EV?', variable=self.cbx_ev_remove, font='Arial 12').grid(row=11, column=2)
        tk.Button(self.root, command=self.on_remove_vehicle, text='Remove Vehicle', font='Arial 12',
                  bg='tomato', fg='black', activebackground='red').grid(row=11, column=3)

        # Status Buttons
        tk.Button(self.root, command=self.on_status, text='Current Lot Status', font='Arial 12',
                  bg='PaleGreen1', fg='black', activebackground='PaleGreen3').grid(row=12, column=0, padx=4, pady=4)
        tk.Button(self.root, command=self.on_charge_status, text='EV Charge Status', font='Arial 12',
                  bg='lightblue', fg='black', activebackground='teal').grid(row=12, column=1, padx=4, pady=4)

        # Search Parameters
        tk.Label(self.root, text='Search Option', font='Arial 12').grid(row=12, column=2)
        option_list = ['Registration No', 'Color', 'Model', 'Make']
        self.search_combo = ttk.Combobox(self.root, values=option_list,state="readonly", font='Arial 12', width=12)
        self.search_combo.set('--Select Option-')
        self.search_combo.grid(row=12, column=3)
        
        tk.Entry(self.root, textvariable=self.seach_parameter, font='Arial 12', width=12).grid(row=12, column=4)
        tk.Button(self.root, command=self.on_search, text='Search', font='Arial 12',
                  bg='lightblue', fg='black', activebackground='teal').grid(row=12, column=5, padx=4, pady=4)

        # Text Display
        self.txt_display.grid(row=13, column=0, columnspan=6, padx=10, pady=10)

    
    # ---------------- UI helper methods ----------------
    def update_sites(self, event=None):
        city = self.city_name.get()
        sites = self.app_service.get_sites_in_city(city)
        self.site_combo = sites if sites else []

    def update_levels(self, event=None):
        city = self.city_name.get()
        site = self.site_name.get()
        levels = self.app_service.get_levels_in_site(city, site)
        self.level_combo = levels if levels else []

    def update_sites_park(self, event=None):
        city = self.city_park_combo.get()
        sites = self.app_service.get_sites_in_city(city)
        self.site_park_combo['values'] = sites if sites else []

    def update_levels_park(self, event=None):
        city = self.city_park_combo.get()
        site = self.site_park_combo.get()
        levels = self.app_service.get_levels_in_site(city, site)
        self.level_park_combo['values'] = levels if levels else []


    def on_create_lot(self):
        CITY_PLACEHOLDER = "--Select city--"
        SITE_PLACEHOLDER = "--Select site--"
        site = self.site_name.get()
        city = self.city_name.get()
                
        missing_fields = []

        if city in ("", CITY_PLACEHOLDER):
            missing_fields.append("City")

        if site in ("", SITE_PLACEHOLDER):
            missing_fields.append("Site")

        
        try:
            num_regular = int(self.num_regular_slots.get())
            num_ev = int(self.num_ev_slots.get())
            level = int(self.level_value.get())
            chargers = int(self.num_EVChargers.get())
        except ValueError:
            self.show_error("Level, Slots, and EV Chargers must be valid numbers!")
            return
        if num_ev > 0 and chargers < 1:
            missing_fields.append("You can't create a Parking Lot that have Ev Cars with no Charger!")
        if missing_fields:
            self.show_error(
                "Please select or provide the following from Lot Creation Section:\n- "
                + "\n- ".join(missing_fields)
            )
            return
 
        success, msg = self.app_service.make_lot(num_regular, num_ev, level, site, city, chargers)
        if success:
            self.show_info(msg)
            self.update_sites()
            self.update_levels()
        else:
            self.show_error(msg)

    def on_park_vehicle(self):
        CITY_PLACEHOLDER = "--Select city--"
        SITE_PLACEHOLDER = "--Select site--"
        LEVEL_PLACEHOLDER = "--Select level--"
        
        city = self.city_park_combo.get()
        site = self.site_park_combo.get()
        level = self.level_park_combo.get()
        reg = self.reg_value.get().strip()
        make = self.make_value.get().strip()
        model = self.model_value.get().strip()
        color = self.color_value.get().strip()
        missing_fields = []

        if city in ("", CITY_PLACEHOLDER):
            missing_fields.append("City")

        if site in ("", SITE_PLACEHOLDER):
            missing_fields.append("Site")

        if level in ("", LEVEL_PLACEHOLDER):
            missing_fields.append("Level")
        else:
            try:
                level = int(self.level_park_combo.get())
            except ValueError:
                self.show_error("Level must be a valid number")
                return
        if model=="" or reg == "" or make=="" or color == "":
            missing_fields.append("Car Make, Model, Registration, and Color can't be empty!")

        if missing_fields:
            self.show_error(
                "Please select or provide the following from Car Management Section:\n- "
                + "\n- ".join(missing_fields)
            )
            return

        ev = self.cbx_ev_car.get()
        motor = self.cbx_motor.get()

        success, msg, slot = self.app_service.park_vehicle_and_assign(city, site, level, reg, make, model, color, ev, motor)
        if success:
            self.show_info(msg)
        else:
            self.show_error(msg)

    def on_remove_vehicle(self):
        CITY_PLACEHOLDER = "--Select city--"
        SITE_PLACEHOLDER = "--Select site--"
        LEVEL_PLACEHOLDER = "--Select level--"
        
        city = self.city_park_combo.get()
        site = self.site_park_combo.get()
        level = self.level_park_combo.get()
        
        missing_fields = []

        if city in ("", CITY_PLACEHOLDER):
            missing_fields.append("City")

        if site in ("", SITE_PLACEHOLDER):
            missing_fields.append("Site")

        if level in ("", LEVEL_PLACEHOLDER):
            missing_fields.append("Level")
        else:
            try:
                level = int(self.level_park_combo.get())
                slot_num = int(self.slot_num_for_vehicle_remove.get())
            except ValueError:
                self.show_error("Level and Slot Number must be a valid number")
                return

        if missing_fields:
            self.show_error(
                "Please select or provide the following from Car Management Section:\n- "
                + "\n- ".join(missing_fields)
            )
            return

        # Ensure ev is boolean
        ev = bool(self.cbx_ev_remove.get())

        # Unpack 3 values from remove_vehicle
        # success, msg, billing = self.parking_lot.remove_vehicle(city, site, level, slot_num, ev)
        success, msg, billing = self.app_service.remove_vehicle_and_process(city, site, level, slot_num, ev)

        if success:
            # Show removal message
            self.show_info(msg)

            # Show billing details
            billing_msg = f"Parking Fee: {billing['parking_fee']}\n"
            if ev:
                billing_msg += f"Charging Fee: {billing['charging_fee']}\n"
            billing_msg += f"Total: {billing['total']}"
            self.show_info(billing_msg)
        else:
            self.show_error(msg)

    def on_search(self):
        CITY_PLACEHOLDER = "--Select city--"
        SITE_PLACEHOLDER = "--Select site--"
        LEVEL_PLACEHOLDER = "--Select level--"
        OPTION_PLACEHOLDER = "--Select Option--"

        city = self.city_park_combo.get()
        site = self.site_park_combo.get()
        level = self.level_park_combo.get()
        search_option = self.search_combo.get()
        search_criteria = self.seach_parameter.get()

        missing_fields = []

        if city in ("", CITY_PLACEHOLDER):
            missing_fields.append("City")

        if site in ("", SITE_PLACEHOLDER):
            missing_fields.append("Site")

        if level in ("", LEVEL_PLACEHOLDER):
            missing_fields.append("Level")
        else:
            try:
                level = int(level)
            except ValueError:
                self.show_error("Level must be a valid number")
                return

        if search_option in ("", OPTION_PLACEHOLDER):
            missing_fields.append("Search option")

        if not search_criteria:
            missing_fields.append("Search criteria")

        if missing_fields:
            self.show_error(
                "Please select or provide the following from Car Management Section:\n- "
                + "\n- ".join(missing_fields)
            )
            return

        if self.search_combo.get() == 'Color':
            regular_slot, ev_slots = self.parking_lot.find_slots_by_color(city, site, level, self.seach_parameter.get())
            msg_rgl= ""
            msg_ev = ""
            msg = ""
            for i in regular_slot:
                msg_rgl += str(i)+ ","
            for i in ev_slots:
                msg_ev+= str(i)+", "
            msg_rgl = ", ".join(map(str, regular_slot)) if regular_slot else "None"
            msg_ev = ", ".join(map(str, ev_slots)) if ev_slots else "None"

            msg = (
                f"\nCity: {city}, Site: {site}, Level: {level}\n"
                f"Regular Cars Found at Slot Numbers:\n{msg_rgl}\n"
                f"EV Cars Found at Slot Numbers: \n{msg_ev}"
            )
            self.show_info(msg)
        elif self.search_combo.get() == 'Registration No':
            regular_slot, ev_slots = self.parking_lot.find_slots_by_regnum(city, site, level, self.seach_parameter.get())
            msg_rgl= ""
            msg_ev = ""
            msg = ""
            for i in regular_slot:
                msg_rgl += str(i)+ ","
            for i in ev_slots:
                msg_ev+= str(i)+", "
            msg_rgl = ", ".join(map(str, regular_slot)) if regular_slot else "None"
            msg_ev = ", ".join(map(str, ev_slots)) if ev_slots else "None"

            msg = (
                f"\nCity: {city}, Site: {site}, Level: {level}\n"
                f"Regular Cars Found at Slot Numbers:\n{msg_rgl}\n"
                f"EV Cars Found at Slot Numbers: \n{msg_ev}"
            )
            self.show_info(msg)
        elif self.search_combo.get() == 'Model':
            regular_slot, ev_slots = self.parking_lot.find_slots_by_model(city, site, level, self.seach_parameter.get())
            msg_rgl= ""
            msg_ev = ""
            msg = ""
            for i in regular_slot:
                msg_rgl += str(i)+ ","
            for i in ev_slots:
                msg_ev+= str(i)+", "
            msg_rgl = ", ".join(map(str, regular_slot)) if regular_slot else "None"
            msg_ev = ", ".join(map(str, ev_slots)) if ev_slots else "None"

            msg = (
                f"\nCity: {city}, Site: {site}, Level: {level}\n"
                f"Regular Cars Found at Slot Numbers:\n{msg_rgl}\n"
                f"EV Cars Found at Slot Numbers: \n{msg_ev}"
            )
            self.show_info(msg)
        elif self.search_combo.get() == 'Make':
            regular_slot, ev_slots = self.parking_lot.find_slots_by_make(city, site, level, self.seach_parameter.get())
            msg_rgl= ""
            msg_ev = ""
            msg = ""
            for i in regular_slot:
                msg_rgl += str(i)+ ","
            for i in ev_slots:
                msg_ev+= str(i)+", "
            msg_rgl = ", ".join(map(str, regular_slot)) if regular_slot else "None"
            msg_ev = ", ".join(map(str, ev_slots)) if ev_slots else "None"

            msg = (
                f"\nCity: {city}, Site: {site}, Level: {level}\n"
                f"Regular Cars Found at Slot Numbers:\n{msg_rgl}\n"
                f"EV Cars Found at Slot Numbers: \n{msg_ev}"
            )
            self.show_info(msg)
        else:
            return

    def on_status(self):
        output = ""

        cities = self.app_service.get_all_cities()
        if not cities:
            self.show_info("No parking lots created yet")
            return

        for city_name in cities:
            sites = self.app_service.get_sites_in_city(city_name)
            for site_name in sites:
                levels = self.app_service.get_levels_in_site(city_name, site_name)
                for level_number in levels:
                    status = self.parking_lot.get_parking_status(city_name, site_name, level_number)

                    if not status["regular"] and not status["ev"]:
                        continue

                    output += f"\nCity: {city_name}, Site: {site_name}, Level: {level_number}\n"
                    output += "Regular Vehicles:\n"
                    output += "Slot\tReg No.\tColor\tMake\tModel\n"

                    for v in status["regular"]:
                        output += f"{v['slot']}\t{v['regnum']}\t{v['color']}\t{v['make']}\t{v['model']}\n"

                    output += "Electric Vehicles:\n"
                    output += "Slot\tReg No.\tColor\tMake\tModel\n"
                    for v in status["ev"]:
                        output += f"{v['slot']}\t{v['regnum']}\t{v['color']}\t{v['make']}\t{v['model']}\n"

        if output:
            self.show_info(output)
        else:
            self.show_info("Parking lots are empty")

    def on_charge_status(self):
        cities = self.app_service.get_all_cities()
        if not cities:
            self.show_info("No parking lots created yet")
            return

        header = (
            "Electric Vehicle Charge Levels Across All Parking Lots\n\n"
            f"{'City':12} {'Site':8} {'Level':5} {'Slot':5} "
            f"{'Reg No':10} {'Status':10} {'Charger':10} "
            f"{'kWh':5} {'%':5} {'Start Time':16}\n"
        )
        separator = "-" * 95 + "\n"
        output = header + separator

        any_ev = False

        for city_name in cities:
            sites = self.app_service.get_sites_in_city(city_name)
            for site_name in sites:
                levels = self.app_service.get_levels_in_site(city_name, site_name)
                for level_number in levels:
                    charge_list = self.app_service.get_ev_charge_status(city_name, site_name, level_number)

                    for info in charge_list:
                        any_ev = True

                        status = info.get("charge_status", "waiting")
                        kwh = info.get("kwh_delivered", 0.0)
                        percent = info.get("charge_percent", 0.0)
                        charger_id = info.get('charger_id', "-")

                        start_time_raw = info.get("start_time")
                        if start_time_raw:
                            dt = datetime.fromisoformat(start_time_raw)
                            start_time = dt.strftime("%Y-%m-%d %H:%M")
                        else:
                            start_time = "-"

                        output += (
                            f"{city_name:12} {site_name:8} {level_number:<5} {info['slot']:<5} "
                            f"{info['regnum']:10} {status:10} {charger_id:8} "
                            f"{kwh:5.2f} {percent:5.2f}% {start_time:16}\n"
                        )

        if any_ev:
            self.show_info(output)
        else:
            self.show_info("No EVs parked across all parking lots")
    # ---------------- Display ----------------
    def show_error(self, msg):
        self.txt_display.tag_configure("error", foreground="red")
        self.txt_display.insert(tk.END, msg + "\n")

    def show_info(self, msg):
        self.txt_display.insert(tk.END, msg + "\n")
