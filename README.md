# ispace Technical Assessment
Python tool for comparing propulsion system concepts

## Common Architecture Requirements
* Required delta-V: 2,000 m/s
* Dry mass: 600 kg.
    * Excludes propulsion system dry mass
* Limit mass: 1,500 kg.
    * Vehicle dry mass + prop system dry mass + propellant mass
* TWR requirement at ignition: >= 1.5
* Propellant density: 1,000 kg/m3
* Propellant tank mass
    * Proportional to tank's pressure and propellant mass.
    * Assume Al-6066 tank material
    * Spherical tank for volume + mass
    * Size volume for required propellant load
    * Size tank thickness for Al-6066 mat'l properties
        * density: 2.72 g/cm^3
        * yield stress: 359 MPa
        * safety factor: 1.5
            * typically proof to 1.5x MEOP w/o permanent deformation

### Pressure-fed System Constraints
* Pressurant system mass is proportional to tank pressure and to propellant mass
    * Scalar factor of 0.002 kg/bar
* Propellant tank pressure: 25 bar
* Engine inlet pressure: 20 bar
* Isp: 310 s

### Pump-fed System Constraints
* Pump mass is proportional to thrust
    * Scalar factor of 0.008 kg/N
* Propellant tank pressure: 10 bar
* Engine inlet pressure: 40 bar
* Isp: 330 s

## Outputs
* Propellant mass requirment
* Margin against limit mass