
# Centre of pressure calculator
# Assume that the C_P acts at the centre of planform area

# Rocket broken down into 6 segments

# Segment 1: 5:1 Haack nosecone
D_N = 150 # Diameter of nosecone [mm]
A1 = (10/3) * D_N**2
X1 = (25/8) * D_N

# Segment 2: upper stage
L_u = D_N * 20
D_u = D_N
A2 = L_u * D_u
X2 = 5*D_N + 0.5*L_u

# Segment 3: upper stage fins (assuming at lowest possible point)
b_u = 20 # span of upper stage fins [mm]
c_r_u = 25 # root chord length of upper stage fins [mm]
c_t_u = 10 # tip chord length of upper stage fins [mm]
A3 = 0.5*b_u*(c_r_u + c_t_u)
X3 = 5*D_N + L_u - 0.5*c_r_u

# Segment 4: conical transition
L_t = 100 # conical transition length [mm]
D_l = 200
A4 = 0.5 * L_t * (D_u+D_l)
X4 = ((2/3) * L_t * (D_l+2*D_u)/(D_l+D_u)) + 5*D_N + L_u

# Segment 5: lower stage
L_l = D_l * 15
A5 = L_l * D_l
X5 = 5*D_N + L_u + L_t + 0.5*L_l

# Segment 6: lower stage fins (assuming at lowest possible point)
b_l = 40 # span of lower stage fins [mm]
c_r_l = 50 # root chord length of lower stage fins [mm]
c_t_l = 20 # tip chord length of lower stage fins [mm]
A6 = 0.5*b_l*(c_r_l + c_t_l)
X6 = 5*D_N + L_u + L_t + L_l - 0.5*c_r_l

# Initial centre of pressure of rocket [m]
C_P = (A6*X6+A5*X5+A4*X4+A3*X3+A2*X2+A1*X1)/(1000*(A6+A5+A4+A3+A2+A1))
print(C_P)
