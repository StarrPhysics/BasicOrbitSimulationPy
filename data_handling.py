from vector import Vector, xhat, yhat, zeroVec
from typing import Union
from numpy import linalg

class SimObjectData:
        """
        Class which defines the manner in which simulation objects store the data which is produced
        during the simulation.
        """

        position: list[Vector] = []    # List of all position vectors
        velocity: list[Vector] = []     # List of all velocity vectors 
        speed: list[float] = []       # List of all magnitudes of velocity vectors

        def __init__(self, inital_position: Vector, inital_velocity: Vector) -> None:
                self.position.append(inital_position)
                self.velocity.append(inital_velocity)
                self.speed.append(linalg.norm(inital_velocity))


class SimObject:
        """
        Class which defines the properties of a simulation object, establishes the location of stored data, and the methods to interact with that data during and after the simulation.
        """
              
        _objectName: str # Generic object name
        _objectMass: float # Object mass used in force calculations
        
        __parent: object # References the parent class, which is the containing instance of the Simulation class
        __object_simulation_data: SimObjectData # Stores the actual data gathered during the simulation for this object

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
                

                self.name = name
                self.mass = mass
                self.isStatic = isStatic
                self.__object_simulation_data = SimObjectData(
                        init_position, 
                        init_velocity if not isStatic else zeroVec
                        )

        #def __str__(self):
        #        return 'Blah'
                
        def get_latest(self, *args: str, amount: int = 1) -> tuple[Union[Vector,float]]:
                """
                Returns the latest kinematic data assosiated with the specific SimObject being called.

                Parameters
                ----------
                `*args: strings` 
                        Variable-length argument list of strings specifying the type data to retrieve. 
                        Data tpes avaliable include 'position', 'velocity', 'speed', 'simulation_time', and 'real_time'.
                        If no enteries are provided, then all data types are retrieved by default.

                `amount: int` 
                        The amount of data to retrieve from latest entery. Some example values include:
                - If `amount = 10`; which returns 10 latest enteries. 
                - If `amount = 1`; only returns the latest (aka. last) entry.
                - If `amount = 0`; all data records are returned.

                Examples
                -------- ::

                        sim = Simulation()

                        sim.addObject([0,0], [1,1], isStatic=False)
                        # Assume 3 additional objects have been added to the simulation
                        # using the `addObject` method.

                        sim.run()
                        # Assume the simulation has completed its runtime,
                        # as accessing data during runtime is restricted externally.

                        sim.get_simulation_data()[0]

                ! NEEDS COMPLETION !
                ```

                """

                response: list = []

                args = args or ('position','velocity','speed','simulation_time', 'real_time')
                
                for arg in args:
                        match arg.lower():
                                case 'position':        response += self.__object_simulation_data.position[-amount:]
                                case 'velocity':        response += self.__object_simulation_data.velocity[-amount:]
                                case 'speed':           response += self.__object_simulation_data.speed[-amount:]
                                case 'simulation_time': response += self.__parent.__sim_time[-amount:]
                                case 'real_time':       response += self.__parent.__real_time[-amount:]
                                case _: raise KeyError(f"Invalid argument `{arg}` passed to `get_latest`.")
                
                return response

class SimObjectList:
    """
    Basically, this object is just a `list`, so feel free to treat it as such.

    The only real difference is that items are `SimObject`s by default, and the human-readable representation of the instance is more readable.
    """

    items: SimObject


    # List of number of sim_time seconds since simulation began, updates every time a calculation cycle is executed 
    __sim_time: list[float] = []

    # List of number of real_time seconds since simulation began, updates every time a calculation cycle is executed 
    __real_time: list[float] = []

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
          return f"""[{", ".join([f"<class SimObject: '{simObject.name}'>" for simObject in self.items])}]"""
