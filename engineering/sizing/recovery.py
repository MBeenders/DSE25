from engineering.sizing.rocket import Rocket
import numpy as np

#Constant values:
g = 9.80665
rho = 1.225


def Parachutes(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: mass and cost of parachutes
    """
    dry_mass1 = rocket.stage1.dry_mass
    dry_mass2 = rocket.stage2.dry_mass
    V_1 = rocket.stage1.recovery.descent_rate
    V_2 = rocket.stage2.recovery.descent_rate
    c_D_main1 = rocket.stage1.recovery.main_parachute.c_D
    c_D_drogue2 = rocket.stage2.recovery.drogue.c_D
    c_D_main2 = rocket.stage2.recovery.main_parachute.c_D
    material_density = rocket.stage1.recovery.material_density #Assume material density is the same for both stages
    material_cost = rocket.stage1.recovery.material_cost

    # AREA & DIAMETER OF PARACHUTES:

    # 1st stage main parachute:
    S_main1 = dry_mass1 * g / (0.5 * rho * V_1 ** 2 * c_D_main1)
    d_main1 = np.sqrt(S_main1 / (np.pi * 0.25))

    # 2nd stage drogue parachute:
    S_drogue2 = dry_mass2 * g / (0.5 * rho * V_2 ** 2 * c_D_drogue2)
    d_drogue2 = np.sqrt(S_drogue2 / (np.pi * 0.25))

    # 2nd stage main parachute:
    S_main2 = dry_mass2 * g / (0.5 * rho * V_2 ** 2 * c_D_main2)
    d_main2 = np.sqrt(S_main2 / (np.pi * 0.25))

    d_parachutes = [d_main1, d_drogue2, d_main2]

    # MASS OF PARACHUTES:

    #1st stage main parachute:
    m_main1 = S_main1 * material_density

    # 2nd stage drogue parachute:
    m_drogue2 = S_drogue2 * material_density

    # 2nd stage main parachute:
    m_main2 = S_main2 * material_density

    m_parachutes = [m_main1, m_drogue2, m_main2]

    # COST OF PARACHUTES:

    # 1st stage main parachute:
    cost_main1 = S_main1 * material_cost

    # 2nd stage drogue parachute:
    cost_drogue2 = S_drogue2 * material_cost

    # 2nd stage main parachute:
    cost_main2 = S_main2 * material_cost

    cost_parachutes = [cost_main1, cost_drogue2, cost_main2]

    return m_parachutes, cost_parachutes, d_parachutes

def Lines(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    d_parachutes = Parachutes(rocket)[2]
    line_l_d_main1 = rocket.stage1.recovery.main_parachute.line_l_d
    line_l_d_drogue2 = rocket.stage2.recovery.drogue.line_l_d
    line_l_d_main2 = rocket.stage2.recovery.main_parachute.line_l_d
    n_line_main1 = rocket.stage1.recovery.main_parachute.n_line
    n_line_drogue2 = rocket.stage2.recovery.drogue.n_line
    n_line_main2 = rocket.stage2.recovery.main_parachute.n_line
    line_density = rocket.stage1.recovery.line_density
    line_cost = rocket.stage1.recovery.line_cost

    #SUSPENSION LINE LENGTH & ITS TOTAL
    # 1st stage main parachute:
    l_line_main1 = d_parachutes[0] * line_l_d_main1
    l_total_main1 = l_line_main1 * n_line_main1

    # 2nd stage drogue parachute:
    l_line_drogue2 = d_parachutes[1] * line_l_d_drogue2
    l_total_drogue2 = l_line_drogue2 * n_line_drogue2

    # 2nd stage main parachute:
    l_line_main2 = d_parachutes[2] * line_l_d_main2
    l_total_main2 = l_line_main2 * n_line_main2

    # TOTAL MASS AND COST OF LINES
    # 1st stage main parachute:
    m_main1 = line_density * l_total_main1
    cost_main1 = line_cost * l_total_main1

    # 2nd stage drogue parachute:
    m_drogue2 = line_density * l_total_drogue2
    cost_drogue2 = line_cost * l_total_drogue2

    # 2nd stage main parachute:
    m_main2 = line_density * l_total_main2
    cost_main2 = line_cost * l_total_main2

    m_lines = [m_main1, m_drogue2, m_main2]
    cost_lines = [cost_main1, cost_drogue2, cost_main2]

    return m_lines, cost_lines

def Coldgas(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    m_gas = rocket.stage1.recovery.m_gas # Assume same mass for both stages
    gas_cost = rocket.stage1.recovery.gas_cost
    n_gas1 = rocket.stage1.recovery.n_gas
    n_gas2 = rocket.stage2.recovery.n_gas

    # Total Mass and Cost of cold gas systems
    m_total1 = m_gas * n_gas1
    m_total2 = m_gas * n_gas2

    m_total = m_total1 + m_total2

    gas_total_cost = gas_cost * (n_gas1 + n_gas2)

    return m_total, gas_total_cost



def run(rocket: Rocket) -> Rocket:
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    m_total_recovery = Parachutes(rocket)[0] + Lines(rocket)[0] + Coldgas(rocket)[0]
    cost_total_recovery = Parachutes(rocket)[1] + Lines(rocket)[1] + Coldgas(rocket)[1]

    return rocket, m_total_recovery, cost_total_recovery


if __name__ == "__main__":
    test_rocket = Rocket()
    run(test_rocket)
