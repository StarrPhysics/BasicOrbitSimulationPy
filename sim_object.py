from vector import Vector, xhat, yhat, zeroVec

class SimObject:
        """
        Class which defines the properties of an object in the simulation. 
        Used to add new objects to the simulation, and to access their properties.
        """
        name: str
        mass: float
        position: Vector
        velocity: Vector

        def __init__(self, 
                     position: Vector, 
                     velocity: Vector,
                     name: str = None, 
                     isStatic: bool = False, 
                     mass = 1.00,
                     ) -> None:
        
            self.name = name
            self.mass = mass
            self.isStatic = isStatic
            self.position = position
            self.velocity = velocity if not isStatic else zeroVec
