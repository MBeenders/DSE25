import pytest
import json
import os
import sys

# Main Classes
from sizing.rocket import Rocket
from simulators.simulator import Simulator, FlightData

import sizing.engine as engine
import sizing.electronics as electronics

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


def test_engine():
    dynamics_run = dynamics.run
    drag = aerodynamics.drag
    isa = aerodynamics.isa

    simulator = Simulator(run_parameters["mission_profile"], run_parameters["simulator_parameters"], dynamics_run, gravity.gravity, drag, isa)
    rocket = Rocket(simulator)


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


if __name__ == "__main__":
    pass
