import pytest
import json
import os
import sys
import numpy as np

# Main Classes
from sizing.rocket import Rocket
from simulators.simulator import Simulator, FlightData

import sizing.engine as engine
import sizing.stability as stability
import sizing.electronics as electronics
import sizing.recovery as recovery

import simulators.advanced.aerodynamics as aerodynamics
import simulators.advanced.gravity as gravity
import simulators.advanced.dynamics as dynamics

current_file_path = os.path.split(sys.argv[0])[0]
run_parameters_file = open(os.path.join("files/run_parameters_testing.json"))
run_parameters: dict = json.load(run_parameters_file)


# Engine
def test_engine_initial_acceleration():
    acceleration = engine.initial_acceleration(12.5, 5)
    assert acceleration == 1


def test_parachutes():
    dynamics_run = dynamics.run
    drag = aerodynamics.drag
    isa = aerodynamics.isa

    simulator = Simulator(run_parameters["mission_profile"], run_parameters["simulator_parameters"], dynamics_run, gravity.gravity, drag, isa)
    rocket = Rocket(simulator)

    rocket.stage1.dry_mass = 50
    rocket.stage2.dry_mass = 30
    rocket.stage1.recovery.main_parachute.descent_rate = 20
    rocket.stage2.recovery.drogue.descent_rate = 20
    rocket.stage2.recovery.main_parachute.descent_rate = 5
    rocket.stage1.recovery.main_parachute.c_D = 0.7
    rocket.stage2.recovery.drogue.c_D = 0.5
    rocket.stage2.recovery.main_parachute.c_D = 0.6
    rocket.stage1.recovery.material_density = 0.035  # Assume material density is the same for both stages
    rocket.stage1.recovery.material_cost = 10

    m_main1, m_drogue2, m_main2, cost_main1, cost_drogue2, cost_main2, d_parachutes = recovery.parachutes(rocket)

    # Hand calculated values
    calc_m_main1 = 0
    calc_m_drogue2 = 0
    calc_m_main2 = 0
    calc_cost_main1 = 0
    calc_cost_drogue2 = 0
    calc_cost_main2 = 0
    calc_d_parachutes = 0

    assert abs(m_main1 - calc_m_main1) <= 1E-6
    assert abs(m_drogue2 - calc_m_drogue2) <= 1E-6
    assert abs(m_main2 - calc_m_main2) <= 1E-6
    assert abs(cost_main1 - calc_cost_main1) <= 1E-6
    assert abs(cost_drogue2 - calc_cost_drogue2) <= 1E-6
    assert abs(cost_main2 - calc_cost_main2) <= 1E-6
    assert abs(d_parachutes - calc_d_parachutes) <= 1E-6


def test_engine():
    dynamics_run = dynamics.run
    drag = aerodynamics.drag
    isa = aerodynamics.isa

    simulator = Simulator(run_parameters["mission_profile"], run_parameters["simulator_parameters"], dynamics_run, gravity.gravity, drag, isa)
    rocket = Rocket(simulator)


def test_nozzle_throat_area():
    pyth_area = engine.nozzle_throat_area(10, 5, 6)
    calc_area = 25 / 3
    assert abs(pyth_area - calc_area) <= 1E-6


def test_nozzle_exit_area():
    pyth_exit_area = engine.nozzle_exit_area(6, 1.6, 0.9, 0.45)
    calc_mach = 1.859105131
    calc_exit_area = 1.190586906
    assert abs(pyth_exit_area - calc_exit_area) <= 1E-6


def test_casing_mass():
    pyth_mass = engine.casing_mass(5, 20, 32, 0.650)
    calc_mass = 8168.140899
    assert abs(pyth_mass - calc_mass) <= 1E-6


def test_nozzle_mass():
    pyth_mass = engine.nozzle_mass(4, 0.5, 0.8, 0.05, 20)
    calc_mass = 17.4589725
    assert abs(pyth_mass - calc_mass) <= 1E-6


# Aerodynamics
def test_skin_friction_drag_0():
    rocket = FlightData(int(10E6))
    rocket.fineness_ratio = 5
    rocket.wetted_area = 2
    rocket.wetted_area_body = 1.2
    rocket.wetted_area_fins1 = 0.1472
    rocket.wetted_area_fins2 = 0.1472
    rocket.fin_thickness1 = 0.005
    rocket.fin_thickness2 = 0.005
    rocket.fin_mac1 = 0.17
    rocket.fin_mac2 = 0.17

    drag_friction = aerodynamics.skin_friction_drag(rocket, True, True, 200, 20E3, 0.588)

    assert 1680 < drag_friction < 1700


def test_fin_pressure_drag0():
    rocket = FlightData(int(10E6))
    rocket.fin_thickness1 = 0.005
    rocket.fin_thickness2 = 0.005
    rocket.fin_span1 = 0.15
    rocket.fin_span2 = 0.15

    drag_fin1, drag_fin2 = aerodynamics.fin_pressure_drag(rocket, True, True, 20E3, 0.588)

    assert 2 < drag_fin1 < 2.1
    assert 2 < drag_fin2 < 2.1


