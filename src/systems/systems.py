import numpy as np
from src.systems import Q_
from pint import Quantity
from typing import Union,Literal
from dataclasses import dataclass,field

G0 = Q_(9.81,'m/s^2')

@dataclass
class PropTank:
    matl_density:Quantity
    yield_strength:Quantity
    volume:Quantity
    meop:Quantity
    safety_factor:float
    _inner_radius:Quantity = field(init=False)
    _wall_thickness:Quantity = field(init=False)
    _dry_mass:Quantity = field(init=False)

    def __post_init__(self):
        self._inner_radius = (self.volume.to('m^3')/np.pi)**(1/3)
        self._wall_thickness = self.safety_factor*self.meop.to('Pa')*(self.volume.to('m^3')/np.pi)**(1/3)/(2.0*self.yield_strength.to('Pa'))
        self._dry_mass = self.matl_density.to('kg/m^3')*np.pi*((self.inner_radius.to('m') + self.wall_thickness.to('m'))**3 - self.inner_radius.to('m')**3)

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self,params:dict[str,Quantity]):

        self.volume = params.get('volume',self.volume)
        self._inner_radius = (self.volume.to('m^3')/np.pi)**(1/3)

    @property
    def dry_mass(self):
        return self._dry_mass
    
    @dry_mass.setter
    def dry_mass(self,params:dict[str,Quantity]):

        self.matl_density = params.get('matl_density',self.matl_density)
        self._dry_mass = self.matl_density.to('kg/m^3')*np.pi*((self.inner_radius.to('m') + self.wall_thickness.to('m'))**3 - self.inner_radius.to('m')**3)

    @property
    def wall_thickness(self):
        return self._wall_thickness

    @wall_thickness.setter
    def wall_thickness(self,params:dict):

        self.inner_radius = params

        self.yield_strength = params.get('yield_strength',self.yield_strength)
        self.meop = params.get('meop',self.meop)
        self.safety_factor = params.get('safety_factor',self.safety_factor)

        self._wall_thickness = self.safety_factor*self.meop.to('Pa')*self.inner_radius/(2.0*self.yield_strength.to('Pa'))

        self.dry_mass = params

    @classmethod
    def parse_config(cls,path:str) -> 'PropTank':
        pass

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
    system_type: prop_sytem_type
    mass_scalar: Quantity
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
    
    @dry_mass.setter
    def dry_mass(self,params:dict):
        match self.system_type:
            case 'pressure_fed':
                self.tank.meop = params.get('meop',self.tank.meop)
                self.mass_scalar = params.get('mass_scalar',self.mass_scalar)

                self.tank.wall_thickness = params
                self._dry_mass = self.tank.meop.to('bar')*self.mass_scalar.to('kg/bar') + self.tank.dry_mass.to('kg')
            case 'pump_fed':
                self.thrust = params.get('thrust',self.thrust)
                self.mass_scalar = params.get('mass_scalar',self.mass_scalar)
                self._dry_mass = self.thrust.to('N')*self.mass_scalar.to('kg/N') + self.tank.dry_mass.to('kg')


@dataclass
class Vehicle:
    delta_v: Quantity
    base_mass: Quantity
    limit_mass: Quantity
    propellant_density: Quantity
    prop_system: PropulsionSystem
    
    _twr: float = field(init=False)
    _propellant_mass: Quantity = field(init=False)
    
    def __post_init__(self):
        self._twr = self.prop_system.thrust.to('N')/(G0*(self.base_mass.to('kg')+self.prop_system.dry_mass.to('kg')))
        self._propellant_mass = (self.base_mass.to('kg') + self.prop_system.dry_mass.to('kg'))/(np.exp(self.delta_v/(self.prop_system.specific_impulse*G0))-1.0)

    @classmethod
    def parse_config(cls,path:str) -> 'Vehicle':
        pass   