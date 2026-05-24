from src import Q_
from src.systems import *

lunar_lander = Vehicle(
    delta_v=Q_(2000.0,'m/sec'),
    base_mass=Q_(600.0,'kg'),
    limit_mass=Q_(1500.0,'kg'),
    propellant_density=Q_(1000.0,'kg/m^3'),
    prop_system = PropulsionSystem(
        tank=PropTank(
            matl_density=Q_(2.71,'g/cm^3'),
            yield_strength=Q_(359.0,'MPa'),
            fluid_volume=Q_(1.0,'m^3'),
            meop=Q_(10.0,'bar'),
            safety_factor=1.5
        ),
        inlet_pressure=Q_(40,'bar'),
        specific_impulse=Q_(330,'sec'),
        system_type='pump_fed',
        mass_scalar=Q_(0.008,'kg/N'),
        thrust=Q_(15.0,'kN')
    )
    
)

print(f'Tank Volume: {lunar_lander.prop_system.tank.fluid_volume}')
print(f'Tank Mass: {lunar_lander.prop_system.tank.dry_mass}')
print(f'Prop System Mass: {lunar_lander.prop_system.dry_mass}')

print(f'Propellant Mass = {lunar_lander.propellant_mass}')
print(f'Wet Mass = {lunar_lander.wet_mass}')
print(f'Vehicle Take-off TWR = {lunar_lander.twr}')
print(f'Limit Mass Margin = {lunar_lander.mass_margin}')
print('\n')

optimize_inputs = {
    'thrust':lunar_lander.prop_system.thrust*1.45
}

lunar_lander.size_vehicle(**optimize_inputs)

print(f'Tank Volume: {lunar_lander.prop_system.tank.fluid_volume}')
print(f'Tank Mass: {lunar_lander.prop_system.tank.dry_mass}')
print(f'Prop System Mass: {lunar_lander.prop_system.dry_mass}')

print(f'Propellant Mass = {lunar_lander.propellant_mass}')
print(f'Wet Mass = {lunar_lander.wet_mass}')
print(f'Vehicle Take-off TWR = {lunar_lander.twr}')
print(f'Limit Mass Margin = {lunar_lander.mass_margin}')
