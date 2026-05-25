import pandas as pd

from dataclasses import asdict

from src.systems import *
from src.optimization import *
from src.load_config import get_vehicles,get_constraints

def size_landar(vehicle_config_path:str,constraints_config_path:str):
    
    vehicles = get_vehicles(config_path=vehicle_config_path)
    targets = get_constraints(config_path=constraints_config_path)

    for vehicle in vehicles:
        vehicle = optimize_vehicle(vehicle=vehicle,targets=targets)

    return vehicles

def parse_vehicle_to_df(vehicles:list[Vehicle]|Vehicle):
    df = None

    for vehicle in vehicles:
        data = {}
        for _ka,_va in vehicle.__dict__.items():
            match _va:
                case PropulsionSystem():
                    for _kp,_pa in _va.__dict__.items():
                        match _pa:
                            case PropTank():
                                for _kt,_ta in _pa.__dict__.items():
                                    data[_kt] = _ta
                            case _:
                                data[_kp] = _pa
                case _:
                    data[_ka] = _va

        if df is None:
            df = pd.DataFrame.from_dict(data,orient='index')
        else:
            df = pd.concat([df,pd.DataFrame.from_dict(data,orient='index')],axis=1)
        
    df.columns = df.loc['system_type',:].values
    df = df.drop('system_type',inplace=False)
    df.to_excel('system_compare.xlsx')

    return df

if __name__ == '__main__':
    vehicle_config_path = r'C:\Users\pdwat\git\ispace_assessment\configs\vehicle_configs.yaml'
    constraints_config_path = r'C:\Users\pdwat\git\ispace_assessment\configs\sizing_constraints.yaml'

    vehicles = size_landar(vehicle_config_path=vehicle_config_path,constraints_config_path=constraints_config_path)

    df = parse_vehicle_to_df(vehicles)
    print(df)