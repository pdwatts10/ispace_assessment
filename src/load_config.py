import yaml

from src import Q_
from src.systems import Vehicle, PropulsionSystem, PropTank
from src.optimization import Constraint,Target

def vehicle_constructor(
    loader: yaml.SafeLoader, 
    node: yaml.nodes.MappingNode,
) -> Vehicle:

    """
        NOT CURRENTLY IMPLEMENTED
        could probably do something a little smarter w/ yaml MappingNodes
        bit out of scope for this assessment though
    """
    
    _node = {}

    def process_node(node: yaml.nodes.MappingNode) -> None:
        for _n in node.values():
            pass

    process_node(node)

    return Vehicle(**_node)

def target_constructor(
    loader: yaml.SafeLoader, 
    node: yaml.nodes.MappingNode,
) -> Target:
    
    """
        NOT CURRENTLY IMPLEMENTED
        could probably do something a little smarter w/ yaml MappingNodes
        bit out of scope for this assessment though
    """
    
    _node = {}

    def process_node(node: yaml.nodes.MappingNode) -> None:
        for _n in node.values():
            pass

    process_node(node)

    return Target(**_node)

def get_loader() -> type[yaml.SafeLoader]:
    loader = yaml.SafeLoader
    # loader.add_constructor('!vehicle',vehicle_constructor)
    return loader

def get_vehicles(config_path:str) -> list[Vehicle]:
    with open(config_path,'rb') as fid:
        data = yaml.load(fid,Loader=get_loader())

    # parse nodes in the config tree recursively
    # kinda brute force, fully embracing python idiom: ask forgiveness, not permission...
    def parse_node(node:dict):
        _node = {}
        for k,v in node.items():
            match v:
                case dict():
                    try:
                        # blegh, maybe making all of these Quantities was a mistake...
                        _node[k] = PropTank(
                                matl_density = Q_(v['matl_density']),
                                yield_strength = Q_(v['yield_strength']),
                                fluid_volume = Q_(v['fluid_volume']),
                                meop = Q_(v['meop']),
                                safety_factor = v['safety_factor']
                            )
                    except KeyError:
                        _node[k] = parse_node(v)
                case _:
                    _node[k] = v
        # essentially try to construct one of the 3 governing class objects whenever you get to the bottom of a tree
        try:
            return PropulsionSystem(
                tank = _node['tank'],
                inlet_pressure = Q_(_node['inlet_pressure']),
                specific_impulse = Q_(_node['specific_impulse']),
                thrust = Q_(_node['thrust']),
                mass_scalar = Q_(_node['mass_scalar']),
                system_type = _node['system_type']
            )
        except KeyError:
            return Vehicle(
                delta_v = Q_(_node['delta_v']),
                base_mass = Q_(_node['base_mass']),
                limit_mass = Q_(_node['limit_mass']),
                propellant_density = Q_(_node['propellant_density']),
                prop_system = _node['prop_system'],
            )

    vehicles = []    
    for _n in data.values():
        vehicles.append(parse_node(_n))
        pass

    return vehicles

def get_constraints(config_path:str) -> list[Target]:
    with open(config_path,'rb') as fid:
        data = yaml.load(fid,Loader=get_loader())

    def parse_node(node:list):
        constraints = []
        for item in node:
            _node = {}
            match item:
                case dict():
                    for k,v in item.items():
                        try:
                            _node[k] = Constraint(
                                param=v['param'],
                                operator=v['operator'],
                                threshold=Q_(v['threshold']) 
                                    if isinstance(v['threshold'],str) else v['threshold']
                            )
                        except TypeError:
                            _node[k] = v

            constraints.append(Target(**_node))
        return constraints

    constraints = []    
    for _n in data.values():
        constraints.extend(parse_node(_n))
        
    return constraints
    
if __name__ == '__main__':
    path = r'C:\Users\pdwat\git\ispace_assessment\configs\sizing_constraints.yaml'

    vehicle_config = get_constraints(path)

    pass