
import random
import copy
import matplotlib.pyplot as plt
from typing import List, Tuple


""" 
1. Add sc pit time to the function calculating the best strategy. - DONE
2.1 Add to the funtion to be depended by fuel consumption for time laps - Done
    Add checking if fuel is enough for 1 or laps-left, if not return - DONE
    Add lift and coast coefficient too then it reduces the fuel coast but it increases the laptime - DONE
2.2 Add tyre temperature and how it changes lap time - In progress
3. Add class for different tracks:
    - corners
        + slow
        + medium
        + high
"""

"""
Classes:
    Race_Information
    Tyre
    ERS
    Car
    Race_Simulation

"""

class Race_basic_information:
    laps: int
    pit_stops: int
    coefficient_time_under_safety_car: float
    pit_loss: float
    pit_loss_safety_car: float

    safety_car_probability: float
    safety_car_laps: list [bool]

    lockup_probability: float
    lockup_def_coefficient: float
    lockup_laps: list [bool]

    push_lift_coast: list [float]
    coefficien_pushing_after_pit_stop: float

    time_lost_by_fuel_per_1kg_1lap: float
    
    def __init__(self, laps: int, pit_stops: int, coefficient_time_under_safety_car: float = 0.65, pit_loss: float = 23.00, safety_car_probability: float = 0.03,
        lockup_probability: float = 0.06, lockup_def_coefficient: float = 1.1, coefficien_pushing_after_pit_stop: float = 1.15,
        time_lost_by_fuel_per_1kg_1lap: float = 0.032, push_lift:float = 0.012):
        
        self.laps = laps
        self.pit_stops = pit_stops
        self.coefficient_time_under_safety_car = coefficient_time_under_safety_car
        self.pit_loss = pit_loss
        self.pit_loss_safety_car = pit_loss * coefficient_time_under_safety_car
        self.safety_car_probability = safety_car_probability
        self.lockup_probability = lockup_probability
        self.lockup_def_coefficient = lockup_def_coefficient
        self.coefficien_pushing_after_pit_stop = coefficien_pushing_after_pit_stop
        self.time_lost_by_fuel_per_1kg_1lap = time_lost_by_fuel_per_1kg_1lap
        self.lockup_laps = []
        self.safety_car_laps = []
        self.push_lift_coast = []
        
        def init_sc_lockup_push(push_lift: float):
            self.lockup_laps = []
            self.safety_car_laps = []
            self.push_lift_coast = []
            for i in range(0, self.laps):
                random_number = random.uniform(0, 1)
                self.lockup_laps.append(bool (self.lockup_probability > random_number))
                
                random_number = random.uniform(0, 1)
                if self.was_safety_car_soon(i):
                    self.safety_car_laps.append(False)
                else:
                    self.safety_car_laps.append(bool (self.safety_car_probability > random_number))        
                
                random_number = 0
                while not (random_number >= (1 - 3 * push_lift) and random_number <= (1 + 3 * push_lift)):
                    random_number = random.gauss(1, push_lift)
                self.push_lift_coast.append(random_number)
                
        init_sc_lockup_push(push_lift)
    
    def check_data_validation(self):
        if self.laps < 1:
            raise Exception("Invalid lap number!")
        if self.pit_stops < 1:
            raise Exception("Invalid pitstops!")
        if self.pit_loss < 0:
            raise Exception("Invalid pit loss time!")
        if self.pit_loss_safety_car < 0 or self.pit_loss_safety_car > 1:
            raise Exception("Invalid safety car coefficient!")
        if self.safety_car_probability < 0 or self.safety_car_probability > 1:
            raise Exception("Invalid safety car probability!")
        if self.lockup_probability < 0 or self.lockup_probability > 1:
            raise Exception("Invalid lock-up probability!")
        if self.lockup_def_coefficient < 1:
            raise Exception("Invalid lock-up degradation coefficient!")
        if self.push_lift_coast < 0 or self.push_lift_coast > 0.1:
            raise Exception("Inavil push-lift-coast coefficient!")
        if self.time_lost_by_fuel_per_1kg_1lap < 0:
            raise Exception("Invalid time lost by fuel!")
    
    def was_safety_car_soon(self, curr_lap: int):
        i = random.randint(2, 4)
        index = curr_lap
        while i > 0 and index > 0:
            if self.safety_car_laps[index - 1]:
                return True
            i -= 1
            index -= 1
        return False
    
    def set_lock_up_laps(self, lockups: List[bool]):
        assert lockups.__len__() == self.laps
        ind = 0
        for element in lockups:
            assert element == True or element == False
            self.lockup_laps[ind] = element
            ind += 1
        return
            
    def set_safety_car_for_laps(self, sc_checks: List[bool]):
        assert sc_checks.__len__() == self.laps
        ind = 0
        for element in sc_checks:
            assert element == True or element == False
            self.safety_car_laps[ind] = element
            ind += 1
        return
            
            
class TyreType:
    Wet = "Full Wet"
    Inter = "Intermediate"
    Soft = "Soft"
    Medium = "Medium"
    Hard = "Hard"
    
    @staticmethod
    def is_valid_tyre(check: str):
        return check == TyreType.Wet or check == TyreType.Inter or check == TyreType.Soft or check == TyreType.Medium or check == TyreType.Hard


