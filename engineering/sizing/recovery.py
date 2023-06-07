from engineering.sizing.rocket import Rocket

#Constant values:
g = 9.80665
rho = 1.225



def Parachutes(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
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

    # AREA OF PARACHUTES:

    # 1st stage main parachute:
    S_main1 = dry_mass1 * g / (0.5 * rho * V_1 ** 2 * c_D_main1)

    # 2nd stage drogue parachute:
    S_drogue2 = dry_mass2 * g / (0.5 * rho * V_2 ** 2 * c_D_drogue2)

    # 2nd stage main parachute:
    S_main2 = dry_mass2 * g / (0.5 * rho * V_2 ** 2 * c_D_main2)

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

    return m_parachutes, cost_parachutes


def run(rocket: Rocket) -> Rocket:
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    Parachutes(rocket)

    return rocket


if __name__ == "__main__":
    test_rocket = Rocket()
    run(test_rocket)
