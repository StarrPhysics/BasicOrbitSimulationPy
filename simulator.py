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
from data_handling import SimObject, SimObjectList
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
    _animation: Animation.FuncAnimation = None

    # Contains list of simulation objects which are iterated over for calculations during the simulation runtime
    _sim_object_list: SimObjectList = SimObjectList()

    # Just a flag to keep track of whether the simulation is running or not
    _simulation_running: bool = False
    

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
            case 'interval':
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
                else:
                    self._interval = value
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
            case _:
                raise ValueError(f"Provided argument '{name}' is not recognized as a simulation parameter")
    
    def isRunning(self) -> bool:
        """
        Returns True if the simulation is running.
        """
        return self._simulation_running
    
    def getData(self) -> SimObjectList:
        """
        Safely accesses the current amount data stored in the simulation instance.
        """
        return str(self._sim_object_list)

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
        name = name or f"object{len(self._sim_object_list) + 1}"
        
        # Checks to see if `name` already exists as an object name in _data
        if len(self._sim_object_list) > 0:
            if name in [storedSimObject.name for storedSimObject in self._sim_object_list]:
                    raise Exception(f"Object with name `{name}` already exists in simulation.")

        self._sim_object_list.append(SimObject(
                                self,
                                position if isinstance(position, Vector) else Vector(position),
                                velocity if isinstance(velocity, Vector) else Vector(velocity),
                                name,
                                isStatic,
                                mass,
                                ))


    def run(self):
        """
        Executes the current instance of a simulation.
        """

        if self._display_animation: self._executeSimulation_MatPlotLib()
        else:                       self._executeSimulation_NoDisplay()
    
    def _executeSimulation_MatPlotLib(self):
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
            
        # Initalize `self.a_sim_object_listta._sim_time` and `self._sim_object_list._real_time` data for the current time:
        self._sim_object_list._sim_times.append(0.0)
        self._sim_object_list._real_times.append(datetime.now())

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
                    [vector[0] for vector in simObject._positions], # Aquires all x positions
                    [vector[1] for vector in simObject._positions], # Aquires all y positions
                    marker = 'o', # Object Marker
                    color = 'blue' if simObject.isStatic else 'red'
                )[0] for simObject in self._sim_object_list
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
            frameTime = int(round((datetime.now() - self._sim_object_list._real_times[-1]).total_seconds() * 1000, 0))
            self._sim_object_list._real_times.append(datetime.now())

            # Updates each `SimObject` in `_sim_object_list` with the latest data
            # This is the beating heart of the simulation's recursive cycle
            Kinematics.updateSimObjectList_Kinematics(self._sim_object_list, self._G, self._dt)
            Kinematics.updateSimObjectList_AnimationQuantities(self._sim_object_list)

            # Updates each simObjects line to update the graph
            largest_abs_val = 0

            for artist, simObject in zip(artists, self._sim_object_list):
                latest_positions = simObject._positions[-20:] if len(simObject._positions) >= 20 else simObject._positions
                latest_x = [vector[0] for vector in latest_positions]
                latest_y = [vector[1] for vector in latest_positions]
                print(latest_x)
                print(latest_y)
                exit()
                artist.set_data(latest_x, latest_y)

                
            
            axText.set_text(f'Iteration: {i}\nFrame Time: {frameTime}ms')
            ax.set_xlim(tuple(self._sim_object_list._x_limit))
            ax.set_ylim(tuple(self._sim_object_list._y_limit))

            # if self._max_sim_time != 0 and sum(self._data[-1][0].velocity) >= self._max
            # Simulation Time limites need to be implemented
            return (artists + [axText, ax]) 
                
        self._animation = Animation.FuncAnimation(fig, animate, interval=self._interval, blit=True)
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
                    self._animation.save(f'./{possibleName}', writer=writer)
                    break
                i += 1

    def _executeSimulation_NoDisplay(self):
        pass

    def _check_ConcludeSimulation(self):
        """
            Checks to see if the simulation has reached a conclusion.
            This is used to determine if the simulation should be terminated.
        """
        if self._max_iterations != 0 and len(self._data) >= self._max_iterations:
            print("Simulation finished.")
            print("Triggered By: Max Iterations")
            return True
        if self._max_real_time != 0 and (datetime.now() - self._simuationStartTime).seconds >= self._max_real_time:
            print("Simulation finished.")
            print("Triggered By: Max Real-Time")
            return True
        # if self._max_sim_time != 0 and sum(self._data[-1][0].velocity) >= self._max_sim_time:
        #     print("Simulation finished.")
        #     print("Triggered By: Max Simulation Time")
        #     return True
    
if __name__ == "__main__":
    print("This is a file that is meant to be imported, not run directly.")