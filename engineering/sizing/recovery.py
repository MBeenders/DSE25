import numpy as np

#  Constant values:
g = 9.80665

def parachutes(rocket):
    """
    :param rocket: Rocket class
    :return: mass and cost of parachutes
    """

    dry_mass1: float = rocket.stage1.dry_mass
    dry_mass2: float = rocket.stage2.dry_mass
    rho: float = rocket.stage1.recovery.main_parachute.rho
    rho2drogue: float = rocket.stage2.recovery.drogue.rho
    descent_rate1: float = rocket.stage1.recovery.main_parachute.descent_rate
    descent_rate2_drogue: float = rocket.stage2.recovery.drogue.descent_rate
    descent_rate2_main: float = rocket.stage2.recovery.main_parachute.descent_rate
    c_D_main1: float = rocket.stage1.recovery.main_parachute.c_D
    c_D_drogue2: float = rocket.stage2.recovery.drogue.c_D
    c_D_main2: float = rocket.stage2.recovery.main_parachute.c_D
    material_density: float = rocket.stage1.recovery.material_density  # Assume material density is the same for both stages
    material_cost: float = rocket.stage1.recovery.material_cost

    # AREA & DIAMETER OF PARACHUTES:

    # 1st stage main parachute:
    area_main1 = dry_mass1 * g / (0.5 * rho * descent_rate1 ** 2 * c_D_main1)
    diameter_main1 = np.sqrt(area_main1 / (np.pi * 0.25))

    # 2nd stage drogue parachute:
    area_drogue2 = dry_mass2 * g / (0.5 * rho2drogue * descent_rate2_drogue ** 2 * c_D_drogue2)
    diameter_drogue2 = np.sqrt(area_drogue2 / (np.pi * 0.25))

    # 2nd stage main parachute:
    area_main2 = dry_mass2 * g / (0.5 * rho * descent_rate2_main ** 2 * c_D_main2)
    diameter_main2 = np.sqrt(area_main2 / (np.pi * 0.25))

    d_parachutes = [diameter_main1, diameter_drogue2, diameter_main2]

    # MASS OF PARACHUTES:

    # 1st stage main parachute:
    m_main1 = area_main1 * material_density

    # 2nd stage drogue parachute:
    m_drogue2 = area_drogue2 * material_density
    volume_stage2_drogue = m_drogue2 / rocket.stage2.recovery.drogue.packing_density
    rocket.stage2.recovery.drogue.length = volume_stage2_drogue / (np.pi * rocket.stage2.recovery.diameter**2 / 4)

    # 2nd stage main parachute:
    m_main2 = area_main2 * material_density
    volume_stage2_main_parachute = m_main2 / rocket.stage2.recovery.main_parachute.packing_density
    rocket.stage2.recovery.main_parachute.length = volume_stage2_main_parachute / (np.pi * rocket.stage2.recovery.diameter**2 / 4)

    # COST OF PARACHUTES:

    # 1st stage main parachute:
    cost_main1 = area_main1 * material_cost

    # 2nd stage drogue parachute:
    cost_drogue2 = area_drogue2 * material_cost

    # 2nd stage main parachute:
    cost_main2 = area_main2 * material_cost

    return m_main1, m_drogue2, m_main2, cost_main1, cost_drogue2, cost_main2, d_parachutes


def lines(rocket, d_parachutes):
    """
    :param rocket: Rocket class
    :return: None
    """
    line_l_d_main1 = rocket.stage1.recovery.main_parachute.line_l_d
    line_l_d_drogue2 = rocket.stage2.recovery.drogue.line_l_d
    line_l_d_main2 = rocket.stage2.recovery.main_parachute.line_l_d
    n_line_main1 = rocket.stage1.recovery.main_parachute.n_line
    n_line_drogue2 = rocket.stage2.recovery.drogue.n_line
    n_line_main2 = rocket.stage2.recovery.main_parachute.n_line
    line_density = rocket.stage1.recovery.line_density
    line_cost = rocket.stage1.recovery.line_cost

    # SUSPENSION LINE LENGTH & ITS TOTAL
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

    return m_main1, m_drogue2, m_main2, cost_main1, cost_drogue2, cost_main2


def cold_gas(rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    m_gas = rocket.stage1.recovery.m_gas  # Assume same mass for both stages
    gas_cost = rocket.stage1.recovery.gas_cost  # Assume same cost for both stages
    n_gas1 = rocket.stage1.recovery.n_gas
    n_gas2 = rocket.stage2.recovery.n_gas

    # Total Mass and Cost of cold gas systems
    m_total1 = m_gas * n_gas1
    m_total2 = m_gas * n_gas2

    gas_total_cost1 = gas_cost * n_gas1
    gas_total_cost2 = gas_cost * n_gas2

    return m_total1, m_total2, gas_total_cost1, gas_total_cost2


def run(rocket):
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """
    parachute_data = parachutes(rocket)
    line_data = lines(rocket, parachute_data[6])
    cold_gas_data = cold_gas(rocket)

    # Parachutes
    rocket.stage1.recovery.main_parachute.mass = parachute_data[0] + line_data[0]
    rocket.stage2.recovery.drogue.mass = parachute_data[1] + line_data[1]
    rocket.stage2.recovery.main_parachute.mass = parachute_data[2] + line_data[2]
    rocket.stage1.recovery.main_parachute.cost = parachute_data[3] + line_data[3]
    rocket.stage2.recovery.drogue.cost = parachute_data[4] + line_data[4]
    rocket.stage2.recovery.main_parachute.cost = parachute_data[5] + line_data[5]

    # Deployment
    rocket.stage1.recovery.gas_total_mass = cold_gas_data[0]
    rocket.stage2.recovery.gas_total_mass = cold_gas_data[1]
    rocket.stage1.recovery.gas_total_cost = cold_gas_data[2]
    rocket.stage2.recovery.gas_total_cost = cold_gas_data[3]

    # Total Mass and Cost
    rocket.stage1.recovery.mass = rocket.stage1.recovery.main_parachute.mass + cold_gas_data[0]
    rocket.stage2.recovery.mass = rocket.stage2.recovery.drogue.mass + rocket.stage2.recovery.main_parachute.mass + cold_gas(rocket)[1]
    rocket.stage1.recovery.cost = rocket.stage1.recovery.main_parachute.cost + cold_gas_data[2]
    rocket.stage2.recovery.cost = rocket.stage2.recovery.drogue.cost + rocket.stage2.recovery.main_parachute.cost + cold_gas(rocket)[3]

    # Total Length
    rocket.stage1.recovery.length = rocket.stage1.recovery.main_parachute.length
    rocket.stage2.recovery.length = rocket.stage2.recovery.main_parachute.length + rocket.stage2.recovery.drogue.length

    return rocket


if __name__ == "__main__":
    pass
