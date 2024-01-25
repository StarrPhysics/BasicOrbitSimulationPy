### External Modules ###
from matplotlib import style
import matplotlib.pyplot as plt
import matplotlib.animation as Animation
from datetime import datetime
from matplotlib.text import Text as plotText
from typing import Union, TypeVar, Annotated
import numpy as np
from os import listdir as os_listdir

### Project Modules ###
from vector import Vector, xhat, yhat, zeroVec
from data_handling import SimObject
from kinematics import Kinematics

class Simulation:
    """
    An object oriented gravity simulation/sandbox library.

    Library use is intended to be an accessable way of producing visual and numeric expression of newtonian gravitational mechanics.
    """
    # Following Variables and their use are explained in Simulation.__init__()
    _dt: float
    _G: float
    _interval: int
    _display_animation: bool
    _max_iterations: int
    _max_real_time: int
    _max_sim_time: float
    _save_gif: bool

    _gif_name: str # <--- Variable for a feature that has yet to be integrated

    # Contains the instance of the matplotlib animation object which is created when the display is established
    __animation: Animation.FuncAnimation = None

    # Contains list of simulation objects which are iterated over for calculations during the simulation runtime
    __simulation_data: list[SimObject] = []

    # List of number of sim_time seconds since simulation began, updates every time a calculation cycle is executed 
    __sim_time: list[float] 

    # List of number of real_time seconds since simulation began, updates every time a calculation cycle is executed 
    __real_time: list[float]

    # Just a flag to keep track of whether the simulation is running or not
    __simulation_running: bool = False
    

    def __init__(self, *,
                  dt: float = 0.01,                # .01 second default
                  G: float = 6.67428e-11,
                  display_animation: True = True,
                  save_gif: bool = False,
                  interval: int = 300,           # 300 millisecond default
                  max_iterations: int = 1000,    # 1000 iteration default
                  max_real_time: float = 60.0*3, # Three minute default
                  max_sim_time: float = 0.0      # No default
                ) -> None:
        r"""
        Parameters
        ----------
        `dt : float (seconds)` 
            The time step between calculations in simulation time.
        `G : float (Newtons meters^2/kilograms^2)`
            The gravitational constant. Default is the standard value of the International Astronomical 
            Union, which is ideal for physically accurate simulations. For visual demonstations, a value
            like 1 can be used.
        `display_animation : bool`
            Whether or not the simulation is complimented by an animation rendered using matplotlib. 
            For maximum performance and calculation speed, set to false.
        `save_gif : bool`
            Whether or not to save the animation as a gif. If set to `True`, the animation will be saved.
        `interval : int (milliseconds)`
            The amount of time between each frame of the animation. If `display_animation` is set to
            `False`, this value has no consequence to the simulation runtime. CAUTION: Setting this value
            lower then `60` can lag matplotlib's animation rendering.
        `max_iterations : int`
            The maximum number of iterations in the simulation cycle before the simulation concludes.
            If set to 0, the simulation will run indefinitly unless another stopping condition is met or
            unless the user kills the program.
        `max_real_time : float (seconds)`:
            The maximum amount of "real time" that the simulation will run for before the simulation 
            concludes. If set to 0, the simulation will run indefinitly unless another stopping condition 
            is met or unless the user kills the program.
        `max_sim_time : float (seconds)`: <--- NEEDS TO BE IMPLEMENTED
            The maximum amount of "simulation time" that the simulation will run for before the simulation
        """
        # Strange list nonsense is to avoid passing 'self' into `set_params_by_list()`.
        self.set_params_by_list([(k,v) for (k,v) in locals().items() if k != 'self'])


    def set_params_by_list(self, parameters: list[tuple]) -> None:
        """
        Allows for lists of parameters to be set in a single line. Used mostly for internal use, but can be used externally.
        """
        if self.isRunning():
            print('Warning, simulation parameters cannot be changed or set while the simulation is running.')
            print('Please submit new parameters before starting the simulation.')
            return
        
        for (k,v) in parameters: self.set_param(k,v) # Loops through the list of tuples and sets each parameter using the `set_param` function.
    

    def set_param(self, name: str, value):
        """
        Allows for the safe setting of simulation parameters.
        """
        if self.isRunning():
            print('Warning, simulation parameters cannot be changed or set while the simulation is running.')
            print('Please submit new parameters before starting the simulation.')
            return
        
        # Used to ensure the input parameter is a type in `checkValueType()`. I guess its a type type? I don't know anymore
        AnyType = TypeVar('AnyType') 

        # Basically is the `isinstance` function with extra steps
        def checkValueType(parameterName, givenValue: object, expectedType: AnyType):
                if not isinstance(givenValue, expectedType):
                    raise TypeError(f'Warning, parameter `{parameterName}` is of value "{givenValue}", which is not of allowed type {expectedType}.')
                
        match name:
            case 'dt':
                checkValueType(name, value, float)
                if value <= 0:
                    print('Warning, time step cannot be less than or equal to 0.')
                    print('Please submit another value.')
                    return
                self._dt = value
            case 'G':
                checkValueType(name, value, Union[float,int])
                if value <= 0: raise ValueError('Warning, gravitational constant cannot be less than or equal to 0.')
                self._G = value
            case 'display_animation':
                checkValueType(name, value, bool)
                self._display_animation = value
            case 'save_gif':
                checkValueType(name, value, bool)
                self._save_gif = value
            case 'set_interval':
                checkValueType(name, value, int)
                if value < 0:
                    print('Warning, animation interval cannot be less than 0.')
                    print('Please submit another value.')
                    return
                elif value <= 80:
                    print('WARNING: Setting the interval lower than 40 can cause unstable animation rendering.')
                    while True:
                        print("Press 'C' to assign the current value, or 'X' to skip this value assignment: ", end='')
                        if input().upper() == 'C': self._interval = value; return
                        elif input().upper() == 'X': return
                        else: print("Invalid input. Please try again.\n")
            case 'max_iterations':
                checkValueType(name, value, int)
                if value < 0:
                    print('Warning, maximum iterations cannot be less than 0.')
                    print('Please submit another value.')
                    return
                self._max_iterations = value
            case 'max_real_time':
                checkValueType(name, value, Union[float,int])
                if value < 0.0:
                    print('Warning, maximum real-time cannot be less than 0.')
                    print('Please submit another value.')
                    return
                self._max_real_time = value
            case 'max_sim_time':
                checkValueType(name, value, Union[float,int])
                if value < 0.0:
                    print('Warning, maximum simulation-time cannot be less than 0.')
                    print('Please submit another value.')
                    return
                self._max_sim_time = value
    
    def isRunning(self) -> bool:
        """
        Returns True if the simulation is running.
        """
        return self.__simulation_running
    
    def getData(self, objectSelectionMethod: Union[int, str, list[str], Annotated[tuple[int], 2]] = None) -> Union[SimObject, list[SimObject]]:
        """
        Safely accesses the current amount data stored in the simulation instance
        """
        if objectSelectionMethod == None:
             # Implies the user has no preference, and so all `SimObject`s are provided
            return self.__simulation_data
        elif isinstance(objectSelectionMethod, int):
            # Implies the user intends to access a specific object by index
            return self.__simulation_data[objectSelectionMethod]
        elif isinstance(objectSelectionMethod, str):
            # Implies the user intends to access a specific object by name
            pass
        elif isinstance(objectSelectionMethod, list[str]):
            # Implies the user intends to access a list of objects by name
            return [simObject for simObject in self.__simulation_data if simObject.name in objectSelectionMethod]
        elif isinstance(objectSelectionMethod, Annotated[tuple[int], 2]):
            # Implies user wants to access a substring of objects between two indicies:
            start, finish = objectSelectionMethod
            return self.__simulation_data[start:finish]


    def addObject(self,
                  position: Union[list[float], Vector],
                  velocity: Union[list[float], Vector],
                  *,
                  name: str = None,
                  isStatic: bool = False,
                  mass: float = 1.00
                  ):
        """
        Adds an object to the simulation for .

        Parameters
        ----------
        position : list[float] or Vector
        
        Example of how to use::

            sim = Simulation()
        
            sim.addObject([0,0], [0,1], mass = 2.0, isStatic = True)
        """

        # !--- Below code could be improved ---!

        # Produces a unique name for the soon-to-be `SimObject`.
        name = name or f"object{len(self.__simulation_data) + 1}"
        
        # Checks to see if `name` already exists as an object name in __simulation_data
        if len(self.__simulation_data) > 0:
            if name in [storedSimObject.name for storedSimObject in self.__simulation_data]:
                    raise Exception(f"Object with name `{name}` already exists in simulation.")
            
        self.__simulation_data.append(SimObject(
                                    self,
                                    position if isinstance(position, Vector) else Vector(position), 
                                    velocity if isinstance(position, Vector) else Vector(velocity),
                                    name,
                                    isStatic,
                                    mass,
                                    )
                                )

    def run(self):
        """
        Executes the current instance of a simulation.
        """

        if self._display_animation: self.__executeSimulation_MatPlotLib()
        else:                       self.__executeSimulation_NoDisplay()
    
    def __executeSimulation_MatPlotLib(self):
        # Check if Stopping Methods are Enabled
        if self._max_iterations == 0 and self._max_real_time == 0 and self._max_sim_time == 0.0:
            print('WARNING: You currently do not have any stopping methods enabled.')
            print('Ok: Continute, Cancel: Exit >>> ', end='')
            userInput = input()
            if userInput.lower() == 'ok':
                pass
            else:
                return
            
        #### At this point going forward, the animation is set to occur unless ####
        #### an uncaught exception is raised                                   ####
        
        # Used to compare to see if _max_real_time has been exceded in the animation() function
        self.__simulationStartTime = datetime.now()

        # Used to calculate framerate for performance metrics
        self.__previousTime = datetime.now()

        # Set up video encoding
        if self._save_gif:
            Writer = Animation.writers['pillow']
            writer = Writer(fps=15, metadata=dict(artist=''), bitrate=1800)

        # Sets up matplotlib graph
        style.use('fivethirtyeight')
        fig = plt.figure()
        fig.set_size_inches(6, 6)
        ax = fig.add_subplot(1,1,1)
        ax.set_title('Orbit Simulation')

        # Creates a text box for the animation. Performance metrics are intended to be shown.
        axText: plotText = ax.text(0.05, 0.95, f'', 
                                   transform=ax.transAxes, 
                                   fontsize=14, 
                                   verticalalignment='top', 
                                   bbox=dict(boxstyle='round', 
                                             facecolor='wheat', 
                                             alpha=0.5)
                                    )
        
        # Contains every line object, which is currently 1:1 with the number of sim objects
        artists: list[plt.Line2D] = [
            ax.plot(
                    simObject.position[0], # Inital x position
                    simObject.position[1], # Inital y position
                    marker = 'o', # Object Marker
                    color = 'blue' if simObject.isStatic else 'red'
                )[0] for simObject in self.__simulation_data
            ] 


        def animate(i): # Callback Function which updates the graph with the latest simulated data
            """
                The animation function is currently the limiting factor for simulation speed.
                Ideally in the future, the execution cycle for the simulation can be made to run
                independently of the animation, so that the lasest and most accurate information
                can be generated prior to the completion of the animation cycle. For example, one
                might be able to calculate 100 data points per second in the simulation without 
                requiring the animation running 10 ms per frame, which is just about helpless
                with the use of matplotlib.animation lol. From videos I've seen, the best one can
                do is to optomize the animation speed is enable blitz mode, which brought the animation
                runtime down to 20ms.
            """
            frameTime = int(round((datetime.now() - self.__previousTime).total_seconds() * 1000, 0))

            self.__previousTime = datetime.now()

            # Uses the latest data to determine new positions/velocities
            # While assigning this data to newObjectData
            # Followed by appending this data to __simulation_data
            self.__simulation_data.append( 
                newObjectData := Kinematics.updateSimObjectList(self._dt, self._G, self.__simulation_data[-1])
            )
            
            # Updates each simObjects line to update the graph
            largest_abs_val = 0

            for artist, objectData in zip(artists, newObjectData):
                (x, y) = objectData.position
                
                # (vel_x, vel_y) = (objectData.velocity[0], objectData.velocity[1])
                # abs_vel = np.linalg.norm(objectData.velocity)
                # vel_unit_vector = abs_vel
                (x_list,y_list) = artist.get_data()

                x_list = np.concatenate((x_list, [x]), axis=0)
                y_list = np.concatenate((y_list, [y]), axis=0)
                

                """
                Gonna add later
                plt.arrow(x,
                          y,
                          newX+newObjectData.,4,width=0.2)

                """
                
                if len(x_list) > 20:
                    x_list = x_list[-20:]
                    y_list = y_list[-20:]

                if abs(y_list.max()) > largest_abs_val: largest_abs_val = abs(y_list.max())
                if abs(x_list.max()) > largest_abs_val: largest_abs_val = abs(x_list.max())

                artist.set_data(x_list, y_list)
            
            axText.set_text(f'Iteration: {i}\nFrame Time: {frameTime}ms')
            ax.set_xlim(-largest_abs_val * 1.33, largest_abs_val * 1.33)
            ax.set_ylim(-largest_abs_val * 1.33, largest_abs_val * 1.33)

            # if self._max_sim_time != 0 and sum(self.__simulation_data[-1][0].velocity) >= self._max
            # Simulation Time limites need to be implemented
            return tuple(artists)
        
        self.__animation = Animation.FuncAnimation(fig, animate, interval=self._interval, blit=False, cache_frame_data=False)
        plt.show()
        
        # Saves the animation if the user has enabled it
        # Also checks to see if the output needs to be written a unique name
        # to avoid overwritting consecutive executions.
        if self._save_gif:
            i = 0
            while True:
                possibleName = f'output{i}.gif'
                if i == 100: print('Bruh what the hell')
                if i == 200: print('Chill out on the files my guy')
                if possibleName not in os_listdir('./'):
                    self.__animation.save(f'./{possibleName}', writer=writer)
                    break
                i += 1

    def __executeSimulation_NoDisplay(self):
        pass

    def __check_ConcludeSimulation(self):
        """
            Checks to see if the simulation has reached a conclusion.
            This is used to determine if the simulation should be terminated.
        """
        if self._max_iterations != 0 and len(self.__simulation_data) >= self._max_iterations:
            print("Simulation finished.")
            print("Triggered By: Max Iterations")
            return True
        if self._max_real_time != 0 and (datetime.now() - self.__simuationStartTime).seconds >= self._max_real_time:
            print("Simulation finished.")
            print("Triggered By: Max Real-Time")
            return True
        # if self._max_sim_time != 0 and sum(self.__simulation_data[-1][0].velocity) >= self._max_sim_time:
        #     print("Simulation finished.")
        #     print("Triggered By: Max Simulation Time")
        #     return True
    
if __name__ == "__main__":
    print("This is a file that is meant to be imported, not run directly.")