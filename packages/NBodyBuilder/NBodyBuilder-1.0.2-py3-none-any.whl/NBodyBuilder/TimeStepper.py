import numpy as np
import NBodyBuilder.Particle as part
import NBodyBuilder.DirectForce as df
import NBodyBuilder.BH as bh

class TimeStepper(object):
    ''' This class evolves a set of Particles through time to simulate N gravitationally-interacting particles.
    '''
    
    # Given an array of Particles, an end time, a time step dt, and an integration scheme, evolve the Particles through time and save the history of particle positions (and masses) in a 3D array
    def __init__(self, particles, time, dt, integrator, gravity):
        self.particles = particles
        self.time = time
        self.dt = dt
        
        self.history = np.zeros((int(time/dt) + 1, particles.size, 4))
        
        for t in range(self.history.shape[0]):
            if (t != 0):
                
                if (gravity == "direct"):
                    accelSolver = df.DirectForce(self.particles)
                elif (gravity == "BH"):
                    accelSolver = bh.BH(50, 0.1, self.particles)
                else:
                    accelSolver = df.DirectForce(self.particles)
                    
                accelSolver.computeAllAccels()
                
                if (integrator == "euler_cromer"):
                    self.euler_cromer()    
                elif (integrator == "euler"):
                    self.euler()
                else:
                    self.euler_cromer()
            
            for i in range(particles.size):
                self.history[t,i] = np.array([particles[i].mass, 
                                              particles[i].com[0], particles[i].com[1], particles[i].com[2]]) 
        
    def __repr__(self):
        ''' Display the 3D array containing the history of the particle positions.

        Returns:
            s (string): String showing history of particle positions (3D)
        '''

        s = "\n Displaying [mass, x, y, z] for each particle for each time step: \n\n"
        for t in range(self.history.shape[0]):
            s += "time: {:.2f}, particles: {} \n\n".format(self.dt * t, self.history[t])
            
        return s
            
    def euler(self):
        ''' Evolves the particles by one time step using the forward-Euler method.
        '''

        for p in self.particles:
            
            dv = self.dt * p.accel
            dx = self.dt * p.vel
            p.vel = p.vel + dv
            p.com = p.com + dx
            
            p.resetAccel()

    def euler_cromer(self):
        ''' Evolves the particles by one time step using the Euler-Cromer method.
        '''

        for p in self.particles:
            
            dv = self.dt * p.accel
            p.vel = p.vel + dv
            dx = self.dt * p.vel
            p.com = p.com + dx
            
            p.resetAccel()

def main():
    #### !!!! TEST !!!! ####

    p1 = part.Particle(1, np.array([0,0,0]))
    p2 = part.Particle(10, np.array([3,3,0]))
    
    particles = np.array([p1, p2])
    particles.size
    
    ts = TimeStepper(particles, 5, 0.1, "euler_cromer", "direct")
    
    print(ts)
    
    
    
    
if __name__ == "__main__":
    main()
    
        