from vector import Vector, xhat, yhat, zeroVec


class SimObject_DataEntryStruct:
        """
        Class which defines the manner in which simulation objects store the data which is produced
        during the simulation.
        """

        position: list[Vector] = []    # List of all position vectors
        velocity: list[Vector] = []     # List of all velocity vectors 
        mag_vel: list[float] = []       # List of all magnitudes of velocity vectors



class SimObject:
        """
        Class which defines the properties of a simulation object and establishes the location of stored data.
        """
              
        _objectName: str # Generic object name
        _objectMass: float # Object mass used in force calculations
        
        __parent: object # References the parent class, which is a Simulation instance
        __simulation_data = SimObject_DataEntryStruct()


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
                print(id(parent))
                self.name = name
                self.mass = mass
                self.isStatic = isStatic
                self.__simulation_data.position.append(init_position)
                self.__simulation_data.velocity.append(init_velocity if not isStatic else zeroVec)
                

        """
        def get_latest_position_velocity(self) -> tuple(Vector):
                print('Test')
                return (
                        self.__simulation_data.position[-1], 
                        self.__simulation_data.velocity[-1]
                        )
        """

        def get_latest_position(self) -> Vector:
                return self.__simulation_data.position[-1]
        
        def get_latest_velocity(self) -> Vector:
                return self.__simulation_data.velocity[-1]
        
        def get_latest_sim_time(self) -> float:
                return self.__simulation_data.parent
        
        def get_position_at_index(self, index: int) -> Vector:
                return self.__simulation_data.position(index)
        
        def get_velocity_at_index(self, index: int) -> Vector:
                return self.__simulation_data.position(index)
        
        


