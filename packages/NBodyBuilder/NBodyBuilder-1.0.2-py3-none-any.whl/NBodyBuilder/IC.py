import numpy as np
import numpy.random as rand
import NBodyBuilder.Particle as part
import NBodyBuilder.Hernquist_IC as hern

class IC(object):
    ''' Generated particle array given number of particles randomly OR using Hernquist distribution. 
    
    Args:
        numParticles (integer): Number of particles
        ic (?): ?
        twoD (boolean): True for 2D, false for ?
        seed (integer): Random number generator seed
        boxSize (integer or float): Size of the simulation box
        hern_a (integer or float): Hernquist scale radius
        hern_m (integer): Hernquist mass
        '''
    
    def __init__(self, numParticles, ic, twoD = True, seed=12345, boxSize = 50, hern_a = 10, hern_m = 10):
        
        if (ic == "random"):
            self.particles = self.randParticles(numParticles, boxSize, seed, twoD)
        
        elif (ic == "hernquist"):
            self.particles = hern.Hernquist(numParticles, hern_a, hern_m).particles
            
        else:
            self.particles = self.randParticles(numParticles, boxSize, seed, twoD)
            
            
    def __repr__(self):
        ''' ???

        Returns:
            s (string): ?
        '''
        
        s = ""
        for p in self.particles:
            s += "{} \n\n".format(p)
            
        return s
    
    def randParticles(self, numParticles, boxSize, seed, twoD = True):
        ''' Returns the number particles specified by numParticles, randomly generated with the random seed.

        Args:
            numParticles (integer): Number of particles
            boxSize (integer or float): Size of the simulation box
            seed (integer): Random number generator seed
            twoD (boolean): True for 2D, false for ?

        Returns:
            particles (list): A list of Particles 'p'
        '''

        particles = []
        generator = rand.default_rng(seed)
        randMasses = generator.random(numParticles)
        randCOMS = generator.random((numParticles, 3))
        
        for i in range(numParticles):
            mass = 10 * randMasses[i]
            com = boxSize * randCOMS[i] - boxSize/2.
            if (twoD): com[2] = 0
            
            p = part.Particle(mass, com)
            particles.append(p)
            
        return np.array(particles)
    
def main():
    #### !!!! TEST !!!! ####
    ic = IC(10, "random")
    print(ic)
    
    
if __name__ == "__main__":
    main()
