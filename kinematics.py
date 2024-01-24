from data_handling import SimObject
from vector import Vector
import numpy as np

G = 1 # 6.67408e-11

class Kinematics:
    @classmethod
    def calculateMutualForce(cls, principleObject: SimObject, attractorObject: SimObject, G: float) -> Vector:
            """
            Calculates the mutual force between two objects.
            """
            r_vec: Vector       = principleObject.position - attractorObject.position # Radial direction pointing from source of attraction
            r_squared: float    = np.dot(r_vec, r_vec) # Magnitude**2 of radial vector
            force:  Vector      = - (G * principleObject.mass * attractorObject.mass / r_squared) * r_vec # Force calculation, which is opposite of radial direction

            return force
    @classmethod
    def updateSimObjectList(cls, dt: float, G: float, record: list[SimObject]) -> list[SimObject]:
        """
        Takes a list of `(class) SimObjects` and returns a list of `(class) SimObjects` with updated positions and velocities.

        This function can be improved, as there's redundencies in this calculation method. 
        """
        
        mutualForceRecord: list[list[Vector]] = [[None for _ in range(len(record))] for _ in range(len(record))]
        # ^^^^ Stores the mutual forces for recipricol use. The list requires a specific notation to be used properly.
        # The first entery is the index of the principleObject, and the second entry is the index of attractorObject.
        # Note that this index is with respect to the submitted list of `simObjects`.
        # So if we submit the following:
        #    mutualForceRecord[0][4]
        # The value aquired will be the force which points from the first object in the list to the 5th object in the list.
        # This means that the recipricol of the keys is the negitive of the resulting vector.
        # Although, not all enteries will be utalized due to the symmetry.
        # Number of calculations as a function of n where `n = len(record)` (the number of force causing objects)
        # Without Record Keeping: n^n
        # With Record Keeping: n!
        # Big improvement (I don't know how to use big O notation but this does the job)

        for (principleObj, i) in zip(record, range(len(record))):
            # Loops through each `simObject` in `record` to calculate the force of each `simObject` with the other `simObject`s.
            # The `principleObj` is the current `simObject` whose force is being determined. Think of the principle as the "Center of the Universe" so to speak

            sumOfForces: Vector = Vector([0.0,0.0]) # Sum of all forces acting on `principleObj`
            otherObjects: list[SimObject] = record[:i] + record[i + 1:] # List of all `simObjects` which are

            for (attractingObj, j) in zip(otherObjects, range(len(otherObjects))): # Removes current `simObject` from the record to avoid calculating force it has with itself
                # Loops through to build the `sumOfForces` by adding all mutual forces the `principleObj` feels from all the other `attractingObj`s
                
                force_vec: Vector
                # Checks to see if the mutual force has already been calculated
                if (force := mutualForceRecord[j][i]) is not None:
                     force_vec: Vector = -1 * force
                    # If so, flip it around (since we're transforming the orientation of the mutual force vector)
                else:
                    # If not, do the calculation and record the calculation for later use
                    mutualForceRecord[i][j] = (force_vec := cls.calculateMutualForce(principleObj, attractingObj, G))
    
                sumOfForces = np.add(sumOfForces, force_vec)
            
            # If the `simObject` is static, then it's position and velocity are not updated.
            # This is done after doing the calculations so that mutual forces can be calculated for other objects.
            if principleObj.isStatic:
                continue

            # updates the position and velocity of the two objects
            principleObj.position += (principleObj.velocity * dt) + (sumOfForces * (dt ** 2) / 2)
            principleObj.velocity += (sumOfForces * dt) / principleObj.mass
                
        return record