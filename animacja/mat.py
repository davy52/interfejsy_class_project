import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt

from scipy.integrate import odeint



c_S = 2 		#m^2
c_k = 1.2		#stała przepływu

#nastawy_PID
c_Kp = 2
c_Ki = 0.8
c_Kd = 0.0

c_deadband = 0.05
c_wd = 0.2

sat = [0, 7] 		#saturacja - graniczne wartości wymuszenia
#end-of-nastawy_PID

#warunki_początkowe
y0 = 0 						#h0

#end-of-warunki_początkowe

t = np.arange(0, 30, 1e-6)


#zmienne_regulatora?
vals = [5.0, 7.6, 2.0]
t_traj = [0.0, 10.0, 20.0]

#end-of-zmienne_reg


[e_old, t_old, I, F_old] = [0, 0, 0, 0]
i = 0
traj = [vals, [*t_traj, 1000.0]]

tt = [0]
FF = [0]
ee = [0]

def model(y, t):
	global c_Kp, c_Ki, c_Kd, c_k, c_S, c_deadband, c_wd
	global e_old, t_old, I, F_old
	global tt, FF, ee, sat, i, traj
	#dydt = np.zeros_like(y)
	
	if traj[1][i+1] < t:
		i += 1
	hz = traj[0][i]
	e = hz - y 								# uchyb

	if t-t_old > 0.009 and (e < hz * c_deadband or e > -hz * c_deadband):
		I = I + ((e) * (t - t_old))		# calka
		dedt = (e - e_old)/(t - t_old)			# rozniczka
		F = (c_Kp * e) + (c_Ki * I) + (c_Kd * dedt)	# sterowanie


		if F > sat[1]:
			I = I - c_wd * (F - sat[1])
			F = sat[1]
		elif F < sat[0]:
			I = I - c_wd * (F - sat[0])
			F = sat[0]

		[e_old, t_old, F_old] = [e, t, F]
		tt.append(t)
		FF.append(F)
		ee.append(e)

	else:
		F = F_old

	dydt = (1/c_S)*F - (c_k/c_S)*np.sqrt(y)
	return dydt



y = odeint(model, y0, t, hmax=0.01)


#dtmax = max([ t2-t1 for t1,t2 in zip(tt[:], tt[1:]) if t1 < 0.6])
#print(dtmax)

plt.subplot(211)
plt.plot(t, y, label="h")
plt.plot(tt, ee, label="uchyb")
plt.stairs(traj[0], traj[1], label="trajektoria")
plt.xlim((t[0], t[-1]))
plt.legend(loc="upper right")
plt.grid()

plt.subplot(212)
plt.step(tt, FF, label="wymuszenie")
plt.xlim((t[0], t[-1]))
plt.legend(loc="upper right")
plt.grid()

plt.show()

