import numpy as np

# Fin sizing (variables: size, shape, sweep, number) (https://rocketry.gitbook.io/public/tutorials/airframe/sizing-fins)

# Fin flutter
# Maximum fin flutter must lie above the maximum rocket speed

G = 26900000000 # shear modulus [Pa]
#a = M / v # speed of sound [m/s]
t = 0.005 # wing thickness [m]
c_r = 0.4 # root chord length [m]
c_t = 0.1 # tip chord length [m]
b = 0.3 # semi-span length [m]
p = 12000 # air pressure [Pa]
S = 0.5 * b * (c_t+c_r) # surface area [m^2]
AR = (b**2) / S # aspect ratio [-]
TR = c_t / c_r # taper ratio [-]

v_f = np.sqrt(G / ((1.337*p*(1+TR)*AR**3) / (2*(AR+2)*(t/c_r)**3))) # fin flutter speed [m/s]
print(v_f)

# Fin thickness

sweep_LE = 30 * np.pi/180 # sweep angle of leading edge [rad]
A = t * (b/np.cos(sweep_LE)) # area experienced by airflow [m^2]
C_D_f = 0.12 # fin drag coefficient [-]
v = 200 # velocity [m/s]

F_d = 0.5 * p * v**2 * C_D_f * A # drag force [N]
print(F_d)
