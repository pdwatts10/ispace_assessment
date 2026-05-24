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
        self._wall_thickness = self.safety_factor*self.meop.to('Pa')*(self.fluid_volume.to('m^3')/np.pi)**(1/3)/(2.0*self.yield_strength.to('Pa'))
        self._dry_mass = self.matl_density.to('kg/m^3')*np.pi*((self.inner_radius.to('m') + self.wall_thickness.to('m'))**3 - self.inner_radius.to('m')**3)

    @classmethod
    def parse_config(cls,path:str) -> 'PropTank':
        pass

    @property
    def inner_radius(self) -> Quantity:
        return self._inner_radius

    @property
    def dry_mass(self) -> Quantity:
        return self._dry_mass
    
    @property
    def wall_thickness(self) -> Quantity:
        return self._wall_thickness

    def size_tank(self,**kwargs) -> None:
        self.matl_density = kwargs.get('matl_density',self.matl_density)
        self.yield_strength = kwargs.get('yield_strength',self.yield_strength)
        self.fluid_volume = kwargs.get('fluid_volume',self.fluid_volume)
        self.meop = kwargs.get('meop',self.meop)
        self.safety_factor = kwargs.get('safety_factor',self.safety_factor)

        self._inner_radius = (self.fluid_volume.to('m^3')/np.pi)**(1/3)
        self._wall_thickness = self.safety_factor*self.meop.to('Pa')*(self.fluid_volume.to('m^3')/np.pi)**(1/3)/(2.0*self.yield_strength.to('Pa'))
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
    
    @classmethod
    def parse_config(cls,path:str) -> 'PropulsionSystem':
        pass

    @property
    def dry_mass(self):
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

    def __post_init__(self):
        self._initialize_prop_mass()
        
        self._wet_mass = self.propellant_mass.to('kg') + self.base_mass.to('kg') + self.prop_system.dry_mass.to('kg')
        self._twr = self.prop_system.thrust.to('N')/(G0*self.wet_mass)
        self._mass_margin = (self.limit_mass.to('kg') - self.wet_mass.to('kg'))/self.limit_mass.to('kg')
    
    def _initialize_prop_mass(self) -> None:
        guess_final_mass = self.limit_mass/np.exp(self.delta_v.to('m/sec')/(self.prop_system.specific_impulse.to('sec')*G0.to('m/sec^2')))
        self._propellant_mass = self.limit_mass.to('kg') - guess_final_mass.to('kg')

        self._initialize_tank_volume()

    def _initialize_tank_volume(self) -> None:
        self.prop_system.tank.fluid_volume = self.propellant_mass.to('kg')/self.propellant_density.to('kg/m^3')

    @classmethod
    def parse_config(cls,path:str) -> 'Vehicle':
        pass

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

    def optimize(
        self,
        constraints:list,
        independents:list
    ):
        pass