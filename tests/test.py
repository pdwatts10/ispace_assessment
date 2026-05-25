import pytest

from src import Q_
from src.systems import *

PROP_TANK = PropTank(
    matl_density=Q_(2.71,'g/cm^3'),
    yield_strength=Q_(359.0,'MPa'),
    fluid_volume=Q_(1.0,'m^3'),
    meop=Q_(10.0,'bar'),
    safety_factor=1.5
)

PROPULSION_SYSTEM = PropulsionSystem(
    tank=PROP_TANK,
    inlet_pressure=Q_(40,'bar'),
    specific_impulse=Q_(330,'sec'),
    thrust=Q_(10.0,'kN'),
    mass_scalar=Q_(0.008,'kg/N'),
    system_type='pump_fed'    
)

# TEST_VEHICLE = Vehicle(
#     delta_v=Q_(2000.0,'m/sec'),
#     base_mass=Q_(600.0,'kg'),
#     limit_mass=Q_(1500.0,'kg'),
#     propellant_density=Q_(1000.0,'kg/m^3'),
#     prop_system=PROPULSION_SYSTEM    
# )

def calc_prop_tank_mass(
    matl_density,
    yield_strength,
    fluid_volume,
    meop,
    safety_factor
) -> float:
    
    return PropTank(
        matl_density=matl_density,
        yield_strength=yield_strength,
        fluid_volume=fluid_volume,
        meop=meop,
        safety_factor=safety_factor
    ).dry_mass.to('kg').m

def test_prop_tank():
    assert calc_prop_tank_mass(
        matl_density=Q_(2.71,'g/cm^3'),
        yield_strength=Q_(359.0,'MPa'),
        fluid_volume=Q_(1.0,'m^3'),
        meop=Q_(10.0,'bar'),
        safety_factor=1.5
    ) == pytest.approx(17.0202)

def calc_prop_system_mass(
    tank,
    inlet_pressure,
    specific_impulse,
    thrust,
    mass_scalar,
    system_type
):
    return PropulsionSystem(
        tank=tank,
        inlet_pressure=inlet_pressure,
        specific_impulse=specific_impulse,
        thrust=thrust,
        mass_scalar=mass_scalar,
        system_type=system_type
    ).dry_mass.to('kg').m

def test_prop_system():
    assert calc_prop_system_mass(
        tank=PROP_TANK,
        inlet_pressure=Q_(40,'bar'),
        specific_impulse=Q_(330,'sec'),
        thrust=Q_(10.0,'kN'),
        mass_scalar=Q_(0.008,'kg/N'),
        system_type='pump_fed'
    ) == pytest.approx(97.0202)

def calc_vehicle_propellant_mass(
    delta_v,
    base_mass,
    limit_mass,
    propellant_density,
    prop_system,
):
    return Vehicle(
        delta_v=delta_v,
        base_mass=base_mass,
        limit_mass=limit_mass,
        propellant_density=propellant_density,
        prop_system=prop_system
    ).propellant_mass.to('kg').m

def calc_vehicle_wet_mass(
    delta_v,
    base_mass,
    limit_mass,
    propellant_density,
    prop_system,
):
    return Vehicle(
        delta_v=delta_v,
        base_mass=base_mass,
        limit_mass=limit_mass,
        propellant_density=propellant_density,
        prop_system=prop_system
    ).wet_mass.to('kg').m

def calc_vehicle_twr(
    delta_v,
    base_mass,
    limit_mass,
    propellant_density,
    prop_system,
):
    return Vehicle(
        delta_v=delta_v,
        base_mass=base_mass,
        limit_mass=limit_mass,
        propellant_density=propellant_density,
        prop_system=prop_system
    ).twr.m

def calc_vehicle_mass_margin(
    delta_v,
    base_mass,
    limit_mass,
    propellant_density,
    prop_system,
):
    return Vehicle(
        delta_v=delta_v,
        base_mass=base_mass,
        limit_mass=limit_mass,
        propellant_density=propellant_density,
        prop_system=prop_system
    ).mass_margin.m

def test_vehicle():
    assert calc_vehicle_propellant_mass(
        delta_v=Q_(2000.0,'m/sec'),
        base_mass=Q_(600.0,'kg'),
        limit_mass=Q_(1500.0,'kg'),
        propellant_density=Q_(1000.0,'kg/m^3'),
        prop_system=PROPULSION_SYSTEM 
    ) == pytest.approx(691.3052)

    assert calc_vehicle_wet_mass(
        delta_v=Q_(2000.0,'m/sec'),
        base_mass=Q_(600.0,'kg'),
        limit_mass=Q_(1500.0,'kg'),
        propellant_density=Q_(1000.0,'kg/m^3'),
        prop_system=PROPULSION_SYSTEM 
    ) == pytest.approx(1383.0713)

    assert calc_vehicle_twr(
        delta_v=Q_(2000.0,'m/sec'),
        base_mass=Q_(600.0,'kg'),
        limit_mass=Q_(1500.0,'kg'),
        propellant_density=Q_(1000.0,'kg/m^3'),
        prop_system=PROPULSION_SYSTEM 
    ) == pytest.approx(0.7370321)

    assert calc_vehicle_mass_margin(
        delta_v=Q_(2000.0,'m/sec'),
        base_mass=Q_(600.0,'kg'),
        limit_mass=Q_(1500.0,'kg'),
        propellant_density=Q_(1000.0,'kg/m^3'),
        prop_system=PROPULSION_SYSTEM 
    ) == pytest.approx(0.0779524)