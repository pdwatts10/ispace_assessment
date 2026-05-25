import numpy as np

from src import Q_
from pint import Quantity
from typing import Literal
from dataclasses import dataclass,field

G0 = Q_(9.81,'m/s^2')

@dataclass
class PropTank:
    matl_density:Quantity
    yield_strength:Quantity
    fluid_volume:Quantity
    meop:Quantity
    safety_factor:float
    _inner_radius:Quantity = field(init=False)
    _wall_thickness:Quantity = field(init=False)
    _dry_mass:Quantity = field(init=False)

    def __post_init__(self):
        self._inner_radius = (self.fluid_volume.to('m^3')/np.pi)**(1/3)
        self._wall_thickness = self.safety_factor*self.meop.to('Pa')*self.inner_radius.to('m')/(2.0*self.yield_strength.to('Pa'))
        self._dry_mass = self.matl_density.to('kg/m^3')*np.pi*((self.inner_radius.to('m') + self.wall_thickness.to('m'))**3 - self.inner_radius.to('m')**3)

    @property
    def inner_radius(self) -> Quantity:
        return self._inner_radius

    @property
    def dry_mass(self) -> Quantity:
        return self._dry_mass
    
    @property
    def wall_thickness(self) -> Quantity:
        return self._wall_thickness

    # preliminary sizing of tank based on req'd volume, material properties, MEOP, and safety factor
    # mostly just need the mass of the tank for propellant loading and TWR calcs
    def size_tank(self,**kwargs) -> None:
        self.matl_density = kwargs.get('matl_density',self.matl_density)
        self.yield_strength = kwargs.get('yield_strength',self.yield_strength)
        self.fluid_volume = kwargs.get('fluid_volume',self.fluid_volume)
        self.meop = kwargs.get('meop',self.meop)
        self.safety_factor = kwargs.get('safety_factor',self.safety_factor)

        self._inner_radius = (self.fluid_volume.to('m^3')/np.pi)**(1/3)
        self._wall_thickness = self.safety_factor*self.meop.to('Pa')*self.inner_radius.to('m')/(2.0*self.yield_strength.to('Pa'))
        self._dry_mass = self.matl_density.to('kg/m^3')*np.pi*((self.inner_radius.to('m') + self.wall_thickness.to('m'))**3 - self.inner_radius.to('m')**3)

prop_sytem_type = Literal[
    'pump_fed',
    'pressure_fed'
]

@dataclass
class PropulsionSystem:
    tank: PropTank
    inlet_pressure: Quantity
    specific_impulse: Quantity
    thrust: Quantity
    mass_scalar: Quantity
    system_type: prop_sytem_type
    _dry_mass: Quantity = field(init=False)

    def __post_init__(self):
        match self.system_type:
            case 'pressure_fed':
                self._dry_mass = self.tank.meop.to('bar')*self.mass_scalar.to('kg/bar') + self.tank.dry_mass.to('kg')
            case 'pump_fed':
                self._dry_mass = self.thrust.to('N')*self.mass_scalar.to('kg/N') + self.tank.dry_mass.to('kg')
            # should be impossible to reach here since system_type is Literal typed, but still hit a _dry_mass attribute error due to typo during testing...
            case _:
                raise ValueError(f"Invalid system_type input: {self.system_type}. Acceptable options are 'pump_fed' or 'pressure_fed'")
    
    @property
    def dry_mass(self) -> Quantity:
        return self._dry_mass
    
    def size_prop_system(self,**kwargs) -> None:
        self.tank.size_tank(**kwargs)

        self.thrust = kwargs.get('thrust',self.thrust)
        self.mass_scalar = kwargs.get('mass_scalar',self.mass_scalar)

        match self.system_type:
            case 'pressure_fed':
                self._dry_mass = self.tank.meop.to('bar')*self.mass_scalar.to('kg/bar') + self.tank.dry_mass.to('kg')
            case 'pump_fed':
                self._dry_mass = self.thrust.to('N')*self.mass_scalar.to('kg/N') + self.tank.dry_mass.to('kg')
            # same deal,shouldn't be possible to reach here
            case _:
                raise ValueError(f"Invalid system_type input: {self.system_type}. Acceptable options are 'pump_fed' or 'pressure_fed'")

