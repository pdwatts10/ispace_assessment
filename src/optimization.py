import operator

from pint import Quantity
from typing import Optional
from dataclasses import dataclass

from src import Q_
from src.systems import Vehicle, PropTank, PropulsionSystem

MAX_PASS = 50
OPERATORS = {
    '>'  : operator.gt,
    '>=' : operator.ge,
    '<'  : operator.lt,
    '<=' : operator.le,
    '==' : operator.eq
}

@dataclass
class Constraint:
    param: str
    operator: str
    threshold: int|float|Quantity
    tolerance: Optional[float] = None

    @staticmethod
    def search_for_field_value(param:str,vehicle:Vehicle) -> Quantity|float:
            try:
                val = getattr(vehicle,param)
            except AttributeError:
                for _va in vehicle.__dict__.values():
                    match _va:
                        case PropulsionSystem():
                            try:
                                val = getattr(_va,param)
                            except AttributeError:
                                for _pa in _va.__dict__.values():
                                    match _pa:
                                        case PropTank():
                                            val = getattr(_pa,param)

            return val

    def evaluate_constraint(self,vehicle:Vehicle) -> bool:

        curr_val = self.search_for_field_value(self.param,vehicle)
        match self.operator:
            case '==':
                match self.threshold:
                    case int():
                        if curr_val == self.threshold: return True
                    case _:
                        if not self.tolerance:
                            raise Exception("Cannot evaluate equivalence of float type objects without a tolerance")
                        else:
                            if abs(curr_val - self.threshold) < self.tolerance: return True
            case _:
                if OPERATORS.get(self.operator)(curr_val,self.threshold): return True

        return False
    
@dataclass
class Target:
    independent: str
    constraint: Constraint

def optimize_vehicle(
    vehicle: Vehicle,
    targets:list[Target]
) -> Vehicle:
    
    def evaluate_targets(targets:list[Target],vehicle:Vehicle):
        pass_fail = {}
        error = {}
        for target in targets:
            pass_fail[target.constraint.param] = target.constraint.evaluate_constraint(vehicle)
            error[target.constraint.param] = (target.constraint.search_for_field_value(target.constraint.param,vehicle) - target.constraint.threshold)/target.constraint.threshold

        return pass_fail,error
    
    pass_fail,error = evaluate_targets(targets,vehicle)

    passes = 0
    while not all(good for good in pass_fail.values()):
        if passes > MAX_PASS: break
        new_inputs = {}
        for target in targets:
            if not pass_fail[target.constraint.param]:
                new_inputs[target.independent] = (1.0-error[target.constraint.param])*target.constraint.search_for_field_value(target.independent,vehicle)

        vehicle.size_vehicle(**new_inputs)
        pass_fail,error = evaluate_targets(targets,vehicle)
        passes += 1

        # last_error = {k:v for k,v in error.items()}
        
    return vehicle