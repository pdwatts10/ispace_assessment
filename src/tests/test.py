from src.systems import Q_
from src.systems.systems import *

lunar_lander = Vehicle(
    delta_v=Q_(2000.0,'m/sec'),
    dry_mass=Q_(600.0,'kg'),
    limit_mass=Q_(1500.0,'kg'),
    twr=1.5,
    propellant_density=Q_(1000.0,'kg/m^3'),
    tank=PropTank(
        matl_density=Q_(2.72,'g/cm^3'),
        yield_strength=Q_(359.0,'MPa'),
        volume=Q_(1.0,'m^3'),
        meop=Q_(25.0,'bar'),
        safety_factor=1.5
    )
)

print(lunar_lander.tank.inner_radius)
print(lunar_lander.tank.wall_thickness.to('mm'))
print(lunar_lander.tank.dry_mass)

lunar_lander.tank.wall_thickness = {'volume':Q_(2.0,'m^3')}

print(lunar_lander.tank.inner_radius)
print(lunar_lander.tank.wall_thickness.to('mm'))
print(lunar_lander.tank.dry_mass)

lunar_lander.tank.wall_thickness = {'meop':Q_(15.0,'bar')}

print(lunar_lander.tank.inner_radius)
print(lunar_lander.tank.wall_thickness.to('mm'))
print(lunar_lander.tank.dry_mass)