@dataclass
class Vehicle:
    delta_v: Quantity
    base_mass: Quantity
    limit_mass: Quantity
    propellant_density: Quantity
    prop_system: PropulsionSystem
    
    _propellant_mass: Quantity = field(init=False)
    _wet_mass: Quantity = field(init=False)
    _twr: Quantity = field(init=False)

    def __post_init__(self) -> None:
        self._initialize_prop_mass()
        
        self._wet_mass = self.propellant_mass.to('kg') + self.base_mass.to('kg') + self.prop_system.dry_mass.to('kg')
        self._twr = self.prop_system.thrust.to('N')/(G0*self.wet_mass)
        self._mass_margin = (self.limit_mass.to('kg') - self.wet_mass.to('kg'))/self.limit_mass.to('kg')
    
    # since we know the limit mass, can make an educated guess of the required prop load before optimization
    def _initialize_prop_mass(self) -> None:
        guess_final_mass = self.limit_mass/np.exp(self.delta_v.to('m/sec')/(self.prop_system.specific_impulse.to('sec')*G0.to('m/sec^2')))
        self._propellant_mass = self.limit_mass.to('kg') - guess_final_mass.to('kg')

        self._initialize_tank_volume()

    # after prelim prop load sizing, initialize max required tank volume
    # this doesn't include any ullage volume though
    def _initialize_tank_volume(self) -> None:
        self.prop_system.tank.fluid_volume = self.propellant_mass.to('kg')/self.propellant_density.to('kg/m^3')
        self.prop_system.size_prop_system(fluid_volume=self.prop_system.tank.fluid_volume)

    @property
    def propellant_mass(self) -> Quantity:
        return self._propellant_mass
    
    @property
    def wet_mass(self) -> Quantity:
        return self._wet_mass
    
    @property
    def twr(self) -> Quantity:
        return self._twr
    
    @property
    def mass_margin(self) -> Quantity:
        return self._mass_margin

    def size_vehicle(self,**kwargs) -> None:
        
        self.delta_v = kwargs.get('delta_v',self.delta_v)
        self.base_mass = kwargs.get('base_mass',self.base_mass)
        self.limit_mass = kwargs.get('limit_mass',self.limit_mass)
        self.propellant_density = kwargs.get('propellant_density',self.propellant_density)

        curr_wet_mass = self.wet_mass
        diff = 1.0

        # small iteration loop
        # size the prop system based on the currently required volume of propellant
        # everytime the prop volume changes, the tank mass (and therefore vehicle mass) changes, so our propellant requirement changes
        # make a couple passes until the vehicle wet mass stops appreciably changing
        while diff > 0.005:
            kwargs['fluid_volume'] = self.propellant_mass.to('kg')/self.propellant_density.to('kg/m^3')
            self.prop_system.size_prop_system(**kwargs)

            self._propellant_mass = (self.base_mass.to('kg') + self.prop_system.dry_mass.to('kg'))*(np.exp(self.delta_v.to('m/sec')/(self.prop_system.specific_impulse.to('sec')*G0))-1.0)
            self._wet_mass = self._propellant_mass.to('kg') + self.base_mass.to('kg') + self.prop_system.dry_mass.to('kg')

            diff = abs(self.wet_mass - curr_wet_mass)/curr_wet_mass
            diff = diff.m
            curr_wet_mass = self.wet_mass
        
        self._twr = self.prop_system.thrust.to('N')/(G0*self._wet_mass)
        self._mass_margin = (self.limit_mass.to('kg') - self.wet_mass.to('kg'))/self.limit_mass.to('kg')

