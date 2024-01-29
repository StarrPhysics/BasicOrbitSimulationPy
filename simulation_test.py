from simulator import Simulation as newSim
from data_handling import SimObjectList

sim1 = newSim(G = 1, interval=500, max_real_time=0, max_sim_time=0, max_iterations=100, save_gif=False)

sim1.addObject([0,0], [0,0])
sim1.addObject([1,0], [0,1])

sim1.run()