from typing import List

import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt

from scipy.integrate import odeint

class Sim:
	"""
	Klasa odpowiedzialna za symulowanie systemu sterowania
	skladajacego sie z regulatora PID i modelu zbiornika z ciecza i 
	swobodnym wyplywem
	regulator posiada ograniczenia wymuszenia majace na celu symulowanie
	rzeczywistej pompy ktora nie posiada nieskonczonej sprawnosci
	"""

	def __init__(self):
		# zmienne zbiornika
		_surface = 0				# powierzchnia zbiornika
		_k = 0						# wspolczynnik przeplywu 

		# nastawy PID
		_kp = 0
		_ki = 0
		_kd = 0

		_wd = 0						# wzmocnienie anti-windup
		_deadband = 0				#strefa nieczułości (% wartości zadanej)

		# warunki symulacji
		_sat = [0, 0]				# wartości graniczne pompy wody
		_t = []						# wektor czasu symulacji
		_control_trajectory = []	# macierz wartości pozadanych i odpowiadajacych im czasow
		
		_h0 = 0						# warunek początkowy - poziom cieczy w zbiorniku

		# zmienne modelu
		_e_old = 0					# poprzednia wartość uchybu
		_t_old = 0					# czas poprzedniego wywołania algorytmu regulatora
		_integral = 0				# wartosc calki
		_f_old = 0 					# poprzednia wartosc wymuszenia

		_iterator = 0				# iterator potrzebny do zapamietania aktualnej pozycji w macierzy trajektowii

		# vektory do wykresów
		_h = []						# wektor wartosci wysokosci slupa
		_tt = [0]					# wektor czasu regulatora
		_ff = [0]					# wekor wymuszenia regulatora
		_ee = [0]					# wektor uchybu (pracy regulatora)


	@staticmethod
	def _model(y, t, obj: 'Sim'):
		"""
		Model systemu wykorzystywany do symulacj
		Regulator PID zaimplementowany jest "recznie" numerycznie 
		Zbiornik jest w postaci funckji rozniczkowej rozwiazywanej przez 
		funkcje modulu scipy
		"""

		# wyznaczanie aktualnej wartosci zadanej
		if obj._control_trajectory[1][obj._iterator + 1] < t:
			obj._iterator += 1
		hz = obj._control_trajectory[0][obj._iterator]
		e = hz - y												# uchyb sterowania

		# reuglator PID
		if (t - obj._t_old) > 0.009 and (e > hz * obj._deadband or e < -hz * obj._deadband):		# krok czasu funkcji ODE jest czasem zbyt bliski zeru
			obj._integral = obj._integral + ((e)*(t - obj._t_old))									# czlon calkujacy
			dedt = (e - obj._e_old)/(t - obj._t_old)												# czlon rozniczkujacy
			f = (obj._kp * e) + (obj._ki * obj._integral) + (obj._kd * dedt)						# wymuszenie
			
			# saturacja + antiwindup
			if f < obj._sat[0]:
				obj._integral = obj._integral - obj._wd * (f - obj._sat[0])
				f = obj._sat[0]

			elif f > obj._sat[1]:
				obj._integral = obj._integral - obj._wd * (f - obj._sat[1])
				f = obj._sat[1]

	
			[obj._e_old, obj._t_old, obj._f_old] = [e, t, f]										#zapamietanie wartosci dla nastepnego wywolania alg. reg.

			# zapisanie wartości potrzebnych do wykresów
			obj._tt.append(t)
			obj._ee.append(e)
			obj._ff.append(f)

		else:
			f = obj._f_old																			#dla zbyt krotkiego kroku utrzymuj wczesniejsze wymuszenie
		
		# model zbiornika
		dydt = (1/obj._surface) * f - ((obj._k/obj._surface) * np.sqrt(y))
		return dydt

	def _reset_simulation(self):
		"""
		Resetuj symulacje do stanu poczatkowego
		"""
		self._e_old = 0
		self._t_old = 0
		self._integral = 0
		self._f_old = 0

		self._iterator = 0

		self._tt = [0]
		self._ff = [0]
		self._ee = [0]

		self._y = 0

	def run_simulation(self):
		"""
		Przeprowadz symujacje:
		
		-resetuj symulacje
		-przeprowadz symulacje
		"""
		self._reset_simulation()
		self._h = odeint(self._model, self._h0, self._t, args=(self,), hmax=0.01)

	def set_pid_settings(self, kp: float, ki: float, kd: float, wd: float = 0, deadband:float = 0):
		"""
		Ustaw nastawy PID
		"""
		self._kp = kp
		self._ki = ki
		self._kd = kd
		self._wd = wd
		self._deadband = deadband

	def set_sim_time(self, t0: float, t_end: float):
		"""
		Ustaw wektor czasu symulacji
		"""    
		self._t = np.arange(t0, t_end, t_end*1e-5)

	def set_tank_variables(self, surface: float, k: float):
		"""
		Ustaw wartości własne zbiornika
		"""
		self._surface = surface
		self._k = k

	def set_trajectory(self, y_zadane: List[float], t_y: List[float]):
		"""
		Ustaw macierz wartosci zadanych i odpowiadajacch im czasow
		"""
		self._control_trajectory = [y_zadane, [*t_y, 1000]]

	def get_trajectory(self) -> List[List[float]]:
		return self._control_trajectory

	def set_saturation(self, sat_low: float, sat_high: float):
		"""
		Ustaw graniczne wartości wymuszenia
		"""
		self._sat = [sat_low, sat_high]

	def set_initial_condition(self, h0:float):
		"""
		Ustaw warunki poczatkowe symulacji
		"""
		self._h0 = h0


	
	def get_simulation_output(self) ->List:
		"""
		Odbierz wyniki symulacji
		
		:return: [t, h, tt, ee, ff]
		:rtype:    t - wektor czasu symulacji
				h - wektor wartosci poziomu cieczy
				tt - wektor czasu wywolan regulatora PID
				ee - wektor uchybu wywolan regulatora PID
				ff - wektor wymuszenia wywolan regulatora PID
		"""
		return [self._t, self._h, self._tt, self._ee, self._ff]

	

