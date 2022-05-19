from dataclasses import dataclass

import tkinter as tk
from tkinter import ttk

from matplotlib import pyplot as plt, animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np

from imports.sim import Sim


class Window:

	def __init__(self) -> None:
		self._zbiornik_t = np.arange(0, 100, 1e-4)
		self._zbiornik_y = np.zeros_like(self._zbiornik_t)
		self._zbiornik_tt = np.arange(0, 100, 1e-4)
		self._zbiornik_ee = np.arange(0, 100, 1e-4)
		self._zbiornik_ff = np.arange(0, 100, 1e-4)

		self._zbiornik_traj = [np.zeros((0, 10)), np.arange(1, 100, 10)]
		self._init_sim()

		self._win = tk.Tk()
		self._win.title("Controla poziomu wody w zbiorniku")
		self._win.wm_minsize(width=640, height=360)

		self._s = ttk.Style()
		#self._s.configure("my.TFrame", background='red')

		self._root = ttk.Frame(self._win, padding=10)
		self._root.grid(row=0, column=0, sticky='news')

		# Frame zbiornik - animacja napełniania zbiornika
		self._zbiornik = ttk.Frame(self._root, height=300, width=500, style='my.TFrame')
		self._zbiornik.grid(row=0, column=0)

		self._fig_zbiornik = plt.figure(dpi=100, figsize=(5, 3))
		self._ax_zbiornik = self._fig_zbiornik.add_subplot(xlim=(0, 1), ylim=(0, 20))
		self._ax_zbiornik.xaxis.set_visible(False)
		self._line_zbiornik, = self._ax_zbiornik.plot([], [], lw=2)

		self._canvas_zbiornik = FigureCanvasTkAgg(self._fig_zbiornik, master=self._zbiornik)
		self._canvas_zbiornik.draw()
		self._canvas_zbiornik.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

		self._label_zbiornik = ttk.Label(self._zbiornik, text="Poziom zbiornika")
		self._label_zbiornik.pack(side=tk.TOP)

		self._zbiornik_run_first_animation()

		# Frame poziom - wykres poziomu wody w czasie
		self._poziom = ttk.Frame(self._root, height=300, width=500, style='my.TFrame')
		self._poziom.grid(row=0, column=1)

		self._fig_poziom = plt.figure(dpi=100, figsize=(5, 3))
		self._ax_poziom = self._fig_poziom.add_subplot(xlim=(0, 100), ylim=(0, 20))
		self._line_poziom = [0, 0]
		self._line_poziom[0] = self._ax_poziom.plot([], [], lw=2, label="h")
		self._line_poziom[1] = self._ax_poziom.stairs(self._zbiornik_traj[0], self._zbiornik_traj[1], linestyle=":", color="green", label="wartości zadane", linewidth=2)
		self._ax_poziom.legend(loc='upper right')
		self._ax_poziom.grid()

		self._canvas_poziom = FigureCanvasTkAgg(self._fig_poziom, master=self._poziom)
		self._canvas_poziom.draw()
		self._canvas_poziom.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

		self._label_poziom = ttk.Label(self._poziom, text="Funkcja poziomu w czasie")
		self._label_poziom.pack(side=tk.TOP)

		self._poziom_run_first_animation()

		# Frame regulacja 
		self._regulacja = ttk.Frame(self._root, height=300, width=500, style='my.TFrame')
		self._regulacja.grid(row=1, column=0)

		# self._fig_regulacja = plt.figure(dpi=100, figsize=(5,3))
		# self._ax_regulacja = self._fig_regulacja.add_subplot(xlim=(0, 100), ylim=(0, 20))
		# self._line_regulacja = [0, 0]
		# self._line_regulacja[0] = self._ax_regulacja.plot([], [], lw=2, label="Sterowanie")
		# self._line_regulacja[1] = self._ax_regulacja.plot([], [], lw=2, label="Uchyb")
		# self._ax_regulacja.legend(loc='upper right')
		# self._ax_regulacja.grid()

		# self._canvas_regulacja = FigureCanvasTkAgg(self._fig_regulacja, master=self._regulacja)
		# self._canvas_regulacja.draw()
		# self._canvas_poziom.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

		
		self._label_regulacja = ttk.Label(self._regulacja, text="Regulacja")
		#self._label_regulacja.pack(side=tk.TOP)
		
		# self._regulacja_run_first_animation()

		# Frame nastawy
		self._nastawy = ttk.Frame(self._root, height=300, width=500, style='my.TFrame')
		self._nastawy.grid(row=0, column=2)

		self._label_nastawy = ttk.Label(self._nastawy, text="Nastawy")
		self._label_nastawy.pack(side=tk.TOP)

		# Frame symulacja
		self._symulacja = ttk.Frame(self._root, height=300, width=500, style='my.TFrame')
		self._symulacja.grid(row=1, column=2)	

		self.button = ttk.Button(master=self._symulacja, text="RUN", command= lambda: self.run_sim())
		self.button.pack()

		self.button_exit = ttk.Button(master=self._symulacja, text="EXIT", command= lambda: self._quit())
		self.button_exit.pack()



	# Metody zbiornika
	def _zbiornik_animate(self: 'Window', i: int):
		x = np.linspace(0, 1, 1000)
		y0 = self._zbiornik_y[i] 
		y = np.add(y0, np.sin(x * 15 + 0.0001*i) * 0.1)
		self._line_zbiornik.set_data(x, y)
		self._ax_zbiornik.collections.clear()
		self._ax_zbiornik.fill_between(x, y, facecolor='#4780cc')
		return self._line_zbiornik

	def _zbiornik_run_first_animation(self):
		self._anim_zbiornik = animation.FuncAnimation(
			self._fig_zbiornik, 
			self._zbiornik_animate,  
			frames=[i for i in range(0, int(100/0.01 ), 10)], 
			interval=self._sim_speed,
			repeat=False
		)
		self._anim_zbiornik.pause()

	def _zbiornik_run_animation(self):
		self._anim_zbiornik.frame_seq = self._anim_zbiornik.new_frame_seq()
		self._anim_zbiornik.resume()

	#metody poziomu
	def _poziom_animate(self: 'Window', i: int):
		x = self._zbiornik_t[0:i]
		y = self._zbiornik_y[0:i]
		self._line_poziom[0][0].set_data(x, y)
		self._line_poziom[1].set_data(self._zbiornik_traj[0], self._zbiornik_traj[1])
		return self._line_poziom

	def _poziom_run_first_animation(self):
		self._anim_poziom = animation.FuncAnimation(
			self._fig_poziom,
			self._poziom_animate,
			frames=[i for i in range(0, int(100/0.01), 10)],
			interval=self._sim_speed,
			repeat=False
		)
		self._anim_poziom.pause()
	
	def _poziom_run_animation(self):
		self._anim_poziom.frame_seq = self._anim_poziom.new_frame_seq()
		self._anim_poziom.resume()

	#metody regulacji
	def _regulacja_animate(self: 'Window', i: int):
		x = self._zbiornik_tt[0:i]
		y = self._zbiornik_ff[0:i]
		self._line_regulacja[0][0].set_data(x, y)

		y = self._zbiornik_ee[0:i]
		self._line_regulacja[1][0].set_data(x, y)
		return self._line_regulacja

	def _regulacja_run_first_animation(self):
		self._anim_regulacja = animation.FuncAnimation(
			self._fig_regulacja,
			self._regulacja_animate,
			frames=[i for i in range(0, int(100/0.01), 10)],
			interval=self._sim_speed,
			repeat=False
		)
		self._anim_regulacja.pause()
	
	def _regulacja_run_animation(self):
		self._anim_regulacja.frame_seq = self._anim_regulacja.new_frame_seq()
		self._anim_regulacja.resume()
	
	# symulacja
	def _init_sim(self):
		self._sim = Sim()		#definicja obiektu klasy Sim
		
		# parametry symulacji
		self._sim.set_tank_variables(			surface=2.0,		k=1.2														)	# charakterystyka zbiornika: surface - powierzchnia podstawy zbiornika, k - wpółczynnik wypływu cieczy ze zbiornika
		self._sim.set_pid_settings(				kp=2,				ki=0.8,		kd=0.,		wd=0.1,		deadband=0.0			)	# nastawy regulatora <IND>: Kp - wzmocnienie proporcjonalne, Ki - wzmocnienie członu całkującego, Kd - wzmocnienie członu różniczkującego, Wd - wmocnienie filtru przeciwnasyceniowego, deadbanc - szerokość pasma nieczułości [% y_zad], 
		self._sim.set_saturation(				sat_low=0,			sat_high=7													)	# saturacja urządzenia wykonującego: sat_low - dolna granica, sat_high - górna granica
		self._sim.set_initial_condition(		h0=0.0																			)	# stan początkowy zbiornika: h0 - początkowy poziom wody
		self._sim.set_sim_time(					t0=0,				t_end=100													)	# czas symulacji: t0 - czas rozpoczęcia, t_end - czas zakończenia symulacji
		self._sim.set_trajectory(				y_zadane=[10.0, 5.0, 0.0, 15.0, 5.0], 		t_y=[0.0, 20.0, 40.0, 60.0, 80.0]	)	# trajektoria zadana: y_zadane - wartości zadane, t_y - czasy odpowiadające momentom zadania kolejnej wartości
		self._zbiornik_traj = self._sim.get_trajectory()

		self._sim_speed = 10			# 100 "czas rzeczywisty" - okreś odświerzania animacji

	def run_sim(self):
		self._sim.run_simulation()

		self._zbiornik_t, self._zbiornik_y, self._zbiornik_tt, self._zbiornik_ee, self._zbiornik_ff = self._sim.get_simulation_output()
		self._zbiornik_traj = self._sim.get_trajectory()

		self._zbiornik_run_animation()
		self._poziom_run_animation()
		# self._regulacja_run_animation()

	def open_window(self):
		self._win.mainloop()

	def _quit(self):
		self._anim_poziom.pause()
		self._anim_zbiornik.pause()
		self._win.quit()


	

def module_test():
	WINDOW = Window()

	WINDOW.open_window()


if __name__ == '__main__':
	module_test()
