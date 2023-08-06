import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import NBodyBuilder.NBodyBuilderClass as nb

def driver(numParticles,ic,gravity,integrator,time,dt):
    """Run NBodyBuilder

    Runs NBodyBuilder and animates results

    Args:
        numParticles (int): integer number of particles to use in simulation
        ic (str): name of initial conditions
        gravity (str): name of gravity solver
        integrator (str): name of integration method
        time (float): total time to run simulation
        df (float): time step for integrator
    """
    data = nb.NBodyBuilderClass(numParticles,ic,gravity,integrator,time,dt).history
    times = np.arange(0,time+dt,dt)
    scatter_plot_2d(data,times)

def scatter_plot_2d(data,time):
    """Animated scatter plot

    Animates data in scatter plot over time.

    Args:
        data (array): 3D array containing time slices on the first axis, particles on the second axis, and [mass, x-position, y-position, z-position] on the third axis
        time (array): 1D array of time values
    """

    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    fig, ax = plt.subplots()

    def animate(i):
        fig.clear()
        ax = fig.add_subplot(111, aspect='equal', autoscale_on=False, xlim=(0, 1), ylim=(0, 1))
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('t = {:.3f}'.format(time[i]))
        s = ax.scatter(data[i,:,1], data[i,:,2], s=25, marker="o", edgecolor='black')

    ani = animation.FuncAnimation(fig, animate, interval=100, frames=range(len(data)),repeat_delay = 3000)
    fig.tight_layout()
    plt.show()

