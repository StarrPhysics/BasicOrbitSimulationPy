
### External Modules ###
from matplotlib import style
import matplotlib.pyplot as plt
import matplotlib.animation as Animation
from datetime import datetime
from matplotlib.text import Text as plotText
from typing import Union
import numpy as np
from os import listdir as os_listdir

### Project Modules ###
from vector import Vector, xhat, yhat, zeroVec
from data_handling import SimObject
from kinematics import Kinematics

class Simulation:
    """
    <Description To Be Added>

    """
    _dt: float
    _G: float
    
    _interval: int
    _display_animation: bool

    # Simulation Conclusion Conditions
    _max_iterations: int
    _max_real_time: int
    _max_sim_time: float

    _save_gif: bool
    _gif_name: str

    # Runtime Variables
    __simuationStartTime: datetime
    __previousTime: datetime

    __animation: Animation.FuncAnimation = None
    __simulation_data: list[SimObject] = [[]]

    #__sim_time: list[float] # List of number of sim_time seconds since simulation began, updated 


    def __init__(self, *,
                  dt = 0.01,                # .01 second default
                  G = 6.67428e-11,
                  display_animation = True,
                  save_animation = False,
                  interval = 300,           # 300 millisecond default
                  max_iterations = 1000,    # 1000 iteration default
                  max_real_time = 60*3,     # Three minute default
                  max_sim_time = 0          # No default
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
        self.set_dt(dt)
        self.set_G(G)
        self.set_interval(interval)
        self.set_display_animation(display_animation)
        self.set_save_gif(save_animation)
        self.set_max_iterations(max_iterations)
        self.set_max_real_time(max_real_time)
        self.set_max_sim_time(max_sim_time)
    
    ### get/set methods ###
    def get_dt(self): return self.dt
    def set_dt(self, dt): #
        if dt <= 0:
            print('Warning, time step cannot be less than or equal to 0.')
            print('Please submit another value.')
        self._dt = dt
    
    def get_G(self): return self._G
    def set_G(self, G): self._G = G

    def get_interval(self): self._interval
    def set_interval(self, interval: int):
        if self.__animation is not None:
            print('Warning, animation interval cannot be changed while an animation is running.')
            print('Please submit value before starting the animation.')
            # To be honest, changing the interval during the animation probably wont do anything, 
            # but I can't imagine why somebody would wanna do this and it seems potentially problematic 
            # in the future depending on how the program develops
        if interval <= 40:
            if interval < 0:
                print('Values for the interval cannot be less than 0.')
                print('Please submit another value.')
                return
            print('WARNING: Setting the interval lower than 40 can cause the animation to lag.')
            print('Ok: Continute, Cancel: Exit >>> ', end='')
            userInput = input()
            if userInput.lower() == 'ok':
                pass
            else:
                return
            
        self._interval = interval
    
    def get_display_animation(self): self._display_animation
    def set_display_animation(self, display_animation: bool):
        if self.__animation is not None:
            print('Warning, animation display cannot be changed while an animation is running.')
            print('Please submit a value before starting the animation.')
            return

        self._display_animation = display_animation

    def get_save_gif(self): return self._save_gif
    def set_save_gif(self, save_gif: bool):
        if self.__animation is not None:
            print('Warning, gif saving cannot be changed while an animation is running.')
            print('Please submit a value before starting the animation.')
            return
        if 'pillow' not in Animation.writers.list():
            print('Warning, gif saving requires the pillow library.')
            print('Please install pillow and try again.')
            print('Info avalable at: https://python-pillow.org')
            return

        self._save_gif = save_gif

    def get_max_iterations(self): self._max_iterations
    def set_max_iterations(self, max_iterations: int):
        if self.__animation is not None:
            print('Warning, max_iterations cannot be changed while an animation is running.')
            print('Please submit value before starting the animation.')
            return
        if max_iterations < 0:
            print('Warning, max_iterations cannot be less than 0.')
            print('Please submit another value.')
        
        self._max_iterations = max_iterations
    
    def get_max_real_time(self): self._max_real_time
    def set_max_real_time(self, max_real_time: float): 
        if self.__animation is not None:
            print('Warning, `max_real_time` cannot be changed while an animation is running.')
            print('Please submit value before starting the animation.')
            return
        if max_real_time < 0:
            print('Warning, max_real_time cannot be less than 0.')
            print('Please submit another value.')

        self._max_real_time = max_real_time
    
    def get_max_sim_time(self): self._max_sim_time
    def set_max_sim_time(self, max_sim_time: float):
        if self.__animation is not None:
            print('Warning, `max_sim_time` cannot be changed while an animation is running.')
            print('Please submit value before starting the animation.')
            return
        if max_sim_time < 0:
            print('Warning, max_sim_time cannot be less than 0.')
            print('Please submit another value.')
        
    def addObject(self,
                  position: Union[list[float], Vector],
                  velocity: Union[list[float], Vector],
                  *,
                  name: str = None,
                  isStatic: bool = False,
                  mass: float = 1.00
                  ):
        """
        Adds an object to the simulation before runtime.

        Parameters
        ----------
        position : list[float] or Vector
        
        Example of how to use::

            sim = Simulation()
        
            simObject = SimObject(isStatic = False, position=[0,0], name='object1')
        
            sim.addObject(simObject)
        """

        # Below code could be improved
        if name is None: # Gives the `SimObject` a unique name if it uses the generic name `object`.
            name = f"object{len(self.__simulation_data[0]) + 1}"
        
        if len(self.__simulation_data[0]) > 0:
            for storedSimObject in self.__simulation_data[0]: # Checks to see if name is unique, which must be the case for __updateSimObjectKinematics to work correctly
                if name == storedSimObject.name:
                    raise Exception(f"Object with name `{name}` already exists in simulation.")
                

        newSimObject = SimObject(
                                self,
                                position if isinstance(position, Vector) else Vector(position), 
                                velocity if isinstance(position, Vector) else Vector(velocity),
                                name,
                                isStatic,
                                mass,
                                )
            
        self.__simulation_data[0].append(newSimObject)

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
        self.__simuationStartTime = datetime.now()

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
                )[0] for simObject in self.__simulation_data[0]
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