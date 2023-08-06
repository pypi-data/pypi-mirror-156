import numpy as np
import sys
import NBodyBuilder.IC as IC
import NBodyBuilder.TimeStepper as TimeStepper
import NBodyBuilder.BH as BH
import NBodyBuilder.DirectForce as DirectForce
import NBodyBuilder.Particle as part

class NBodyBuilderClass(object):
    
    def __init__(self, numParticles, ic, gravity, integrator, time, dt):
        self.numParticles = numParticles
        self.ic = ic
        self.gravity = gravity
        self.integrator = integrator
        self.time = time
        self.dt = dt
        
        self.particles = IC.IC(numParticles, ic).particles
        self.history = TimeStepper.TimeStepper(self.particles, time, dt, integrator, gravity).history
    
    # Display the 3D array containing the history of the particle positions 
    def __repr__(self):
        s = "\n Displaying [mass, x, y, z] for each particle for each time step: \n\n"
        for t in range(self.history.shape[0]):
            s += "time: {:.2f}, particles: {} \n\n".format(self.dt * t, self.history[t])
            
        return s
    
    
def main():
    
    nb = NBodyBuilderClass(3, "random", "direct", "euler_cromer", 10, 1)
    
    print(nb)
    
    

if __name__ == "__main__":
    main()
    
    
