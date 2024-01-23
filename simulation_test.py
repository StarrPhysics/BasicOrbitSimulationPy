from simulator import Simulation as newSim

sim1 = newSim(G = 1, interval=20, max_real_time=0, max_sim_time=0, max_iterations=100, save_animation=True)

sim1.addObject([0,0], [0,0], isStatic=True)
sim1.addObject([1,0], [0,1])

sim1.run()