class Tyre:
    name: str
    base_time: float
    base_degradation: float
    changing_deg: float
    
    old_laps: int
    time_with_old_laps: float
    
    cliff_lap: int
    cliff_deg: float
    
    lockup_time: float
    lockup_lap: list[int]
    
    temperature: float
    
    def __init__(self, name, base_time, base_degradation = -1, temperature = 70,
                 old_laps=0,cliff_lap=0, cliff_deg=0.0,
                 lockup_time=0.0):
        self.lockup_lap = []
        assert TyreType.is_valid_tyre(name)
        if base_degradation < 0:
            match name:
                case TyreType.Soft:
                    self.base_degradation = 0.0011 * base_time
                case TyreType.Medium:
                    self.base_degradation = 0.0009 * base_time
                case TyreType.Hard:
                    self.base_degradation = 0.0006 * base_time
        self.name = name
        self.base_time = base_time
        self.base_degradation = base_degradation
        self.changing_deg = base_degradation
        self.old_laps = old_laps
        self.cliff_lap = cliff_lap
        self.cliff_deg = cliff_deg
        self.time_with_old_laps = self.base_time
        for _ in range(1, old_laps):
            self.change_tyre_age(1)
        self.lockup_time = lockup_time
        self.temperature = temperature
    
    def check_data_valid(self):
        if self.base_time < 0:
            raise Exception("Invalid base time for: " + self.name)
        if self.base_degradation < 0:
            raise Exception("Invalid degradation for: " + self.name)
        if self.old_laps < 0:
            raise Exception("Invalid tyre age for: " + self.name)
        if self.cliff_lap < 0:
            raise Exception("Invalid cliff lap starting for: " + self.name)
        if self.cliff_deg < 0:
            raise Exception("Invalid cliff degradation for: " + self.cliff_deg)
        if self.lockup_time < 0:
            raise Exception("Invalid lock-up lost time for: " + self.name)
        if self.temperature < 0:
            raise Exception("Invalid temperature for: " + self.name)
        return True

    def change_tyre_age(self, lap: int, coeff_push_calm: float = 1):
        assert lap == 1 or lap == -1 or lap == 0
        if lap == 0:
            self.time_with_old_laps = self.base_time
            return
        
        temp = 0
        if lap == 1:
            if self.old_laps >= self.cliff_lap:
                temp += self.cliff_deg
        else:
            if self.old_laps > self.cliff_lap:
                temp -= self.cliff_deg
        
        self.old_laps += lap
        self.time_with_old_laps += coeff_push_calm * self.changing_deg * lap + temp
        return
    
    #only lockup time is applied to the lap, deg starts from next lap
    def apply_lockup(self, lap_: int, race_info: Race_basic_information) -> float:
        self.lockup_lap.append(lap_)
        self.changing_deg *= race_info.lockup_def_coefficient
        return self.lockup_time

    def misapply_lockup(self, race_info: Race_basic_information):
        self.changing_deg /= race_info.lockup_def_coefficient
        self.lockup_lap.pop()
        return 
    
    def was_pitstop_soon(self) -> bool:
        return self.old_laps == 0 or self.old_laps == 1
    
    
class laps_pitstops_list:
    time: float
    laps: List [Tuple[int, Tyre, float]] # int = lap for pit, str = tyre_type, float = stint time 
    
    def __init__(self, t: float, l:list):
        self.laps = l.copy()
        self.time = t
        
        

class fuel_mode:
    Lean = "Lean"
    Standard = "Standard"
    Rich = "Rich"

class fuel_car:
    fuel_mass_kg: float
    fuel_max: float
    fuel_min: float
    fuel_burn_kg_per_lap: float
    fuel_mod: str
    
    def __init__(self, fuel_mass_kg: float = 120, fuel_max: float = 120, fuel_burn_kg_per_lap: float = 1):
        assert fuel_mass_kg <= fuel_max and fuel_mass_kg >= 1
        self.fuel_mass_kg = fuel_mass_kg
        self.fuel_max = fuel_max
        self.fuel_min = 1
        self.fuel_burn_kg_per_lap = fuel_burn_kg_per_lap
        self.fuel_mod = fuel_mode.Standard
        
    def check_data_valid(self):
        if self.fuel_max < 0:
            raise Exception("Invalid max fuel!")
        if self.fuel_mass_kg < 0 or self.fuel_mass_kg > self.fuel_max:
            raise Exception("Invalid fuel mass!")
        if self.fuel_burn_kg_per_lap < 0:
            raise Exception("invalid fuel burn!")
        return True
        
    def consumption_coeff(self):
        match self.fuel_mod:
            case "Lean":
                return 0.94
            case "Standard":
                return 1.0
            case "Rich":
                return 1.07
            case _:
                print("Problem with fuel mode!")
                assert False
                
    def check_consume_fuel(self, for_laps: int = 1, coefficient_push_or_lift_coast: List[float] | None = None, coef: str = "x") -> bool:
        if coefficient_push_or_lift_coast is None:
            coefficient_push_or_lift_coast = [1.0]
        assert coefficient_push_or_lift_coast.__len__() == abs(for_laps) and for_laps != 0
        check = 0
        if coef == "x":
            coef = self.fuel_mod
        coefficient = 0
        match coef:
            case "Lean":
                coefficient = 0.94
            case "Standard":
                coefficient = 1.0
            case "Rich":
                coefficient = 1.07
        mark = 1
        if(for_laps < 0):
            mark = -1
        
        for i in coefficient_push_or_lift_coast:
            assert i >= 0.5 and i <= 1.5
            check += self.fuel_burn_kg_per_lap * i * coefficient * mark
        
        check = round(self.fuel_mass_kg - check, 3)
        #print("CHECK:")
        #print(check)
        #print(coef)
        return bool (self.fuel_min <= check and check <= self.fuel_max)
    
    def consume_fuel(self, for_laps: int = 1, coefficient_push_or_lift_coast: List[float] | None = None) -> bool:
        if coefficient_push_or_lift_coast is None:
            coefficient_push_or_lift_coast = [1.0]
        assert ((for_laps == 1 or for_laps == -1) and coefficient_push_or_lift_coast.__len__() == 1) # Just for info what is happening
        if for_laps == 0:
            return 0
        
        # In future to be replaced with if and change to the function when is used to try and reduce fuel-mod otherwise just go back to recursion
        assert self.check_consume_fuel(for_laps, coefficient_push_or_lift_coast, self.fuel_mod)
        check = 0
        
        mark = 1
        if(for_laps < 0):
            mark = -1
        
        for i in coefficient_push_or_lift_coast:
            check += self.fuel_burn_kg_per_lap * i * self.consumption_coeff() * mark
            
        to_return = check
        self.fuel_mass_kg = self.fuel_mass_kg - check
        return to_return
    
    def change_fuel_mode_to(self, to: str):
        assert to in ("Lean", "Standard", "Rich")
        match to:
            case "Lean":
                self.fuel_mod = fuel_mode.Lean
            case "Standard":
                self.fuel_mod = fuel_mode.Standard
            case "Rich":
                self.fuel_mod = fuel_mode.Rich
                
    def get_time_from_fuel(self, race_info: Race_basic_information):
        return race_info.time_lost_by_fuel_per_1kg_1lap * self.fuel_mass_kg
    
    def get_coeff_for_engine_power_by_fuel(self):
         match self.fuel_mod:
            case "Lean":
                return 1.0018
            case "Standard":
                return 1.0
            case "Rich":
                return 0.9987
            case _:
                print("Problem with fuel mode!")
                assert False 



#_________________________________________________________ Needs completness_________________________________________________
#      Have to change what the class has, this is WRONG
class ers_mode:
    None_ = "None"
    Medium_ = "Medium"
    Hotlap_ = "Hotlap"
    Overtake = "Overtake"
    
    
