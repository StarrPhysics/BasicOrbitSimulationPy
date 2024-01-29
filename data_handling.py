from vector import Vector, xhat, yhat, zeroVec
from typing import Union
from numpy import linalg

"""
class SimObjectData:
        
        # Class which defines the manner in which simulation objects store the data which is produced
        # during the simulation.
        

        def __init__(self, inital_position: Vector, inital_velocity: Vector) -> None:
                self.positions.append(inital_position)
                self.velocities.append(inital_velocity)
                self.speeds.append(linalg.norm(inital_velocity))
                #print(inital_position)
"""

class SimObject:
        """
        Class which defines the properties of a simulation object, establishes the location of stored data, and the methods to interact with that data during and after the simulation.
        """

        ### Single Assignment Variables ###
        _parent: object # References the parent class, which is the containing instance of the Simulation class
        _objectName: str # Generic object name
        _objectMass: float # Object mass used in force calculations
        _isStatic: bool # Flag to determine whether the object is static or not

        ### Re-referenced Variables ###
        _positions: list[Vector]  = []  # List of all position vectors
        _velocities: list[Vector] = []  # List of all velocity vectors 
        _speeds: list[float]      = []  # List of all magnitudes of velocity vectors

        def __init__(self,
                     parent: object,
                     init_position: Vector, 
                     init_velocity: Vector,
                     name: str, 
                     isStatic: bool = False, 
                     mass = 1.00,
                     ) -> None:
                r"""
                Parameters
                ----------
                `parent : Simulation`
                        Parent class, which is the containing instance of the Simulation class.
                `init_position : Vector`
                        Initial position of the object.
                `init_velocity : Vector`
                        Initial velocity of the object.
                `name : str`
                        Name of the object.
                `isStatic : bool`
                        Flag indicating whether the object is static or not. Default is False.
                `mass : float`
                        Mass of the object. Default is 1.00.
                """
                init_velocity = init_velocity if not isStatic else zeroVec

                self._parent     = parent
                self.name        = name
                self.mass        = mass
                self.isStatic    = isStatic
                self._positions  = [init_position]
                self._velocities = [init_velocity]
                self._speeds     = [linalg.norm(init_velocity)]

        def __str__(self):
                return 'SimObject(' + ', '.join([
                                f"name='{self.name}'",
                                f"mass={self.mass}",
                                f"_positions={[(vector[0], vector[1]) for vector in self._positions[0:3]] if len(self._positions) < 3 else f'[...{self._positions[-1]}]'}",
                                f"_velocities={[(vector[0], vector[1]) for vector in self._velocities[0:3]] if len(self._velocities) < 3 else f'[...{self._velocities[-1]}]'}",
                                f"_speeds={self._speeds[0:3] if len(self._speeds) < 3 else f'[...{self._speeds[-1]}]'}",
                        ]) + ')'

class SimObjectList:
    """
    Basically, this object is just a `list`, so feel free to treat it as such.

    The only real difference is that items are `SimObject`s by default, and the human-readable representation of the instance is more readable.
    """

    items: SimObject

    # List of number of sim_time seconds since simulation began, updates every time a calculation cycle is executed 
    _sim_times: list[float] = []

    # List of number of real_time seconds since simulation began, updates every time a calculation cycle is executed 
    _real_times: list[float] = []


    _center: Vector = None # Center of the simulated objects
    _max_center_deviation = None # Maximum deviation from the center of the simulated objects
    _x_limit: list[float] = None # x-axis limits of the simulation
    _y_limit: list[float] = None # y-axis limits of the simulation

    def __init__(self):
        self.items = []

    def __getitem__(self, index) -> SimObject:
        return self.items[index]

    def __setitem__(self, index, value):
        self.items[index] = value

    def __delitem__(self, index):
        del self.items[index]

    def __len__(self) -> SimObject:
        return len(self.items)

    def append(self, item):
        self.items.append(item)

    def __iter__(self) -> SimObject:
        return iter(self.items)
    
    def __str__(self):
          return ', \n'.join([
                "SimObjectList(items=[\n" + ', \n'.join(f'\t\t{i}:  {str(simObject)}' for (i, simObject) in enumerate(self.items)) + f"\n\t{' ' * 5}]",
                f"\t{' ' * 5}sim_times={self._sim_times}",
                f"\t{' ' * 5}real_times={self._real_times}",
          ])
    
    def positions(self) -> list[Vector]:
         return [simObject._positions[-1] for simObject in self.items]
              
