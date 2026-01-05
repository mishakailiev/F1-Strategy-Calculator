import tkinter as tk
from PIL import Image, ImageTk
from typing import Tuple
from copy import copy, deepcopy
from race_strategy_calculator import Race_Simulator, Tyre, ers_car, fuel_car, Car, Race_basic_information
import json
import os

    
def main():
    main_window = tk.Tk()
    main_window.geometry("1400x700")
    main_window.title("Race Information Import")
    main_window.iconphoto(True, tk.PhotoImage(file="F1-Logo.png"))
    main_window.config(background="#FFFFFF")
    # Configer Starting Tyres
    choose_tyre_position_y = 90
    choose_tyre_position_x = 1200
    choose_tyre_gap_between = 70
    title_font_size = 16
    
    tyre_type_position_x = 350
    tyre_type_position_y = 150
    gap_tyre_type_x = 230
    gap_tyre_type_y = 45
    row = 0
    col = 0
    
    titles: dict[str, tk.Label] = {}
    titles["Title"] = tk.Label(
        main_window,
        text="Race Strategy",
        font=("Arial", 20),
        background="#FFFFFF"
    )
    titles["Title"].place(x= 600, y=0)
    
    titles["Starting_tyre"] = tk.Label(
        main_window, 
        text="Choose a starting tyre!",
        font=("Arial", title_font_size),
        background="#FFFFFF",
    )
    titles["Starting_tyre"].place(x=choose_tyre_position_x - 50, y=choose_tyre_position_y - 40)
    
    titles["Race_data"] = tk.Label(
        main_window, 
        text="Race Data",
        font=("Arial", title_font_size),
        background="#FFFFFF"
    )
    titles["Race_data"].place(x=30, y=choose_tyre_position_y - 40)
    
    car_info_x = 10
    car_info_y = 500
    titles["Car_data"] = tk.Label(
        main_window,
        text="Car Data",
        font=("Arial", title_font_size),
        background="#FFFFFF"
    )
    titles["Car_data"].place(x=30, y=car_info_y)
    
    titles["Tyres_type"] = tk.Label(
        main_window,
        text="Tyre type",
        font=("Arial", title_font_size),
        background="#FFFFFF"
    )
    titles["Tyres_type"].place(x=550, y=choose_tyre_position_y - 40)
    
    
    tyres = ["Soft", "Medium", "Hard"]
    starting_tyre_var = tk.StringVar(master=main_window, value="Medium")
    tyre_images: dict[str, ImageTk.PhotoImage] = {}
    start_tyre_radio_button: dict[str, tk.Radiobutton] = {}
    
    i = 0
    for Ttype in tyres:
        string_name = Ttype + "-tyre.png"
        img = Image.open(string_name)
        img = img.resize((40, 40), Image.LANCZOS)
        tyre_images[Ttype] = ImageTk.PhotoImage(img)
        
        start_tyre_radio_button[Ttype] = tk.Radiobutton(
            main_window,
            variable=starting_tyre_var,
            value=Ttype,
            text=Ttype,
            font=("Arial", 14),
            image=tyre_images[Ttype],
            compound="left",
            background="#FFFFFF"
        )
        start_tyre_radio_button[Ttype].place(x=choose_tyre_position_x, y=choose_tyre_position_y + choose_tyre_gap_between * i)
        
        titles[Ttype] = tk.Label(
            main_window,
            text=Ttype,
            font=("Arial", 12),
            background="#FFFFFF",
            image=tyre_images[Ttype],
            compound="left",
        )
        titles[Ttype].place(x=tyre_type_position_x + 10 + gap_tyre_type_x * i, y=90)
        
        i += 1
    
    race_data_dict: dict[str, Tuple [tk.Entry, tk.Label, float | int]] = {
        "Race_laps": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Race laps",
                background="#FFFFFF",
                font=("Arial", 12)
            ),
            int(10)
        ),
        
        "Pit_stops": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Pit stops",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            int(2)
        ),
        
        "Pit_loss": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Pit loss time (s)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(22.000)
        ),
        
        "Coeff_safety_car": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Coefficient under safety car",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(0.650)
        ),
        
        "Safety_car_probability": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Safety car probability",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(0.000)
        ),
        
        "Lock_up_probability": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Lock up probability",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(0.000)
        ),
        
        "Lock_up_degradation": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Lock up degradation",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(1.100)
        ),
        
        "Push_after_pit_stop": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Push after pit stop",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(1.020)
        ),
        
        "Time_lost_by_fuel": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Time lost by fuel (s/kg)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(0.032)
        ),
        
        "Push_lift_difference": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Push-lift coefficient (max 0.01)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(0.007)
        ),
        
        "Top_n_strategies": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF"
            ),
            tk.Label(
                main_window,
                text="Save top N strategies",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(1.000)
        )
    }
    gap_between_race_info = 35
    i = 0
    for key in race_data_dict.keys():
        race_data_dict[key][0].place(x=10, y=choose_tyre_position_y + gap_between_race_info * i)
        race_data_dict[key][1].place(x=60, y=choose_tyre_position_y + gap_between_race_info * i)
        i += 1
    del i
    
    car_data_dict: dict[str, Tuple [tk.Entry, tk.Label, float | str | int]]= {
        "Driver_number": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Driver number",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            int(1)
        ),
        
        "Driver_name": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=8,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Driver name",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            str("Hamilton")
        ),
        
        "Team_name": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=8,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Team",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            str("Ferrari")
        ),
        
        "Fuel_mass": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Fuel in car (kg)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(100.00)
        ),
        
        "Fuel_max": (
            tk.Entry(
                main_window, 
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Fuel max (kg)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(120.000)
        ),
        
        "Fuel_burn_per_lap": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="Fuel burn per lap (kg)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(0.950)
        ),
        
        "Ers_store_max": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=7,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="ERS store max (kw)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(4000)
        ),
        
        "Ers_deployment": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="ERS deployed per lap (kw)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(6)
        ),
        
        "Ers_deployment_max": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="ERS deployment per lap max (kw)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(7)
        ),
        
        "Ers_harvest": (
            tk.Entry(
                main_window,
                font=("Arial", 11),
                width=5,
                background="#85FBFF",
            ),
            tk.Label(
                main_window,
                text="ERS harvest per lap (kw)",
                font=("Arial", 12),
                background="#FFFFFF"
            ),
            float(4)
        )
    }

    car_info_gap_x = 250
    car_info_gap_y = 40
    i = 0
    j = 0
    for key in car_data_dict.keys():
        car_data_dict[key][0].place(x=car_info_x + car_info_gap_x * j, y=car_info_y + 40 + car_info_gap_y * i)
        car_data_dict[key][1].place(x=70 + car_info_x + car_info_gap_x * j, y=car_info_y + 40 + car_info_gap_y * i)
        i += 1
        if i / 3 == 1 and j < 2:
            i = 0
            j += 1
            
    tyre_type_data_dict: dict[str, dict[str, Tuple [tk.Entry, tk.Label, float]]] = {
        "Soft": {
            "Base_time": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Base lap time",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(88.000)
            ),
            "Base_degradation": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Base tyre degradation",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.12)
            ),
            "Temperature": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Temperature",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(70)
            ),
            "Old_laps": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Tyre age",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                int(0)
            ),
            "Cliff_lap": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Cliff lap on",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(8)
            ),
            "Cliff_deg": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Cliff degradation",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.011)
            ),
            "Lock_up_time": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Time lost by lock-up",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.500)
            )
        },
        
        "Medium": {
            "Base_time": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Base lap time",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(90.000)
            ),
            "Base_degradation": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Base tyre degradation",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.099)
            ),
            "Temperature": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Temperature",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(70)
            ),
            "Old_laps": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Tyre age",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                int(0)
            ),
            "Cliff_lap": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Cliff lap on",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(12)
            ),
            "Cliff_deg": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Cliff degradation",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.010)
            ),
            "Lock_up_time": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Time lost by lock-up",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.500)
            )
        },
        
        "Hard": {
            "Base_time": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Base lap time",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(92.000)
            ),
            "Base_degradation": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Base tyre degradation",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.06)
            ),
            "Temperature": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Temperature",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(70)
            ),
            "Old_laps": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Tyre age",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                int(0)
            ),
            "Cliff_lap": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Cliff lap on",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(14)
            ),
            "Cliff_deg": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Cliff degradation",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.009)
            ),
            "Lock_up_time": (
                tk.Entry(
                    main_window,
                    font=("Arial", 11),
                    background="#85FBFF",
                    width=5
                ),
                tk.Label(
                    main_window,
                    text="Time lost by lock-up",
                    font=("Arial", 12),
                    background="#FFFFFF"
                ),
                float(0.500)
            )
        }
            
    }
    
    for tyre_type_key in tyre_type_data_dict.keys():
        for label_key in tyre_type_data_dict[tyre_type_key].keys():
            tyre_type_data_dict[tyre_type_key][label_key][0].place(x= tyre_type_position_x + gap_tyre_type_x * row,
                                                                   y= tyre_type_position_y + gap_tyre_type_y * col)
            tyre_type_data_dict[tyre_type_key][label_key][1].place(x= tyre_type_position_x + gap_tyre_type_x * row + 50,
                                                                   y= tyre_type_position_y + gap_tyre_type_y * col)
            col += 1
        col = 0
        row += 1
    
    def write_data_to_json_file():
        data: dict = {}
        data["Race_data"] = {}
        data["Car_data"] = {}
        for compound in tyres:
            data[compound] = {}
    
        for key in race_data_dict.keys():
            try:
                k = race_data_dict[key][0].get()
                if '.' in k:
                    data["Race_data"][key] = float(k)
                else:
                    data["Race_data"][key] = int(k)
            except Exception:
                data["Race_data"][key] = race_data_dict[key][2]
                
        for key in car_data_dict.keys():
            try:
                l = car_data_dict[key][0].get()
                data["Car_data"][key] = float(l)
            except ValueError:
                if len(l) != 0:
                    data["Car_data"][key] = l
                else:
                    data["Car_data"][key] = car_data_dict[key][2]
            except Exception:
                data["Car_data"][key] = car_data_dict[key][2]
        for compound in tyres:
            for key in tyre_type_data_dict[compound].keys():
                try:
                    k = tyre_type_data_dict[compound][key][0].get()
                    if '.' in k:
                        data[compound][key] = float(k)
                    else:
                        data[compound][key] = int(k)
                except Exception:
                    data[compound][key] = tyre_type_data_dict[compound][key][2]
        
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
            
        print("Data save successfully!")
        return
    
    # Input user check will be when you click calculate strategy
    def read_data_from_json_file():
        if os.path.getsize("config.json") == 0:
            print("File is empty")
            return
        
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for key in race_data_dict.keys():
            # How to insert values in the entry
            race_data_dict[key][0].delete(0, tk.END)
            race_data_dict[key][0].insert(0, str(data["Race_data"][key]))
        for key in car_data_dict.keys():
            car_data_dict[key][0].delete(0, tk.END)
            car_data_dict[key][0].insert(0, str(data["Car_data"][key]))
        for compound in tyres:
            for Key in tyre_type_data_dict[compound].keys():
                tyre_type_data_dict[compound][Key][0].delete(0, tk.END)
                tyre_type_data_dict[compound][Key][0].insert(0, str(data[compound][Key]))
        print("Data upload successfully!")
        
    def calculate_best_strategy():
        try:
            simulator = Race_Simulator(
                softT=Tyre(
                    name="Soft",
                    base_time=float(tyre_type_data_dict["Soft"]["Base_time"][0].get()),
                    base_degradation=float(tyre_type_data_dict["Soft"]["Base_degradation"][0].get()),
                    temperature=float(tyre_type_data_dict["Soft"]["Temperature"][0].get()),
                    old_laps=int(tyre_type_data_dict["Soft"]["Old_laps"][0].get()),
                    cliff_deg=float(tyre_type_data_dict["Soft"]["Cliff_deg"][0].get()),
                    cliff_lap=float(tyre_type_data_dict["Soft"]["Cliff_lap"][0].get()),
                    lockup_time=float(tyre_type_data_dict["Soft"]["Lock_up_time"][0].get())
                ),
                mediumT=Tyre(
                    name="Medium",
                    base_time=float(tyre_type_data_dict["Medium"]["Base_time"][0].get()),
                    base_degradation=float(tyre_type_data_dict["Medium"]["Base_degradation"][0].get()),
                    temperature=float(tyre_type_data_dict["Medium"]["Temperature"][0].get()),
                    old_laps=int(tyre_type_data_dict["Medium"]["Old_laps"][0].get()),
                    cliff_deg=float(tyre_type_data_dict["Medium"]["Cliff_deg"][0].get()),
                    cliff_lap=float(tyre_type_data_dict["Medium"]["Cliff_lap"][0].get()),
                    lockup_time=float(tyre_type_data_dict["Medium"]["Lock_up_time"][0].get())
                ),
                hardT=Tyre(
                    name="Hard",
                    base_time=float(tyre_type_data_dict["Hard"]["Base_time"][0].get()),
                    base_degradation=float(tyre_type_data_dict["Hard"]["Base_degradation"][0].get()),
                    temperature=float(tyre_type_data_dict["Hard"]["Temperature"][0].get()),
                    old_laps=int(tyre_type_data_dict["Hard"]["Old_laps"][0].get()),
                    cliff_deg=float(tyre_type_data_dict["Hard"]["Cliff_deg"][0].get()),
                    cliff_lap=float(tyre_type_data_dict["Hard"]["Cliff_lap"][0].get()),
                    lockup_time=float(tyre_type_data_dict["Hard"]["Lock_up_time"][0].get())
                ),
                startT=Tyre(
                    name=starting_tyre_var.get(),
                    base_time=float(tyre_type_data_dict[starting_tyre_var.get()]["Base_time"][0].get()),
                    base_degradation=float(tyre_type_data_dict[starting_tyre_var.get()]["Base_degradation"][0].get()),
                    temperature=float(tyre_type_data_dict[starting_tyre_var.get()]["Temperature"][0].get()),
                    old_laps=int(tyre_type_data_dict[starting_tyre_var.get()]["Old_laps"][0].get()),
                    cliff_deg=float(tyre_type_data_dict[starting_tyre_var.get()]["Cliff_deg"][0].get()),
                    cliff_lap=float(tyre_type_data_dict[starting_tyre_var.get()]["Cliff_lap"][0].get()),
                    lockup_time=float(tyre_type_data_dict[starting_tyre_var.get()]["Lock_up_time"][0].get())
                ),
                race_info=Race_basic_information(
                    laps=int(race_data_dict["Race_laps"][0].get()),
                    pit_stops=int(race_data_dict["Pit_stops"][0].get()),
                    pit_loss=float(race_data_dict["Pit_loss"][0].get()),
                    coefficient_time_under_safety_car=float(race_data_dict["Coeff_safety_car"][0].get()),
                    safety_car_probability=float(race_data_dict["Safety_car_probability"][0].get()),
                    lockup_probability=float(race_data_dict["Lock_up_probability"][0].get()),
                    lockup_def_coefficient=float(race_data_dict["Lock_up_degradation"][0].get()),
                    time_lost_by_fuel_per_1kg_1lap=float(race_data_dict["Time_lost_by_fuel"][0].get()),
                    push_lift=float(race_data_dict["Push_lift_difference"][0].get()),
                    coefficien_pushing_after_pit_stop=float(race_data_dict["Push_after_pit_stop"][0].get())
                ),
                car_track=Car(
                    car_id=car_data_dict["Driver_number"][0].get(),
                    team=car_data_dict["Team_name"][0].get(),
                    driver=car_data_dict["Driver_name"][0].get(),
                    fuel_mass_kg=float(car_data_dict["Fuel_mass"][0].get()),
                    fuel_max=float(car_data_dict["Fuel_max"][0].get()),
                    fuel_burn_kg_per_lap=float(car_data_dict["Fuel_burn_per_lap"][0].get()),
                    ers_store_max_kw=float(car_data_dict["Ers_store_max"][0].get()),
                    ers_deploy_max_kw=float(car_data_dict["Ers_deployment_max"][0].get()),
                    ers_deploy_per_lap_kw=float(car_data_dict["Ers_deployment_max"][0].get()),
                    ers_harvest_kw=float(car_data_dict["Ers_harvest"][0].get())
                ),
                number_top_strategies=5
            )
            simulator.calculate_best_strategy()
            print("Successfully found the best strategy!")
            simulator.show_plots(True)
        except Exception as e:
            print("Error with finding best strategy: ", end="")
            print(e)
        return
    
    write_data_button = tk.Button(
        main_window,
        text="Write Data to file",
        font=("Arial", 14),
        background="#B9FFEE",
        command=write_data_to_json_file
    )
    write_data_button.place(x=880, y=500)
    
    write_data_button = tk.Button(
        main_window,
        text="Input data from file",
        font=("Arial", 14),
        background="#EFB9FF",
        command=read_data_from_json_file
    )
    write_data_button.place(x=880, y=550)
    
    start_calculating_best_strategy = tk.Button(
        main_window,
        text="Find best strategy",
        font=("Arial", 14),
        background="#FFAADE",
        command=calculate_best_strategy
    )
    start_calculating_best_strategy.place(x=880, y=600)
    
    main_window.mainloop()

if __name__ == "__main__":
    main()