class ers_car:
    ers_store_kw: float
    ers_store_max_kw: float
    #     1kw = 1000 kj
    ers_deploy_per_lap_kw: float
    ers_deploy_max_kw: float
    ers_harvest_kw: float
    
    ers_mod: str
    
    def __init__(self, ers_store_max_kw: float = 4000, ers_deploy_per_lap_kw: float = 10, ers_deploy_max_kw: float = 6, ers_harvest_kw: float = 4):
        self.ers_store_max_kw = ers_store_max_kw
        self.ers_store_kw = ers_store_max_kw
        self.ers_deploy_per_lap_kw = ers_deploy_per_lap_kw
        self.ers_deploy_max_kw = ers_deploy_max_kw
        self.ers_harvest_kw = ers_harvest_kw
        self.ers_mod = ers_mode.Medium_
        
    def check_data_valid(self):
        if self.ers_store_max_kw < 0:
            raise Exception("Invalid ERS max store!")
        if self.ers_store_kw < 0 or self.ers_store_kw > self.ers_store_max_kw:
            raise Exception("Invalid ERS current store!")
        if self.ers_deploy_max_kw < 0:
            raise Exception("Invalid ERS deployment current!")
        if self.ers_deploy_per_lap_kw < 0:
            raise Exception("Invalid ERS deploymnet max per lap!")
        if self.ers_harvest_kw < 0:
            raise Exception("Invalid ERS harvestment!")
        return True
        
    def mode_deploy_coefficient(self) -> float:
        match self.ers_mod:
            case ers_mode.None_:
                return 0.2
            case ers_mode.Medium_:
                return 0.8
            case ers_mode.Hotlap_:
                return 1.0
            case ers_mode.Overtake:
                return 1.2
        assert False
        
    def mode_harvest_coefficient(self) -> float:
        match self.ers_mod:
            case ers_mode.None_:
                return 1.2
            case ers_mode.Medium_:
                return 1.0
            case ers_mode.Hotlap_:
                return 0.8
            case ers_mode.Overtake:
                return 0.65
        assert False
    
    def change_mod(self, to: str):
        match to:
            case "None":
                self.ers_mod = ers_mode.None_
            case "Medium":
                self.ers_mod = ers_mode.Medium_
            case "Hotlap":
                self.ers_mod = ers_mode.Hotlap_
            case "Overtake":
                self.ers_mod = ers_mode.Overtake
                
    def do_lap_using_ers(self, lap_time_seconds: float, push_lift_coef: float, tyre_current: Tyre,
                         lap_number: int, race_information: Race_basic_information) -> Tuple[float, float, float, float, str]:
        ers_state_before_lap = self.ers_mod
        
        flag_pit_stop = tyre_current.was_pitstop_soon()
        if flag_pit_stop:
            self.change_mod(ers_mode.Hotlap_)
        
        flag_safety_car = race_information.was_safety_car_soon(lap_number)
        if flag_safety_car:
            self.change_mod(ers_mode.None_)
        
        changed_push_lift_coef = pow(push_lift_coef, 5)
        
        stored_ers_before_lap = self.ers_store_kw
        # 1kw = 1000 kj
        our_deplayed_desired = self.ers_deploy_per_lap_kw * lap_time_seconds * self.mode_deploy_coefficient() * changed_push_lift_coef
        per_lap_cap_kj = self.ers_deploy_max_kw * lap_time_seconds
        desired_deploy_kj = min(our_deplayed_desired, per_lap_cap_kj, self.ers_store_kw)
        deployed_kj = max(desired_deploy_kj, 0.0)

        self.ers_store_kw -= deployed_kj
        
        push_harvest_factor = max(0.2, min(2.0, 2.0 - changed_push_lift_coef))
        
        base_harvest_kj = self.ers_harvest_kw * lap_time_seconds * self.mode_harvest_coefficient() * push_harvest_factor
        capacity_left_kj = self.ers_store_max_kw - self.ers_store_kw
        harvested_kj = max(0.0, min(base_harvest_kj, capacity_left_kj))

        self.ers_store_kw += harvested_kj
        
        ers_mod_for_the_lap = self.ers_mod
        if flag_safety_car or flag_pit_stop:
            self.change_mod(ers_state_before_lap)
        
        return (0.07 * deployed_kj / 1000, stored_ers_before_lap, deployed_kj, harvested_kj, ers_mod_for_the_lap)
        
    def reverse_ers_from_lap(self, deployed_energy: float, harvested_energy: float):
        self.ers_store_kw += (deployed_energy - harvested_energy)
        self.ers_store_kw = min(self.ers_store_kw, self.ers_store_max_kw)
        
#____________________________________________________________________ Needs completness _________________________________________________

       
def is_ers_mode(check: str):
    return (check == ers_mode.None_ or check == ers_mode.Medium_ or check == ers_mode.Overtake or check == ers_mode.Hotlap_)

def is_fuel_mode(check: str):
    return (check == fuel_mode.Lean or check == fuel_mode.Standard or check == fuel_mode.Rich)
   


class Car:
    car_id: str
    team: str
    driver: str
    
    fuel: fuel_car
    
    ers: ers_car
    
    def __init__(self, car_id: str, team: str, driver: str, fuel_mass_kg: float | None, fuel_max: float | None, fuel_burn_kg_per_lap: float | None, 
                 ers_store_max_kw: float | None, ers_deploy_per_lap_kw: float | None, ers_deploy_max_kw: float | None, ers_harvest_kw: float | None):
        self.car_id = car_id
        self.team = team
        self.driver = driver
        self.fuel = fuel_car(fuel_mass_kg, fuel_max, fuel_burn_kg_per_lap)
        self.ers = ers_car(ers_store_max_kw, ers_deploy_per_lap_kw, ers_deploy_max_kw, ers_harvest_kw)
    
    def chech_data_valid(self):
        return self.fuel.check_data_valid() and self.ers.check_data_valid()
     
