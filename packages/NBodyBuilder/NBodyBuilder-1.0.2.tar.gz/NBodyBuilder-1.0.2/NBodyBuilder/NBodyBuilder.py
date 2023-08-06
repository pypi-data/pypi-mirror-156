import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import NBodyBuilder.Grapher as Grapher

def gui():
	"""GUI
	
	Runs NBodyBuilder driver with interactive GUI
	"""
	root = tk.Tk()
	root.title('NBodyBuilder')
	#root.iconbitmap("./NBodyBuilder.ico") # Need .ico icon file
	#root.geometry('400x250')


	# Make N particle slider
	particleLabel = tk.Label(root, text="Enter number of particles:")

	def read_slide(var):
		global N
		N = num_particles.get()
	num_particles = tk.Scale(root, from_=2, to=10,orient ='horizontal',command = read_slide)

	# Make dropdown for gravity solver
	solverLabel = tk.Label(root, text="Choose a gravity solver:")

	def show_solver(var):
		global S
		S = solver.get()
		if S == "Barnes-Hut": S = "BH"
		if S == "Direct Force": S = "direct"

	options_solver = [
		"Barnes-Hut",
		"Direct Force"]

	solver = tk.StringVar()
	#solver.set(options_solver[0])
	solver_drop = tk.OptionMenu(root, solver,*options_solver,command = show_solver)


	# Make dropdown for potential
	distLabel = tk.Label(root, text="Choose a distribution:")

	def show_dist(var):
		global D
		D = dist.get()
		if D == "Hernquist": D = "hernquist"
		if D == "Random": D = "random"

	options_dist = [
		"Hernquist",
		"Random"
	]
	dist = tk.StringVar()
	#dist.set(options_dist[0])
	dist_drop = tk.OptionMenu(root, dist,*options_dist,command = show_dist)


	# Make dropdown for stepping function
	stepLabel = tk.Label(root, text="Choose a stepping function:")

	def show_step(var):
		global I
		I = step.get()
		if I == "Euler": I = "euler"
		if I == "Euler-Cromer": I = "euler_cromer"
		if I == "Leapfrog": I = "leapfrog"

	options_step = [
		"Euler",
		"Euler-Cromer",
		"Leapfrog"
	]
	step = tk.StringVar()
	#step.set(options_step[0])
	step_drop = tk.OptionMenu(root, step,*options_step,command = show_step)


	# Make entry box for time step
	timestepLabel = tk.Label(root, text="Choose a timestep:")

	def show_timestep():
		global DT
		DT = float(dt.get())
	dt = tk.Entry(root)
	# Puts default text inside textbox
	dt.insert(0, "1")
	# Button to get timestep value
	timestep_botton = tk.Button(root, text="Submit", command = show_timestep)


	# Make entry box for time
	timeLabel = tk.Label(root, text="Choose a run time:")

	def show_time():
		global T
		T = float(t.get())
	t = tk.Entry(root)
	# Puts default text inside textbox
	t.insert(0, "10")
	# Button to get timestep value
	time_botton = tk.Button(root, text="Submit", command = show_time)


	# Make button to plot result
	def graph():
		Grapher.driver(numParticles=N, ic=D, gravity=S, integrator=I, time=T, dt=DT)

	plot = tk.Button(root,text = "Run and Plot", command = graph)


	# Place widgets on grid
	particleLabel.grid(row = 0,column = 0)
	num_particles.grid(row = 0,column = 1)
	solverLabel.grid(row = 1, column = 0)
	solver_drop.grid(row = 1, column = 1)
	distLabel.grid(row = 2, column = 0)
	dist_drop.grid(row = 2, column = 1)
	stepLabel.grid(row = 3, column = 0)
	step_drop.grid(row = 3, column = 1)
	timestepLabel.grid(row = 4, column = 0)
	dt.grid(row = 4, column = 1)
	timestep_botton.grid(row = 4, column = 2)
	timeLabel.grid(row = 5, column = 0)
	t.grid(row = 5, column = 1)
	time_botton.grid(row = 5, column = 2)
	plot.grid(row = 6, column = 0, columnspan = 3)


	root.mainloop()


def non_gui():
	"""Non-GUI

	Runs NBodyBuilder driver with interactive text input
	"""

	print("Enter Number of Particles between 2 and 100:")
	while True:
		N = input()
		if not N.isnumeric() or int(N)<2 or int(N)>100:
			print("Please enter an integer between 2 and 100.")
		else:
			break

	print("Enter a set of initial conditions.  Options are 'Hernquist' or 'Random'.")
	while True:
		D = input()
		if D!='Hernquist' and D!='Random':
			print("Please enter either 'Hernquist' or 'Random'.")
		else:
			break

	print("Enter a gravity solver.  Options are 'Barnes-Hut' or 'Direct Force'.")
	while True:
		S = input()
		if S!='Barnes-Hut' and S!='Direct Force':
			print("Please enter either 'Barnes-Hut' or 'Direct Force'.")
		else:
			break

	print("Enter an integrator.  Options are 'Euler' or 'Euler-Cromer' or 'Leapfrog'.")
	while True:
		I = input()
		if I!='Euler' and I!='Euler-Cromer' and I!='Leapfrog':
			print("Please enter either 'Euler' or 'Euler-Cromer' or 'Leapfrog'")
		else:
			break

	print("Enter a final time:")
	while True:
		T = input()
		if not T.isnumeric() or float(T)<=0:
			print("Please enter a positive integer or a float")
		else:
			break

	print("Enter a time step:")
	while True:
		DT = input()
		if not DT.isnumeric() or float(DT)<=0 or float(DT) > float(T):
			print("Please enter a positive integer or a float that is less than the final time.")
		else:
			break

	Grapher.driver(numParticles=int(N), ic=D, gravity=S, integrator=I, time=float(T), dt=float(DT))