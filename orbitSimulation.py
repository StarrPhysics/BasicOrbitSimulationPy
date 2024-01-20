from matplotlib import style
import matplotlib.pyplot as plt
import matplotlib.animation as Animation
from matplotlib.text import Text as plotText
# from typing import Union <-- Unused thus far
import numpy as np

G = 1 # 6.67408e-11

class Vector(np.ndarray):
    """
    Redefines the `numpy.array` class to make it easier to work with.
    All properties are inherited, but default data type is changed to `float64`.
    """
    def __new__(cls, object):
        obj = np.asarray(object, dtype=np.float64).view(cls)
        return obj

class SimObject:
        """
        Class which defines the properties of an object in the simulation. 
        Used to add new objects to the simulation, and to access their properties.
        """
        name: str = ''
        mass: float = 1.00
        position: Vector = Vector([0,0])
        velocity: Vector = Vector([0,0])

        def __init__(self, name = 'object', isStatic: bool = False, mass = 1.00, position = [0,0], velocity = [0,0]) -> None:
            self.name = name
            self.mass = mass
            self.isStatic = isStatic
            self.position = Vector(position)
            self.velocity = Vector(velocity) if not isStatic else Vector([0,0])

class Simulation:
    """
    Class which allows for the establishment of a simulation.
    """

    refreshRate: int = 1000
    """
    The number of times per second the animation is updated in milliseconds.
    
    Caution the use of low values if `displayLive` is true.
    """

    displayAnimation: bool = True
    """
    Determines if the animation is displayed. Display is supported by `matplotlib.animation`.
    """

    maxIterations: int = 1000
    """
    Number of iterations before the simulation concludes.
    
    Caution the use of large values, as memory is aggregated during the simulation's execution.
    """

    animation: Animation.FuncAnimation = None
    """
    If `displayAnimation` is `True`, then this variable will inhertic the animation object provided by `animation.`
    """

    data: list[list[SimObject]] = [[]]
    """
    Array which contains the data produced by the simulation.
    """

    dt: float = 0.01

    def __init__(self, refreshRate = 1000, displayAnimation = True, maxIterations = 1000, dt = 0.01) -> None:
        self.refreshRate = refreshRate
        self.displayAnimation = displayAnimation
        self.maxIterations = maxIterations
        self.dt = dt

    def addObject(self, simObject: SimObject):
        """
        Adds an object to the simulation.
        
        Example of how to use::

            sim = Simulation()
        
            simObject = SimObject(isStatic = False, position=[0,0], name='object1')
        
            sim.addObject(simObject)
        """

        # Following code has issues that could be frustraiting for users. Will adjust later 

        if simObject.name == 'object': # Gives the `SimObject` a unique name if it uses the generic name `object`.
            simObject.name = f"object{len(self.data[0]) + 1}"
        
        if len(self.data[0]) > 0:
            for storedSimObject in self.data[0]: # Checks to see if name is unique, which must be the case for __updateSimObjectKinematics to work correctly
                if simObject.name == storedSimObject.name:
                    raise Exception(f"Object with name {simObject.name} already exists in simulation.")
            
        self.data[0].append(simObject)

    def run(self):
        """
        Executes the simulation with the current settings.
        """

        if self.displayAnimation:
            self.__executeDisplayedSimulation()
        else:
            self.__executeNumbericalSimulation()
    
    def __executeDisplayedSimulation(self):
        # Set up video encoding
        Writer = Animation.writers['pillow']
        writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

        # Sets up matplotlib graph
        style.use('fivethirtyeight')
        fig     = plt.figure()
        ax = fig.add_subplot(1,1,1)
        axText: plotText = ax.text(0.05, 0.95, f'', transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.set_title('Orbit Simulation')

        plotLines: list[plt.Line2D] = []

        for simObject in self.data[0]: # Initalize plot
            plotLines.append(ax.plot(simObject.position[0], simObject.position[1], 'o', color = 'blue' if simObject.isStatic else'red')[0])


        def animate(i, simInstance: Simulation):
            # Updates the graph with the latest simulated data


            # Uses the latest data to determine new positions/velocities
            simInstance.data.append( data := self.__updateSimObjectKinematics(simInstance.data[-1]) )
            
            # Updates each simObjects line to update the graph
            largest_abs_val = 0

            for line, objectData in zip(plotLines, data):
                (x,y) = line.get_data()

                x = np.concatenate((x, [objectData.position[0]]), axis=0)
                y = np.concatenate((y, [objectData.position[1]]), axis=0)

                if len(x) > 50:
                    x = x[-50:]
                    y = y[-50:]
                

                if abs(y.max()) > largest_abs_val: largest_abs_val = abs(y.max())
                if abs(x.max()) > largest_abs_val: largest_abs_val = abs(x.max())

                line.set_data(x, y)

            axText.set_text(f'Iteration: {i}')
            ax.set_xlim(-largest_abs_val * 1.33, largest_abs_val * 1.33)
            ax.set_ylim(-largest_abs_val * 1.33, largest_abs_val * 1.33)

            if i + 1 >= simInstance.maxIterations:
                simInstance.animation.pause()
                print("Animation finished.")
            

        self.animation = Animation.FuncAnimation(fig, animate, fargs=[self], interval=self.refreshRate, blit=False)
        plt.show()
        
        # Uncomment if you wish to save a video
        # self.animation.save('./example.gif', writer=writer)


    def __executeNumbericalSimulation(self):
        pass

    def __updateSimObjectKinematics(self, record: list[SimObject]) -> list[SimObject]:
        """
        Takes a list of `(class) SimObjects` and returns a list of `(class) SimObjects` with updated positions and velocities.

        This function can be improved, as there's redundencies in this calculation method. 
        """
        
        mutualForceRecord: dict[str, dict[str, float]] = {}
        # ^^^^ Stores the mutual forces for recipricol use. The dictionary requires a specific notation to be used properly.
        # The first entery is the name of the principleObject, and the second entry is the attractorObject.
        # So if we submit the following:
        #    mutualForceRecord['object1']['object2']
        # The value aquired will be the force which points from `object1` to `object2`.
        # This means that the recipricol of the keys is the negitive of the resulting vector.


        for (principleObj, i) in zip(record, range(len(record))):
            # Loops through each `simObject` in `record` to calculate the force of each `simObject` with the other `simObject`s.
            # The `principleObj` is the current `simObject` whose force is being determined. Think of the principle as the "Center of the Universe" so to speak

            mutualForceRecord: dict[str, dict[str, Vector]] = {} # Dictionary containing all previously calulcated, mutual forces
            # Number of calculations as a function of n where `n = len(record)` (the number of force causing objects)
            # Without Record Keeping: n^n
            # With Record Keeping: n!
            # Big improvement (I don't know how to use big O notation but this does the job)

            sumOfForces: Vector = Vector([0.0,0.0]) # Sum of all forces acting on `principleObj`

            for attractingObj in (record[:i] + record[i + 1:]): # Removes current `simObject` from the record to avoid calculating force it has with itself
                # Loops through to build the `sumOfForces` by adding all mutual forces the `principleObj` feels from all the other `attractingObj`s
                
                force_vec: Vector = Vector([0.0,0.0])
                # Checks to see if the mutual force has already been calculated
                if (attractingObj.name in mutualForceRecord) and (principleObj.name in mutualForceRecord[principleObj.name]):
                    # If so, flip it around (since we're transforming the orientation of the mutual force vector)
                    force_vec: Vector = -1 * mutualForceRecord[attractingObj.name][principleObj.name]
                else:
                    # If not, do the calculation and record the calculation for later
                    force_vec: Vector = self.__mutualForce(principleObj, attractingObj)
                    mutualForceRecord[principleObj.name] = {f'{[attractingObj.name]}' : force_vec}
                    

                sumOfForces = np.add(sumOfForces, force_vec)
            

            
            # If the `simObject` is static, then it's position and velocity are not updated.
            # This is done after doing the calculations so that mutual forces can be calculated for other objects.
            if principleObj.isStatic:
                continue
            

            # updates the position and velocity of the two objects
            principleObj.position += (principleObj.velocity * self.dt) + (sumOfForces * (self.dt ** 2) / 2)
            principleObj.velocity += (sumOfForces * self.dt) / principleObj.mass
                
        return record

    @staticmethod
    def __mutualForce(principleObject: SimObject, attractorObject: SimObject) -> Vector:
        """
        Calculates the mutual force between two objects.
        """
        r_vec: Vector       = principleObject.position - attractorObject.position # Radial direction pointing from source of attraction
        r_squared: float    = np.dot(r_vec, r_vec) # Magnitude**2 of radial vector
        force:  Vector      = - (G * principleObject.mass * attractorObject.mass / r_squared) * r_vec # Force calculation, which is opposite of radial direction

        return force
    
if __name__ == "__main__":
    print("This is a file that is meant to be imported, not run directly.")