class lap_each_info:
    lap_time: list[float]
    delta_to_last_lap: list[float]
    tyre_degradation_current_lap: list[float]
    
    fuel_burn: list[float]
    fuel_mode: list[str]
    lift_and_coast_coef: list[float]
    
    ers_start_of_lap: list[float]
    ers_deployed_lap: list[float]
    ers_harvested_lap: list[float]
    ers_time_gained: list[float]
    ers_mod_used: list[str]
    
    size_of_list: int
    
    
    def __init__(self, laps_: int):
        assert laps_ > 1
        self.size_of_list = laps_
        
        self.lap_time = [None] * laps_
        self.delta_to_last_lap = [None] * laps_
        self.tyre_degradation_current_lap = [None] * laps_
        
        self.fuel_burn = [None] * laps_
        self.fuel_mode = [None] * laps_
        self.lift_and_coast_coef = [None] * laps_
        
        self.ers_start_of_lap = [None] * laps_
        self.ers_deployed_lap = [None] * laps_
        self.ers_harvested_lap = [None] * laps_
        self.ers_time_gained = [None] * laps_
        self.ers_mod_used = [None] * laps_
        
        
    def calculate_delta_to_prev_lap(self, current_lap: int):
        assert (self.lap_time[current_lap - 1] is not None)
        if current_lap == 1:
            self.delta_to_last_lap[current_lap - 1] = 0
            return
        
        self.delta_to_last_lap[current_lap - 1] = self.lap_time[current_lap - 1] - self.lap_time[current_lap - 2]
        return
        
    def add_lap_info(self, lap_number: int, lap_time: float, tyre_degradation_: float, 
                     fuel_burn: float, fuel_mode: str, ers_start_MJ: float, ers_deployment: float,
                     ers_harvested: float, ers_time_gain:float, ers_mode: str, lift_coast: float = 1):

        assert(0 < lap_number and lap_number <= self.size_of_list and is_ers_mode(ers_mode) and is_fuel_mode(fuel_mode) and self.lap_time[lap_number - 1] is None)
        self.lap_time[lap_number - 1] = lap_time
        self.calculate_delta_to_prev_lap(lap_number)
        self.tyre_degradation_current_lap[lap_number - 1] = tyre_degradation_
        
        self.fuel_burn[lap_number - 1] = fuel_burn
        self.fuel_mode[lap_number - 1] = fuel_mode
        self.lift_and_coast_coef[lap_number - 1] = lift_coast
        
        self.ers_start_of_lap[lap_number - 1] = ers_start_MJ
        self.ers_deployed_lap[lap_number - 1] = ers_deployment
        self.ers_harvested_lap[lap_number - 1] = ers_harvested
        self.ers_time_gained[lap_number - 1] = ers_time_gain
        self.ers_mod_used[lap_number - 1] = ers_mode
        
        
        
    def delete_lap_info(self, lap_number: int):
        assert(0 < lap_number and lap_number <= self.size_of_list)
        assert(self.lap_time[lap_number - 1] is not None)
            
        self.lap_time[lap_number - 1] = None
        self.delta_to_last_lap[lap_number - 1] = None
        self.tyre_degradation_current_lap[lap_number - 1] = None
        
        self.fuel_burn[lap_number - 1] = None
        self.fuel_mode[lap_number - 1] = None
        self.lift_and_coast_coef[lap_number - 1] = None
        
        self.ers_start_of_lap[lap_number - 1] = None
        self.ers_deployed_lap[lap_number - 1] = None
        self.ers_harvested_lap[lap_number - 1] = None
        self.ers_time_gained[lap_number - 1] = None
        self.ers_mod_used[lap_number - 1] = None
        
        
        
    def change_lap_time(self, lap_number: int, time: float):
        assert(0 < lap_number and lap_number <= self.size_of_list)
        assert(self.lap_time[lap_number - 1] is not None)
        
        self.lap_time[lap_number - 1] = time
        if lap_number != 1:
            self.delta_to_last_lap[lap_number - 1] = self.lap_time[lap_number - 1] - self.lap_time[lap_number - 2]
        else:
            self.delta_to_last_lap[lap_number - 1] = 0
        
    