def module_test():
	"""
	Funkcja stworzona do testów klasy Sim 

	Tworzy obiekt klasy Sim i przypisuje mu parametry symulacji
	Wyświetla wynik symulacji na wykresach 
	"""
	symulacja = Sim()
	
	# parametry symulacji
	symulacja.set_tank_variables(			surface=2.0,		k=1.2												)	# charakterystyka zbiornika: surface - powierzchnia podstawy zbiornika, k - wpółczynnik wypływu cieczy ze zbiornika
	symulacja.set_pid_settings(				kp=2,				ki=0.8,		kd=0.2,		wd=0.1,		deadband=0.0	)	# nastawy regulatora <IND>: Kp - wzmocnienie proporcjonalne, Ki - wzmocnienie członu całkującego, Kd - wzmocnienie członu różniczkującego, Wd - wmocnienie filtru przeciwnasyceniowego, deadbanc - szerokość pasma nieczułości [% y_zad], 
	symulacja.set_saturation(				sat_low=0,			sat_high=7											)	# saturacja urządzenia wykonującego: sat_low - dolna granica, sat_high - górna granica
	symulacja.set_initial_condition(		h0=0.0																	)	# stan początkowy zbiornika: h0 - początkowy poziom wody
	symulacja.set_sim_time(					t0=0,				t_end=200											)	# czas symulacji: t0 - czas rozpoczęcia, t_end - czas zakończenia symulacji
	symulacja.set_trajectory(				y_zadane=[10.0, 5.0, 0.0, 15.0, 5.0, 10.0, 5.0, 0.0, 15.0, 5.0, 10.0], 		t_y=[0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0]					)	# trajektoria zadana: y_zadane - wartości zadane, t_y - czasy odpowiadające momentom zadania kolejnej wartości
	
	# uruchomienie symulacji
	symulacja.run_simulation()

	# odczytanie wyniku symulacji
	t, h, tt, ee, ff = symulacja.get_simulation_output()
	traj = symulacja.get_trajectory()

	# generowanie wykresów
	plt.subplot(211)
	plt.plot(t, h, label="h")
	plt.plot(tt, ee, label="uchyb")
	plt.stairs(traj[0], traj[1], label="trajektoria")
	plt.xlim((t[0], t[-1]))
	plt.legend(loc="upper right")
	plt.grid()

	plt.subplot(212)
	plt.step(tt, ff, label="wymuszenie")
	plt.xlim((t[0], t[-1]))
	plt.legend(loc="upper right")
	plt.grid()

	plt.show()

if __name__ == "__main__":
	module_test()

