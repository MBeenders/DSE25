import numpy as np

# NOSECONE - 3:1 Haack (optimised for length and diameter, where c = 0)

# 3:1 Haack minimum drag noses
c = 0 # Optimisation coefficient        [-]
X = 0.24 # Axial distance from the nose [m]
L = 1.5 # Model length                  [m]
D = 0.5 # Model base diameter           [m]
R = 0.25 # Model base radius            [m]

phi = np.arccos(1-2*(X/L)) # [rad]

r = (R/np.sqrt(np.pi))*np.sqrt(phi-0.5*np.sin(2*phi)+c*np.sin(phi)**3) # Model local radius [m]

C_D_F = 0.12 # Maximum foredrag coefficient in supersonic conditions
C_D_w = 0.071 # Wave drag coefficient for 3:1 Haack


# Stagnation temperature from diatomic isentropic flow
M = 5.02 # Maximum mach number [-]
T = 219.15 # Atmospheric temperature at altitude maximum mach number [K]
T_nc = T*((1-0.2*(M**2))**-1) # Stagnation temperature [K] --> is incorrect

print(T_nc)
