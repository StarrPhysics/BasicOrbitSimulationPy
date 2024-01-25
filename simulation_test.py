from simulator import Simulation as newSim

sim1 = newSim(G = 1, interval=100, max_real_time=0, max_sim_time=0, max_iterations=100, save_gif=True)

sim1.addObject([0,0], [0,0], isStatic=True)
sim1.addObject([1,0], [0,1])

print(str(sim1.getData()[0]))


#sim1.get_sim_data()[0].get_latest('test1', 'test2', 'test3')

#sim1.run()