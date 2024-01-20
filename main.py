from orbitSimulation import Simulation, SimObject

if __name__ == "__main__":
    sim = Simulation(dt = .1, refreshRate=10, maxIterations = 300)
    sim.addObject(SimObject(isStatic = True, position=[0,0], name='object1'))
    sim.addObject(SimObject(isStatic = False, position=[1,0], velocity=[0,1], name='object2'))
    sim.run()