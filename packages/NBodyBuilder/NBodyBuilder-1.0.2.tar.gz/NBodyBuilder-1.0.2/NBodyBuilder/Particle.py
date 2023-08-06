import numpy as np

class Particle(object):
    ''' This class keeps track of individual particles as well as the "super-particles" associated with non-leaf Nodes in Barnes-Hut.
    
    Args:
        mass (integer): Total mass of particles (or a particle)
        com (?): Center of mass of particles (or a position, for an individual particle)

    '''
    
    # Given a mass and a center of mass (or a position, for individual particles), instantiate a Particle object with no acceleration
    def __init__(self, mass, com):
        self.mass = mass
        self.com = com
        self.accel = np.zeros(3) 
        self.vel = np.zeros(3) #: array representing Particle velocity
    
    def __str__(self):
        ''' Returns a string representation of a Particle displaying the Particle's mass, COM, and acceleration.
        
        '''

        return "mass: {}, COM: {}, Accel: {}".format(self.mass, self.com, self.accel)
    
    def setAccel(self, accel):
        ''' Sets this Particle's acceleration to 'accel'.

        Args:
            accel (integer or float): New acceleration of Particle 

        '''

        self.accel = accel
    
    def resetAccel(self):
        ''' Sets this Particle's acceleration to 0.

        '''

        self.accel = np.zeros(3)
        
    def setVel(self, vel):
        ''' Sets this Particle's velocity to to 'vel'.

        Args:
            vel (integer or float): New velocity of Particle
        
        '''

        self.vel = vel
    
    def distTo(self, p):
        ''' Returns the distance between current Particle and another Particle 'p'.
        
        Args: 
            p (?): A Particle 'p'

        Returns:
            array: Vector norm of the two particles 

        '''

        disp = self.com - p.com
        return np.linalg.norm(disp)
    
    def combine(self, p):
        ''' Combines the mass and COM of this Particle with another Particle p.

        Args: 
            p (?): A Particle 'p'

        '''

        self.com = (self.mass * self.com + p.mass * p.com) / (self.mass + p.mass)
        self.mass += p.mass 
    
    def newtonAccel(self, p):
        ''' Computes the 1/r^2 acceleration induced on this Particle due to another Particle 'p'.
        
        Args: 
            p (?): A Particle 'p'

        Returns:
            accelVec (integer or float): 1/r^2 acceleration induced on this Particle by another Particle 'p'

        '''

        r = self.distTo(p)
        displacement = p.com - self.com
        
        accelMag = p.mass / r**2   # G = 1
        accelVec = accelMag * displacement / r
        
        return accelVec
    
    def newtonAccelSmooth(self, p, eps0, r0):
        ''' Computes the 1/r^2 acceleration induced on this Particle due to another Particle p, with gravitational softening length eps0 and cutoff distance r0.
        
        Args: 
            p (?): A Particle 'p'
            eps0 (integer or float): Gravitational softening
            r0 (integer or float): ?

        Returns:
            accelVec (integer or float): 1/r^2 acceleration induced on this Particle by another Particle 'p'

        '''

        r = self.distTo(p)
        displacement = p.com - self.com
        
        eps = self.epsilon(r, eps0, r0)   # gravitational softening
        softDisp = r + eps                # softened displacement
        
        accelMag = p.mass / softDisp**2
        accelVec = accelMag * displacement / softDisp
        
        return accelVec
    
    def epsilon(self, r, eps0, r0):
        ''' Implementation of gravitational softening law from Springel et al. 2013; r is the displacement and eps0 is the softening length. The softening has a finite range, going to 0 for distances greater than r0 (with r0 being smaller than half the smallest box dimension).
        
        Args: 
            r (?): Displacement
            eps0 (integer or float): Gravitational softening
            r0 (?): ?

        Returns:
            integer or float(?): ?

        '''

        if (r >= r0):
            return 0
        
        else:
            return -2.8 * eps0 / self.W2(r / (2.8 * eps0)) - r
        
    def W2(self, u):
        ''' Kernel for gravitational softening (from Springel, Yoshida, White 2001). 
        
        Args:
            u (?): ?

        Returns:
            float: ?

        '''

        if ((u >= 0) and (u < 0.5)):
            return 16./3 * u**2 - 48./5 * u**4 + 32./5 * u**5 - 14./5
      
        elif ((u >= 0.5) and (u < 1)):
            return 1./15 * u**-1 + 32./3 * u**2 - 16 * u**3 + 48./5 * u**4 - 32./15 * u**5 - 16./5
      
        else: 
            return -1./u
        
        
def main():
    #### !!!! TEST !!!! ####
    print("Hello World!")
        
    p1 = Particle(2, np.array([1,2,3]))
    p2 = Particle(3, np.array([1,1,1]))
    p3 = Particle(2, np.array([1,2,3.001]))
    print(p1)
        
    print(p1.distTo(p2) - np.sqrt(5))
    
    p1.combine(p2)
    print(p1)
    
    l = [1, np.NaN]*8
    print(l)
    print(np.all(np.isnan(l)))
    
    print("\n\n")
    
    print(p1.newtonAccel(p3))
    print(p1.newtonAccelSmooth(p3, 0.1, 5))

if __name__ == "__main__":
    main()

