from data_handling import SimObject, SimObjectList
from vector import Vector
import numpy as np
import numpy.linalg as linalg

class Kinematics:
    @classmethod
    def calculateMutualForce(cls, principleObject: SimObject, attractorObject: SimObject, G: float) -> Vector:
            """
            Calculates the mutual force between two objects.
            """

            r_vec: Vector       = principleObject._positions[-1] - attractorObject._positions[-1] # Radial vector pointing from source of attraction
            r_squared: float    = np.dot(r_vec, r_vec) # Magnitude**2 of radial vector
            force:  Vector      = - (G * principleObject.mass * attractorObject.mass / r_squared) * r_vec # Force calculation, which is opposite of radial direction

            return force
    @classmethod
    def updateSimObjectList_AnimationQuantities(cls, simObjectList: SimObjectList):
        """
        Updates values in `simObjectList` assosiated with graphical representations of the simulation objects.
        For example: the center of the simulated objects, or the furthest deviation these objects have from the center.
        """
        # Updates `SimObjectList._center` with the average of the x and y positions 
        simObjectList._center = np.sum(simObjectList.positions(), axis=1)/len(simObjectList.positions())
        
        # Updates the `SimObjectList._max_center_deviation` with the largest center-simObject displacement vector's magnitude
        simObjectList._max_center_deviation = max([linalg.norm(SimObject_position - simObjectList._center) for SimObject_position in simObjectList.positions()])
        
        simObjectList._x_limit = [simObjectList._center[0] - simObjectList._max_center_deviation, simObjectList._center[0] - simObjectList._max_center_deviation]
        simObjectList._y_limit = [simObjectList._center[1] - simObjectList._max_center_deviation, simObjectList._center[1] + simObjectList._max_center_deviation]
    
    @classmethod
    def updateSimObjectList_Kinematics(cls, simObjectList: SimObjectList, G: float, dt: float) -> None:
        """
        Takes an instance of the `SimObjectList` Class by reference and updates the kinematic values assosiated with each `SimObject`.
        """

        previouslyCalulatedMutualForces: list[list[Vector]] = [[None for _ in range(len(simObjectList) - i)] for i, _ in enumerate(simObjectList)]
        # ^^^^ Stores calculated mutual forces for repeaded use in recipricol cases; all in all, it's purpose is to avoid redundent re-calculations of mutual force.
        # The list requires a specific notation to be used properly. As desribed below:
        #   The first entery is the index of the principleObject, and the second entry is the index of attractorObject.
        #   Note that the index used here is with respect to the index of each object `simObjectList_Reference` as an identifier.
        #   Suppose we execute the following code in this scope:
        #       >>> previouslyCalulatedMutualForces[0][4]
        #   The value aquired will be the force whose tail begins at object `0` and points to object `4`.
        #   In other words, we will aquire the force influence object `4` has on `0`, which suggests that each entry takes the point of view of the each object and the `pull` each object feels.
        #   If the matrix was a square of dimentions `len(simObjectList_Reference)`, then the recipricol of the keys would be is the negitive of the resulting vector;
        #   Since the force each pair of objects experience is the same, but the direction of those forces are opposite (but point inward): ◯⟶ ⟵◯
        #   Although, this is not a square matrix, and rather it's a triangular matrix, since:
        #       - The use of recipricol enteries is useless and unesseary since `forceMatrix[0][1] = neg * forceMatrix[0][1]`
        #       - We will never calculate a force forceMatrix[i][i] since no objects will be allowed to cause a force on themselves.
        #   One could say that we are utalizing an Upper-Left, Triangular, Hollow Matrix. Aint that a god damn mouth full.
        #   Here is a visual representation of this matrix with 4 simObjects:
        #
        #        ╔═══╦══════╦══════╦══════╦══════╗
        #   j    ║   ║ 0    ║ 1    ║ 2    ║ 3    ║ i index, first object
        # index, ╠═══╬══════╬══════╬══════╬══════╣
        # second ║ 0 ║ None ║      ║      ║      ║
        # object ╠═══╬══════╬══════╬══════╬══════╣
        #        ║ 1 ║ 1.0  ║ None ║      ║      ║
        #        ╠═══╬══════╬══════╬══════╬══════╣
        #        ║ 2 ║ 1.0  ║ 1.0  ║ None ║      ║
        #        ╠═══╬══════╬══════╬══════╬══════╣
        #        ║ 3 ║ 1.0  ║ 1.0  ║ 1.0  ║ None ║
        #        ╚═══╩══════╩══════╩══════╩══════╝
        #
        #   Notice that there's a lot of enteries per column, and that they slowly diminish over time
        #   This is because in the first iteration, no previous calculations have been done, and so every calculation must be done manually;
        #   But towards the last iteration, almost every calculation has been done already, so no manual calculations have to be done and the matrix can be fully utalized.
        # 
        # Number of calculations as a function of n where `n = len(record)` (the number of force causing objects)
        # Without Record Keeping: n^n
        # With Record Keeping: n!
        # Big improvement (I don't know how to use big O notation but this does the job)
        


        for (i, principleObj) in enumerate(simObjectList):
            # Loops through each `simObject` in `record` to calculate the force of each `simObject` with the other `simObject`s.
            # The `principleObj` is the current `simObject` whose force is being determined. Think of the principle as the "Center of the Universe" so to speak
            
            sumOfForces: Vector = Vector([0.0,0.0]) # Sum of all forces acting on `principleObj`

            for (j, attractingObj) in enumerate(simObjectList[:i]):
                # For all objects where j < i, mutual force has been previously calculated at `previouslyCalulatedMutualForces[j][i]`
                # The value becomes negitive since the force which effected it is opposite of the force it effects
                sumOfForces += -1 * previouslyCalulatedMutualForces[j][i]

            for (j, attractingObj) in enumerate(simObjectList[i+1:], start=i+1): 
                # For all objects where j > i, mutual force must be calculated and stored at `previouslyCalulatedMutualForces[i][j]`
                #print(principleObj._object_simulation_data.position)
                #print(attractingObj._object_simulation_data.position)
                
                force = cls.calculateMutualForce(principleObj, attractingObj, G)
                previouslyCalulatedMutualForces[i][j] = force
                sumOfForces += force

                """force_vec: Vector
                
                # Checks to see if the mutual force has already been calculated
                if (force := mutualForceRecord[j][i]) is not None:
                     force_vec: Vector = -1 * force
                    # If so, flip it around (since we're transforming the orientation of the mutual force vector)
                else:
                    # If not, do the calculation and record the calculation for later use
                    mutualForceRecord[i][j] = (force_vec := cls.calculateMutualForce(principleObj, attractingObj, G))
    
                sumOfForces = np.add(sumOfForces, force_vec)"""
            
            # If the `simObject` is static, then it's position and velocity are not updated.
            # This is done after doing the calculations so that mutual forces can be calculated for other objects.
            if principleObj.isStatic:
                continue

            # updates the position and velocity of the two objects
            nextPosition: Vector = principleObj._positions[-1]  + (principleObj._velocities[-1] * dt) + (sumOfForces * (dt ** 2) / 2)
            nextVelocity: Vector = principleObj._velocities[-1] + (sumOfForces * dt) / principleObj.mass

            principleObj._positions.append(nextPosition)
            principleObj._velocities.append(nextVelocity)
            principleObj._speeds.append(linalg.norm(nextVelocity))

            
            