class Race_Simulator:
    counter = 0
    
    soft_tyre: Tyre
    medium_tyre: Tyre
    hard_tyre: Tyre
    starting_tyre: Tyre
    
    car_on_track: Car
    
    best_strategy: laps_pitstops_list
    best_strategy_each_lap_info: lap_each_info
    
    top_n_strategies: List[laps_pitstops_list] # Last element is always None
    
    fastest_possible_lap: float
    
    race_all_information: Race_basic_information
    
    def __init__(self, softT: Tyre, mediumT: Tyre, hardT: Tyre, startT: Tyre, car_track: Car, race_info: Race_basic_information, number_top_strategies: int):
        assert softT.name == TyreType.Soft and mediumT.name == TyreType.Medium and hardT.name == TyreType.Hard and number_top_strategies >= 1
        self.soft_tyre = copy.deepcopy(softT)
        self.medium_tyre = copy.deepcopy(mediumT)
        self.hard_tyre = copy.deepcopy(hardT)
        self.starting_tyre = copy.deepcopy(startT)
        self.car_on_track = copy.deepcopy(car_track)
        self.race_all_information = copy.deepcopy(race_info)
        
        self.fastest_possible_lap = min(softT.base_time, mediumT.base_time, hardT.base_time)
        
        self.best_strategy = laps_pitstops_list(float("inf"), [(0, startT, 0.0)])
        
        self.best_strategy_each_lap_info = lap_each_info(self.race_all_information.laps)
        
        self.top_n_strategies = [None] * (number_top_strategies + 1)
    
    def check_data_validation(self):
        tyres_check: bool = self.soft_tyre.check_data_valid() and self.medium_tyre.check_data_valid() and self.hard_tyre.check_data_valid()
        return tyres_check and self.car_on_track.chech_data_valid()
    
    def clear_best_strategy_info(self):
        self.best_strategy = laps_pitstops_list(float("inf"), [(0, self.starting_tyre, 0.0)])
        
        self.best_strategy_each_lap_info = lap_each_info(self.race_all_information.laps)
        
        size = self.top_n_strategies.__len__()
        self.top_n_strategies = [None] * (size)
        
    def change_starting_tyre(self, starting_tyre_name: str):
        assert TyreType.is_valid_tyre(starting_tyre_name)
        match starting_tyre_name:
            case TyreType.Soft:
                self.starting_tyre = copy.deepcopy(self.soft_tyre)
            case TyreType.Medium:
                self.starting_tyre = copy.deepcopy(self.medium_tyre)
            case TyreType.Hard:
                self.starting_tyre = copy.deepcopy(self.hard_tyre)
        return
            
    def set_lockup_laps(self, lockuplaps: List[bool]):
        self.race_all_information.set_lock_up_laps(lockuplaps)
        return
    
    def set_safety_car_laps(self, sc_on_laps: List[bool]):
        self.race_all_information.set_safety_car_for_laps(sc_on_laps)
        return
    
    def calculate_best_strategy(self):
        def are_same_tyres(listed: List[Tuple[int, TyreType]]):
            length = listed.__len__()
            if length == 1:
                return True
            i = 0
            flag = 1
            while i < length - 1 and flag == 1:
                if listed[i][1] != listed[i + 1][1]:
                    flag = 0
                i += 1
            return flag
        
        def add_strategy(to_add: laps_pitstops_list):
            size = self.top_n_strategies.__len__()
            assert self.top_n_strategies[size - 1] is None
            if self.top_n_strategies[0] is None:
                self.top_n_strategies[0] = copy.deepcopy(to_add)
                return
            
            index = size - 2
            while self.top_n_strategies[index] is None:
                index -= 1
                
            while index >= 0  and to_add.time < self.top_n_strategies[index].time:
                self.top_n_strategies[index + 1] = copy.deepcopy(self.top_n_strategies[index])
                index -= 1
            self.top_n_strategies[index + 1] = copy.deepcopy(to_add)
            self.top_n_strategies[size - 1] = None
            return
        
        def pit_tyre_helper(are_same_previous_tyre: bool, this__and_next_tyre_same: bool, how_many_laps_left: bool):
            if are_same_previous_tyre == 1:
                if this__and_next_tyre_same == 1:
                    return False
                else:
                    if how_many_laps_left == 1:
                        return False
                    else:
                        return True
            else:
                if how_many_laps_left == 1:
                    return False
                else:
                    return True
                
        def get_push_lift_coefficient(current_lap: int, current_tyre: Tyre):
            assert current_lap > 0 and current_lap <= self.race_all_information.laps
            
            if self.race_all_information.was_safety_car_soon(current_lap):
                return self.race_all_information.coefficient_time_under_safety_car
            
            if current_tyre.was_pitstop_soon():
                return self.race_all_information.coefficien_pushing_after_pit_stop
            
            return self.race_all_information.push_lift_coast[current_lap - 1]
        
        def my_calc_best_strategy(car: Car, tyre: Tyre, laps_left: int, pit_stop_left: int,
                              current_strat: laps_pitstops_list, temporary_lap_each_info: lap_each_info):
            Race_Simulator.counter += 1
            # Finished all laps: evaluate
            if current_strat.time > self.best_strategy.time:
                return 
            
            if laps_left <= 0:
                if (pit_stop_left != self.race_all_information.pit_stops and current_strat.time <= self.best_strategy.time or
                    (current_strat.time == self.best_strategy.time and len(current_strat.laps) < len(self.best_strategy.laps))):
                    # Add tyres time to the last stint
                    sum_time_stint = current_strat.time
                    for _, _, C in current_strat.laps:
                        sum_time_stint -= C
                        
                    sum_time_stint = round(sum_time_stint, 3)
                    A, B, _ = current_strat.laps[current_strat.laps.__len__() - 1]
                    current_strat.laps[current_strat.laps.__len__() - 1] = (A, B, sum_time_stint)
                    
                    # Update the best strategy
                    self.best_strategy = copy.deepcopy(current_strat)
                    
                    # Add to the top strategies
                    add_strategy(self.best_strategy)
                    
                    # Update each lap info
                    self.best_strategy_each_lap_info = copy.deepcopy(temporary_lap_each_info)
                    
                    # Redo current strategy
                    current_strat.laps[current_strat.laps.__len__() - 1] = (A, B, 0.0)
                    
                # Go back
                return

            # Exceeded pit budget: prune this branch
            
            if pit_stop_left < 0:
                return 
            
            # May be let it stay or no, will see, depends on fuel comsumption and how it changes laptime, so we dont cut the best strat by accident________
            #sum_to_check = min(Hard.base_degradation, Medium.base_degradation, Soft.base_degradation) * (laps_left * (laps_left - 1) / 2)
            sum_to_check = 0
            if self.fastest_possible_lap * laps_left + current_strat.time + sum_to_check >= self.best_strategy.time:
                return
            
            # When it gets more complex with pushing on laps -> burning more fuel -> may be useful __________________________________________________________
            #if not car.fuel.check_consume_fuel(laps_left, [0.9] * laps_left):
                #return
                
            # Get the push_or_lift_coast_coefficient with a function (which lap)
            # If number > 1 we want to be faster
            push_or_lift_coast_coefficient = get_push_lift_coefficient(self.race_all_information.laps - laps_left + 1, tyre)
            #print(push_or_lift_coast_coefficient)
            if not car.fuel.check_consume_fuel(1, [push_or_lift_coast_coefficient], car.fuel.fuel_mod):
                return
            
            # ---- SNAPSHOT before doing this lap
            time_before_lap = current_strat.time
            tyre_age_before_lap = tyre.old_laps
            laps_len_before_lap = len(current_strat.laps)
            
            # Run THIS lap on the current tyre (pit is at the end of lap) + possible lock-up + car changes
            time_this_lap = tyre.time_with_old_laps + car.fuel.get_time_from_fuel(self.race_all_information)
                    
            # ERS
            [time_gained_by_ers, ers_before_lap, deployed_ers_kw_this_lap,
             harvested_ers_kw_this_lap, ers_mod_for_this_lap] = car.ers.do_lap_using_ers(time_this_lap, push_or_lift_coast_coefficient, tyre,
                                                                                    self.race_all_information.laps - laps_left + 1, self.race_all_information)
            time_this_lap += time_gained_by_ers
            
            # Change lap time
            time_this_lap *= 1 / push_or_lift_coast_coefficient
            # Change lap time for fuel-burned due to lift&coast/push
            time_this_lap *= car.fuel.get_coeff_for_engine_power_by_fuel()

            # Fuel consume
            fuel_burned = car.fuel.consume_fuel(1, [push_or_lift_coast_coefficient])

            # Lock-ups check
            if self.race_all_information.lockup_laps[self.race_all_information.laps - laps_left]:
                time_this_lap += tyre.apply_lockup(tyre.old_laps, self.race_all_information)
            
            current_strat.time += time_this_lap
            
            # Update temporary lap list - need fix and changes a lot...
            temporary_lap_each_info.add_lap_info(self.race_all_information.laps - laps_left + 1, time_this_lap, tyre.changing_deg * push_or_lift_coast_coefficient,
                                                 fuel_burned, car.fuel.fuel_mod,
                                            ers_before_lap, deployed_ers_kw_this_lap, harvested_ers_kw_this_lap, time_gained_by_ers, ers_mod_for_this_lap,
                                            push_or_lift_coast_coefficient)
            
            tyre.change_tyre_age(1, push_or_lift_coast_coefficient)
            
            # Return to the Standart Fuel Mode
            #car.fuel.change_fuel_mode_to(fuel_mode.Standard)

        #---------------------------------------------- BRANCHES ----------------------------------------------

            # ---- Branch A: no pit at end of this lap
            # Use a copy of tyre OR restore afterwards. Here we’ll restore after exploring both branches.
            my_calc_best_strategy(car, tyre, laps_left - 1, pit_stop_left, current_strat, temporary_lap_each_info)

            # ---- Branch B: pit at end of this lap (if we still have pits)
            if pit_stop_left > 0:
                # snapshot around pit bookkeeping
                #time_before_pit = current_strat.time
                pit_time = 0
                if self.race_all_information.safety_car_laps[self.race_all_information.laps - laps_left]:
                    current_strat.time += self.race_all_information.pit_loss_safety_car
                    pit_time += self.race_all_information.pit_loss_safety_car
                else:
                    current_strat.time += self.race_all_information.pit_loss
                    pit_time += self.race_all_information.pit_loss
                    
                temporary_lap_each_info.change_lap_time(self.race_all_information.laps - laps_left + 1, time_this_lap + pit_time)

                # Try each compound after the stop
                for new_tyre in (
                    copy.deepcopy(self.hard_tyre),
                    copy.deepcopy(self.medium_tyre),
                    copy.deepcopy(self.soft_tyre),
                ):
                    if pit_tyre_helper(are_same_tyres(current_strat.laps), tyre.name == new_tyre.name, laps_left == 1):
                        # Set the stint time in the array
                        sum_time_stint = current_strat.time
                        if (pit_stop_left != self.race_all_information.pit_stops):
                            for _, _, C in current_strat.laps:
                                sum_time_stint -= C
                        
                        sum_time_stint = round(sum_time_stint, 3)
                        A, B, _ = current_strat.laps[current_strat.laps.__len__() - 1]
                        current_strat.laps[current_strat.laps.__len__() - 1] = (A, B, sum_time_stint)
                        
                        # New_tyre starts fresh after the pit; current_strat already includes this lap + pit 
                        current_strat.laps.append((self.race_all_information.laps - laps_left + 1, new_tyre, 0.0))  # 1-based lap number
                        my_calc_best_strategy(car, new_tyre, laps_left - 1, pit_stop_left - 1, current_strat, temporary_lap_each_info)
                        current_strat.laps.pop()
                        
                        # Return before pit
                        current_strat.laps[current_strat.laps.__len__() - 1] = (A, B, 0.0)
            
                
            # ---- BACKTRACK the effects of "this lap" so sibling calls above us see the original state
            current_strat.time = time_before_lap
            temporary_lap_each_info.delete_lap_info(self.race_all_information.laps - laps_left + 1)
            car.fuel.consume_fuel(-1, [push_or_lift_coast_coefficient])
            
            # Restore ers
            car.ers.reverse_ers_from_lap(deployed_ers_kw_this_lap, harvested_ers_kw_this_lap)
            
            # Restore tyre age (we mutated in-place)
            assert tyre_age_before_lap - tyre.old_laps == -1
            tyre.change_tyre_age(-1, push_or_lift_coast_coefficient)
            
            if self.race_all_information.lockup_laps[self.race_all_information.laps - laps_left]:
                tyre.misapply_lockup(self.race_all_information)
                
            # (laps length didn’t change here; we restored after pit. Keep for completeness.)
            assert len(current_strat.laps) == laps_len_before_lap
            return
        
        assert (self.best_strategy.time == float("inf"))
        temporary_strategy = laps_pitstops_list(0.0, [(0, self.starting_tyre, 0.0)])
        temporary_each_lap_info = lap_each_info(self.race_all_information.laps)
        new_car = copy.deepcopy(self.car_on_track)
        my_calc_best_strategy(new_car, copy.deepcopy(self.starting_tyre), copy.deepcopy(self.race_all_information.laps),
                                   copy.deepcopy(self.race_all_information.pit_stops), temporary_strategy, temporary_each_lap_info)


    def number_of_function_called(self):
        print(Race_Simulator.counter)
        return

    def print_lap_info_for_best_strategy(self, lap_number: int):
        a = lap_number - 1
        assert(0 < lap_number and lap_number <= self.race_all_information.laps and self.best_strategy_each_lap_info.lap_time[a] is not None)
        print("\n")
        print(f"Lap number: {lap_number} \n")
        print(f"Lap time: {self.best_strategy_each_lap_info.lap_time[a]:.3f} ")
        print(f"Delta to last lap: {self.best_strategy_each_lap_info.delta_to_last_lap[a]:.3f} ")
        print(f"Tyre degradation: {self.best_strategy_each_lap_info.tyre_degradation_current_lap[a]:.3f}")
        print(f"Fuel burned: {self.best_strategy_each_lap_info.fuel_burn[a]:.3f} ")
        print(f"Fuel mode: " + self.best_strategy_each_lap_info.fuel_mode[a])
        print(f"Lift and coast index: {self.best_strategy_each_lap_info.lift_and_coast_coef[a]:.3f} ")
        print(f"ERS start lap: {self.best_strategy_each_lap_info.ers_start_of_lap[a]:.3f} ")
        print(f"ERS deployed: {self.best_strategy_each_lap_info.ers_deployed_lap[a]:.3f} ")
        print(f"ERS harvested: {self.best_strategy_each_lap_info.ers_harvested_lap[a]:.3f} ")
        print(f"ERS time gained: {self.best_strategy_each_lap_info.ers_time_gained[a]:.3f} ")
        print(f"ERS mode: " + self.best_strategy_each_lap_info.ers_mod_used[a])
        print(f"Lock-up: {self.race_all_information.lockup_laps[a]} ")
        print(f"Safety car: {self.race_all_information.safety_car_laps[a]} ")
        assert self.best_strategy.laps.__len__() != 1
        if lap_number == 1:
            print(f"Pit: {bool(lap_number == self.best_strategy.laps[1][0])} ")
            print("Tyre type: " + self.best_strategy.laps[0][1])
            print("Stint time: No yet!")
        else:
            size = self.best_strategy.laps.__len__()
            if lap_number == self.race_all_information.laps:
                assert bool(lap_number != self.best_strategy.laps[size - 1][0])
                print(f"Pit: {bool(0)}")
                print("Tyre type: " + self.best_strategy.laps[size - 1][1])
                print(f"Stint time: {self.best_strategy.laps[size - 1][2]:.3f}")
            else:
                for index in range(0, size):
                    if lap_number <= self.best_strategy.laps[index][0]:
                        print(f"Pit: {bool(lap_number == self.best_strategy.laps[index][0])} ")
                        print("Tyre type: " + self.best_strategy.laps[index - 1][1])
                        if lap_number == self.best_strategy.laps[index][0]:
                            print(f"Stint time: {self.best_strategy.laps[index - 1][2]:.3f}")
                        else:
                            print("Stint time: No yet!")
                        break

        print("\n" * 2)
        
    def print_safety_car(self):
        size = self.race_all_information.safety_car_laps.__len__()
        sum = 0
        print("\n")
        for i in range(0, size):
            if self.race_all_information.safety_car_laps[i]:
                sum += 1
                print(f"safety_car: {i + 1}")
                
        if sum == 0:
            print("No safety cars! \n")

    def print_lock_ups(self):
        size = self.race_all_information.lockup_laps.__len__()
        sum = 0
        print("\n")
        for i in range(0, size):
            if self.race_all_information.lockup_laps[i]:
                sum += 1
                print(f"lock-up lap: {i + 1}")
                
        if sum == 0:
            print("No lock-ups! \n")
                
    def print_best_strategy(self):
        assert self.best_strategy.time != float("inf")
        print(f"Race time for best strategy: {self.best_strategy.time:.3f}")
        for pit_lap, pit_tyres, time_tyre in self.best_strategy.laps:
            print(f"Pit lap: {pit_lap}")
            print(f"Tyre: {pit_tyres.name}")
            print(f"Sting_time: {time_tyre:.3f} \n")
            
    def print_all_top_strategies(self):
        print("\n" * 2)
        if self.top_n_strategies[0] is None:
            print("No good strategies! \n")
            return
        ind = 1
        for i in self.top_n_strategies:
            if i is not None:
                print(f"Strategy number: {ind}")
                print(f"Race time: {i.time:.3f}")
                for pit_lap, pit_tyres, time_tyre in i.laps:
                    print(f"Pit lap: {pit_lap}")
                    print(f"Tyres: {pit_tyres.name}")
                    print(f"Sting_time: {time_tyre:.3f} \n")
            else:
                return
            ind += 1
            
    def print_n_top_strategies(self, number: int):
        size = self.top_n_strategies.__len__() - 1
        assert number > 0 and number <= size
        print("\n" * 2)
        if self.top_n_strategies[0] is None:
            print("No good strategies! \n")
            return
        
        for i in range(0, number):
            if self.top_n_strategies[i] is not None:
                print(f"Strategy number: {i + 1}")
                print(f"Race time: {self.top_n_strategies[i].time:.3f}")
                for pit_lap, pit_tyres, time_tyre in self.top_n_strategies[i].laps:
                    print(f"Pit lap: {pit_lap}")
                    print(f"Tyres: {pit_tyres}")
                    print(f"Sting_time: {time_tyre:.3f} \n")
                else:
                    return
            
    def print_push_lift_and_coast_coeff(self):
        ind = 1
        print("Push / lift and coast coefficients per laps")
        for i in self.race_all_information.push_lift_coast:
            print(f"Lap {ind}: {i:.3f}")
            ind += 1
    
    def print_all_different_strategies_with_pit_windows(self):
        def merge_two_full_strategies(in_array_elem: List[Tuple[str, Tuple[int, int]]], to_add_elem: List[Tuple[str, int]]):
            size = in_array_elem.__len__()
            assert size == to_add_elem.__len__()
            
            def combine_laps_pit_window(element: Tuple[str, Tuple[int, int]], to_add: int) -> Tuple[str, Tuple[int, int]]:
                if to_add < element[1][0]:
                    name, (_, close) = element
                    return (name, (to_add, close))
                if element[1][1] < to_add:
                    name, (open, _) = element
                    return (name, (open, to_add))
                return element
                
            for i in range(0, size):
                assert in_array_elem[i][0] == to_add_elem[i][0]
                in_array_elem[i] = combine_laps_pit_window(in_array_elem[i], to_add_elem[i][1])
            return
        
        def increase_number_strategies(array: List[List[Tuple[str, Tuple[int, int]]]], position: int, new_element: List[Tuple[str, int]]):
            if position != -1:
                merge_two_full_strategies(array[position], new_element)
            else:
                # position == -1
                size = new_element.__len__()
                for t in range(0, size):
                    tyre, lap = new_element[t]
                    new_element[t] = (tyre, (lap, lap))
                
                array.append(new_element)
            return
        
        def index_if_tyre_strategy_in_already(check_array: List[List[Tuple[str, Tuple[int, int]]]], new_element_to_check: List[Tuple[str, int]]) -> int:
            size = 0
            flag = True
            size_check_aray = check_array.__len__()
            if size_check_aray == 0:
                return -1
            for i in range(0, size_check_aray):
                size = new_element_to_check.__len__()
                if size == check_array[i].__len__():
                    flag = True
                    for index in range(0, size):
                        if check_array[i][index][0] != new_element_to_check[index][0]:
                            flag = False
                    if flag == True:
                        return i
            return -1
        
        
        
        gather_all_strategies: List[List[Tuple[Tyre, Tuple[int, int]]]]
        gather_all_strategies = []
        
        temp = copy.deepcopy(self.top_n_strategies)
        for i in range(0, temp.__len__()):
            if self.top_n_strategies[i] is not None:
                temp[i] = copy.deepcopy(self.top_n_strategies[i])
                length = temp[i].laps.__len__()
                for index in range (0, length):
                    A, B, _ = temp[i].laps[index]
                    temp[i].laps[index] = (B, A)
        
        temp.pop() # in top_n_strat last element is None
        size_of_all_strategies = temp.__len__()
        for i in range(0, size_of_all_strategies):
            position_new_elem = index_if_tyre_strategy_in_already(gather_all_strategies, temp[i].laps)
            increase_number_strategies(gather_all_strategies, position_new_elem, temp[i].laps)
            
        counter = 1
        for element in gather_all_strategies:
            print("\n" * 2)
            print(f"Strategy pit windows: {counter}")
            counter += 1
            for tyres in element:
                print(f"TyreL: {tyres[0].name}")
                print(f"Pit window: {tyres[1][0]} - {tyres[1][1]}")
        return
    # Use matplt to do that        
    def show_plots(self, lap_times: bool = False, delta_last_lap: bool = False, tyre_degrataion: bool = False,
                   fuel_burn: bool = False, fuel_mode: bool = False,
                   ers_start_of_lap: bool = False, ers_deployed_harvested: bool = False, ers_time_gained: bool = False, ers_mod: bool = False):
        
        def load_plt_for_lap_times():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("Lap time", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.lap_time, marker="o", color="#3816F8")
            plt.xlabel("Lap")
            plt.ylabel("Lap time (s)")
            plt.title("Lap times over race distance")
            plt.grid(True, "both", "both")
        def load_plt_for_delta_to_last_lap():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("Delta lap times", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.delta_to_last_lap, marker="o", color="#16A5F8")
            plt.xlabel("Lap")
            plt.ylabel("Delta time (s)")
            plt.title("Delta times over race distance")
            plt.grid(True, "both", "both")
        def load_tyre_degradation():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("Tyre degradation each lap", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.tyre_degradation_current_lap, marker="*", color="#F88316")
            plt.xlabel("Lap")
            plt.ylabel("Tyre deg (seconds)")
            plt.title("Tyre degradation over time")
            plt.grid(True, "both", "both")
        def load_plt_for_fuel_burn():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("Fuel burned", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.fuel_burn, marker="o", color="#4016F8")
            plt.xlabel("Lap")
            plt.ylabel("Fuel kg")
            plt.title("Fuel burned each lap")
            plt.grid(True, "both", "both")
        def load_plt_for_fuel_mode():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("Fuel mode", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.fuel_mode)
            plt.xlabel("Lap")
            plt.ylabel("Mode")
            plt.title("Fuel mode each lap")
            plt.grid(True, "both", "both")
        def load_plt_for_ers_start_of_lap():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("ERS store", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.ers_start_of_lap, marker="*", color="#EB9C0A")
            plt.xlabel("Lap")
            plt.ylabel("ERS kj")
            plt.title("ERS at starts of each lap")
            plt.grid(True, "both", "both")
        def load_plt_for_ers_deployed_harvested():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("ERS deplyed", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.ers_deployed_lap, marker="*", color="#16F834")
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.ers_harvested_lap, marker="*", color="#F82516")
            plt.xlabel("Lap")
            plt.ylabel("ERS kj")
            plt.title("ERS deployed/havested each lap")
            plt.grid(True, "both", "both")
        def load_plt_for_ers_time_gained():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("ERS boost", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.ers_time_gained, marker="+", color="#A7EB0A")
            plt.xlabel("Lap")
            plt.ylabel("Seconds")
            plt.title("ERS time gained each lap")
            plt.grid(True, "both", "both")
        def load_plt_for_ers_mod_used():
            laps_numbers = list(range(1, self.race_all_information.laps + 1))
            plt.figure("ERS mode", figsize=(12, 4))
            plt.plot(laps_numbers, self.best_strategy_each_lap_info.ers_mod_used)
            plt.xlabel("Lap")
            plt.ylabel("Mode")
            plt.gca().invert_yaxis()
            plt.title("ERS mode each lap")
            plt.grid(True, "both", "both")
            
        plt.close("all")
        if lap_times:
            load_plt_for_lap_times()
        if delta_last_lap:
            load_plt_for_delta_to_last_lap()
        if tyre_degrataion:
            load_tyre_degradation()
        if fuel_burn:
            load_plt_for_fuel_burn()
        if fuel_mode:
            load_plt_for_fuel_mode()
        if ers_start_of_lap:
            load_plt_for_ers_start_of_lap()
        if ers_deployed_harvested:
            load_plt_for_ers_deployed_harvested()
        if ers_time_gained:
            load_plt_for_ers_time_gained()
        if ers_mod:
            load_plt_for_ers_mod_used()
        plt.show()
            
        
    def get_lap_times(self):
        return self.best_strategy_each_lap_info.lap_time
        
    def get_delta_to_last_lap(self):
        return self.best_strategy_each_lap_info.delta_to_last_lap
        
    def get_fuel_burn(self):
        return self.best_strategy_each_lap_info.fuel_burn
        
    def get_fuel_mode(self):
        return self.best_strategy_each_lap_info.fuel_mode
        
    def get_ers_start_of_lap(self):
        return self.best_strategy_each_lap_info.ers_start_of_lap
        
    def get_ers_deplyer_harvested(self):
        return self.best_strategy_each_lap_info.ers_deployed_lap
        
    def get_ers_time_gained(self):
        return self.best_strategy_each_lap_info.ers_time_gained
        
    def get_ers_mod_used(self):
        return self.best_strategy_each_lap_info.ers_mod_used
    
    def get_push_lift_coast_coefficient(self):
        return self.race_all_information.push_lift_coast

