#---------Imports
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#---------End of imports

fig = plt.Figure()

x = np.arange(0, 2*np.pi, 0.01)        # x-array``

def animate(i):
	ys = np.add(np.sin(0.01 * (x+i)), np.sin((x+i)*0.8)*0.05)
	ys += 1.1
	line.set_ydata(ys)  # update the data
	return line

root = Tk.Tk()
frame = ttk.Frame(root, padding=10)
frame.grid()

label = Tk.Label(frame ,text="Jebać numpy").grid(column=0, row=0)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().grid(column=0,row=1)

ttk.Button(frame, text="Quit", command=root.destroy).grid(column=0, row=5)

ax = fig.add_subplot(111, ylim=(0, 3), xlim=(0, 6))
line, = ax.plot(x, x)
ani = animation.FuncAnimation(fig, animate, np.arange(1, 1000), interval=30, blit=False)

Tk.mainloop()