def test_nosecone_drag():
    rocket = FlightData(int(10E6))

    rocket.diameter2 = 0.2
    rocket.joint_angle = 0.0

    q = 0.5 * 1.225 * 100 ** 2  # 100 m/s at sea level
    mach = 100 / 343
    drag, cd = aerodynamics.nosecone_pressure_drag(rocket, q, mach)
    assert drag < 0.1  # Should be zero at subsonic
    assert cd == 0

    # Try at above mach, CD around 0.08
    q = 0.5 * 1.225 * 500 ** 2
    mach = 500 / 343
    drag, cd = aerodynamics.nosecone_pressure_drag(rocket, q, mach)
    assert drag > 0.1  # Should be zero at subsonic
    print(cd)
    assert 0.08 < cd < 0.1


def test_shoulder_drag():
    rocket = FlightData(int(10E6))

    rocket.diameter2 = 0.2
    rocket.diameter1 = 0.15
    rocket.joint_angle = 0.0

    q = 0.5 * 1.225 * 340 ** 2  # 100 m/s at sea level
    mach = 340 / 343
    drag, cd = aerodynamics.shoulder_pressure_drag(rocket, q, mach)
    assert drag == 0  # Should be zero at subsonic
    assert cd == 0

    # Try at above mach, CD around 0.08
    q = 0.5 * 1.225 * 500 ** 2
    mach = 500 / 343
    drag, cd = aerodynamics.shoulder_pressure_drag(rocket, q, mach)
    assert drag == 0
    print(cd)
    assert cd > 0.08


# Electronics
def test_electronics_infinitegain():
    diameter = 0
    frequency = 100
    efficiency = 1

    zerogain = electronics.antenna_gain(diameter, frequency, efficiency)
    assert zerogain == -np.inf, f"gain is not infinite gain is {zerogain}"


def test_electronics_gain():
    diameter = 1
    frequency = 10 ** 9
    efficiency = 0.5
    # verified against multiple online calculators

    gain = electronics.antenna_gain(diameter, frequency, efficiency)
    assert ((gain < 17.40) and (gain > 17.39)), f"gain is {gain} not 17.39"


def test_electronics_power_received():
    gain_rx = 0
    gain_tx = 17.390272402849615
    frequency = 10 ** 9
    distance = 1000
    power = 5

    power_rx = electronics.power_received(gain_rx, gain_tx, distance, frequency, power)
    assert ((power_rx > -81) and (power_rx < -78)), f"gain is {power_rx} not -78.0602999566"


def test_electronics_min_bw():
    datarate = 1000
    modulation = "QPSK"
    min_bw = electronics.minimum_bandwidth_required(datarate, modulation)
    assert min_bw == 500, f"minimum bandwidth is not 500 instead bandwidth is {min_bw}"


def test_electronics_noise():
    bw = 500
    antenna_SNR = 10
    gain = 10
    noise = electronics.W_to_dB(electronics.noise_received(bw, antenna_SNR, gain))
    assert ((noise > -201.7) and (noise < -201.6)), f"noise is not -201.60930671 instead noise is {noise}"


def test_electronics_doppler_shift():
    vel = 1000
    frequency = 10 ** 9
    delta_freq = electronics.doppler_shift(vel, frequency)
    assert delta_freq > 3332 and delta_freq < 3336, f"doppler shift is not 2999.999 instead shift is {delta_freq}"


def test_electronics_shannon_capacity():
    bw = 500
    SNR = 20
    capacity = electronics.capacity(bw, SNR)
    assert (capacity > 2180 and capacity < 2197), f"expected nr instead is {capacity}"


def test_electronics_total_power():
    power_total = 10
    dod = 0.7
    margin = 0.25
    p = power_total * (1 + margin) / (dod)
    po = electronics.total_power(power_total, dod, margin)
    assert p == po, f"expected power is not {p} instead power is {po}"


def test_electronics_energy():
    p_tot = 20
    time = 120
    energy = electronics.energy(p_tot, time)
    assert energy == (20 * 2), f"energy is not 40 instead energy is {p_tot}"


def test_electronics_Wh_to_Ah():
    tot_p = 100
    avg_v = 24
    time = 60 * 60
    ah = electronics.Wh_to_Ah(tot_p, avg_v, time)
    assert ah < 4.17 and ah > 4.16, f"amphour is not 4.167 instead ah is {ah}"


def test_stab():
    dynamics_run = dynamics.run
    drag = aerodynamics.drag
    isa = aerodynamics.isa

    simulator = Simulator(run_parameters["mission_profile"], run_parameters["simulator_parameters"], dynamics_run, gravity.gravity, drag, isa)
    rocket = Rocket(simulator)

    rocket.stage2.diameter = 0.15
    rocket.stage2.nosecone.diameter = 0.15
    rocket.stage2.engine.diameter = 0.15
    rocket.stage2.payload.diameter = 0.15
    rocket.stage2.recovery.diameter = 0.15

    rocket.stage2.nosecone.length = 0.5
    rocket.stage2.engine.length = 1
    rocket.stage2.payload.length = 0
    rocket.stage2.recovery.length = 0

    rocket.stage2.fins.chord_root = 0.25
    rocket.stage2.fins.chord_tip = 0.25
    rocket.stage2.fins.span = 0.115

    stability.calculate_cp_locations(rocket)
    stability.calculate_flow_area(rocket)
    cp_location = stability.calculate_total_cp(rocket)

    assert cp_location < 1


if __name__ == "__main__":
    pass