if __name__ == "__main__":
    print("Yes")
    ''' 
    #random.seed(42)
    laps = 100
    pit_stops = 2
    coefficient_time_under_safety_car = 0.65
    pit_loss = 23.000
    
    safety_car_probability = 0.0

    lockup_probability = 0.0
    lockup_def_coefficient = 1.4

    coefficien_pushing_after_pit_stop = 1.012

    time_lost_by_fuel_per_1kg_1lap = 0.032

    push_lift = 0.012
    
    top_strategies_number = 1

    Hard = Tyre(name=TyreType.Hard,
        base_time= 91.5,
        base_degradation= 0.06,
        temperature= 70,
        old_laps= 0,
        cliff_lap= 25,
        cliff_deg= 0.11,
        lockup_time= 0.02)

    Medium = Tyre(name=TyreType.Medium,
        base_time= 90.0,
        base_degradation= 0.08,
        temperature= 70,
        old_laps= 0,
        cliff_lap= 15,
        cliff_deg= 0.15,
        lockup_time= 0.04)

    Soft = Tyre(name=TyreType.Soft,
        base_time= 88.5,
        base_degradation= 0.12,
        temperature= 70,
        old_laps= 0,
        cliff_lap= 7,
        cliff_deg= 0.21,
        lockup_time= 0.09)

    Test = Tyre(name=TyreType.Soft,
        base_time= 88.5,
        base_degradation= 0.08,
        temperature= 70,
        old_laps= 0,
        cliff_lap= 7,
        cliff_deg= 0.21,
        lockup_time= 0.09)


    Car_on_track = Car(car_id = "45",
                team= "RedBull",
                driver= "Max Verstappen",
                
                fuel_mass_kg= 96.5,
                fuel_max= 120,
                fuel_burn_kg_per_lap= 0.95,
                
                ers_store_max_kw= 4000,
                ers_deploy_per_lap_kw= 7,
                ers_deploy_max_kw= 6,
                ers_harvest_kw= 5)
    
    my_race_information = Race_basic_information(laps, pit_stops, coefficient_time_under_safety_car, pit_loss,
                                                 safety_car_probability, lockup_probability, lockup_def_coefficient,
                                                 coefficien_pushing_after_pit_stop, time_lost_by_fuel_per_1kg_1lap, push_lift)
    my_simulator = Race_Simulator(Soft, Medium, Hard, Hard, Car_on_track, my_race_information, top_strategies_number)
    my_simulator.calculate_best_strategy()
    

    #my_simulator.print_lap_info_for_best_strategy(1)
    #my_simulator.print_lap_info_for_best_strategy(57)
    #my_simulator.print_lap_info_for_best_strategy(100)
    #my_simulator.print_best_strategy()
    
    my_simulator.print_best_strategy()
    my_simulator.print_lock_ups()
    my_simulator.print_safety_car()
    
    my_simulator.print_all_top_strategies()
    #my_simulator.print_push_lift_and_coast_coeff()
    
    lap_times_ = True
    delta_last_lap_ = False
    tyre_degradation = False
    fuel_burn_ = False
    fuel_mode_ = False
    ers_start_of_lap_ = False
    ers_deployed_harvested_ = False
    ers_time_gained_ = False
    ers_mod_ = False
    
    my_simulator.print_all_different_strategies_with_pit_windows()
    
    my_simulator.show_plots(lap_times_, delta_last_lap_,tyre_degradation,
                            fuel_burn_, fuel_mode_, ers_start_of_lap_,
                            ers_deployed_harvested_, ers_time_gained_, ers_mod_)
    '''