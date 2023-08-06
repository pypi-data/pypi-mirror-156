import numpy as np
import NBodyBuilder.Particle as part

''' The DirectForce class implements an O(N^2) gravity solver that directly computes the Newtonian (1/r^2) force/acceleration between each pair of particles.

    Args: 
        particles (array): Array of particles
'''

class DirectForce(object):
    
    # Given an array of Particles, instantiate a DirectForce object
    def __init__(self, particles):
        self.particles = particles
        
    def computeAccel(self, p):
        ''' Computes the acceleration of Particle p induced by all other particles in the simulation.

        Args:
            p (?): A Particle 'p'

        Returns:
            totalAccel (?): Total acceleration felt by Particle p from all other particles
        '''

        totAccel = np.zeros(3)
        
        for particle in self.particles:
            if (particle != p):
                accel = p.newtonAccelSmooth(particle, 0.1, 5)
                totAccel += accel
        
        return totAccel
    
    def computeAllAccels(self):
        ''' Computes the pairwise forces/accelerations for all Particles in the simulation.
        '''

        for p in self.particles:
            accel = self.computeAccel(p)
            p.setAccel(accel)
            

def main():
    #### !!!!!! TEST !!!!!! ####
    
    print("Hello World!")
        
    p1 = part.Particle(2, np.array([0,0,0]))
    p2 = part.Particle(2, np.array([1,1,1]))
    p3 = part.Particle(2, np.array([0.5,0.5,0.5]))
    p4 = part.Particle(10, np.array([0.1, -10, -25]))
    
    df = DirectForce(np.array([p1, p2, p3, p4]))
    # print(df.computeAccel(p1))
    # print(df.computeAccel(p2))
    # print(df.computeAccel(p3))
    
    df.computeAllAccels()
    print(p1)
    print(p2)
    print(p3)
    print(p4)
    
    # p2.resetAccel()
    # print(p2)
        

if __name__ == "__main__":
    main()
        
