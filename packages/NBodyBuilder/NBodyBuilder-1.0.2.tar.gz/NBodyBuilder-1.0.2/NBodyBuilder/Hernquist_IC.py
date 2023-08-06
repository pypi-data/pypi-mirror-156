import numpy as np
from numpy import random
import NBodyBuilder.Particle as part

class Hernquist(object):
    """ Hernquist class
    Randomly draw intial conditions of particles from Hernquist distribution.

    Args:
        a (float): Scale radius (See Binney and Tremaine Eqn. 2.66)
        M (float): Total mass
    """

    def __init__(self, numParticles, a, M):
        self.a = a
        self.M = numParticles
        self.numParticles = numParticles
        
        self.particles = self.generateHernquist()
        
    def __repr__(self):
        
        s = ""
        for p in self.particles:
            s += "{} \n\n".format(p)
            
        return s
        
    
    def cumHern(self, y):
        """Cumulative distribution function for the Hernquist distribution, where y = 4pi/3 * r^3 = volume
        
        Agrs: 
            y ():
        
        Returns:
            array: Cumulative distribution function for the Hernquist distribution
        """
        
        return  self.M * np.power(3*y/(4*np.pi), 2./3) * np.power(self.a + np.power(3*y/(4*np.pi), 1./3), -2)
    
    def invHern(self, x):
        """ Inverse of the cumulative distribution function for the Hernquist distribution.
        
        Agrs: 
            x ():
        
        Returns:
            array: Inverse of the cumulative distribution function
        """

        return 4*np.pi/3. * np.power(self.a,3) *np.power(x,1.5) * np.power(np.power(self.M,1./3) - np.power(x,0.5), -3)
    
    def sampleRadius(self):
        """ Draw a random radius from the Hernquist distribution.
        
        Returns:
            array(?): 
        """

        randX = random.rand()
        y = self.invHern(randX)
        
        return np.power(3*y/(4*np.pi), 1./3)
    
    def samplePointSphere(self):
        """ Draw a random point (in spherical coordinates) from the Hernquist distribution.
        
        Returns:
            (3) arrays: randR (), randPhi (), randTheta ()
        """

        randR = self.sampleRadius()
        randPhi = 2*np.pi * random.rand() 
        randTheta = np.pi * random.rand()
        return randR, randPhi, randTheta

    def samplePointCart(self):
        """ Draw a random point (in Cartesian coordinates) from the Hernquist distribution.
        
        Returns:
            (3) arrays: x (array of x-positions), y (array of y-positions), z (array of z-positions)
        """

        randPointSphere = self.samplePointSphere()
        r = randPointSphere[0]
        phi = randPointSphere[1]
        theta = randPointSphere[2]
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        
        return np.array([x, y, z])

    def generateHernquist(self):
        """ Sample numParticles Particles from a Hernquist distribution.
        Args:
            numParticles (integer): How many particles to draw from the distribution
            
        Returns:
            array: An array of particle positions of length numParticles
        """
        #particles = np.zeros(self.numParticles)
        
        particles = []
        for i in range(self.numParticles):
            particles.append(part.Particle(1, self.samplePointCart()))
            
        return np.array(particles)
    
def main():
    #### !!!! TEST !!!! ####
    h = Hernquist(10, 10, 10)
    print(h)
    
    
    
if __name__ == "__main__":
    main()