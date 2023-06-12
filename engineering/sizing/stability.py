import numpy as np


def calculate_wetted_area(rocket):
    def body(stage):
        # Recovery
        stage.recovery.wetted_area = stage.recovery.length * stage.recovery.diameter * np.pi

        # Engine
        stage.engine.wetted_area = stage.engine.length * stage.engine.diameter * np.pi

        # Fins
        stage.fins.wetted_area = stage.fins.span * (stage.fins.chord_root + stage.fins.chord_tip)

    # Nosecone
    rocket.stage2.nosecone.length = 5 * rocket.stage2.nosecone.diameter

    phi = np.arccos(1 - 2 * (rocket.stage2.nosecone.axial_distance / rocket.stage2.nosecone.length))
    local_radius = (rocket.stage2.nosecone.base_radius / np.sqrt(np.pi)) * np.sqrt(phi - 0.5 * np.sin(2 * phi))
    rocket.stage2.nosecone.wetted_area = np.pi * rocket.stage2.nosecone.diameter * local_radius

    # Stage 2 Body + Fins
    body(rocket.stage2)

    # Shoulder
    theta = np.arcsin((rocket.stage2.diameter - rocket.stage1.diameter) / (2 * rocket.stage1.shoulder.length))
    rocket.stage1.shoulder.wetted_area = np.pi * rocket.stage2.diameter * rocket.stage1.shoulder.length * np.cos(theta)

    # Stage 1 Body + Fins
    body(rocket.stage1)


def calculate_cp_locations(rocket):
    def body(length_before, stage):
        # Recovery
        stage.recovery.cp_location = length_before + 0.5 * stage.recovery.length
        length_before += stage.recovery.length

        # Engine
        stage.engine.cp_location = length_before + 0.5 * stage.engine.length
        length_before += stage.engine.length

        # Fins
        stage.fins.cp_location = length_before - 0.5 * stage.fins.chord_root

        return length_before

    datum: float = 0

    # Nosecone (5:1 Haack Nosecone)
    rocket.stage2.nosecone.cp_location = (25 / 8) * rocket.stage2.nosecone.diameter
    rocket.stage2.nosecone.length = 5 * rocket.stage2.nosecone.diameter
    datum += rocket.stage2.nosecone.length

    # Stage 2 Body + Fins
    datum = body(datum, rocket.stage2)

    # Shoulder
    taper_ratio = (rocket.stage1.diameter + 2 * rocket.stage2.diameter) / (rocket.stage1.diameter + rocket.stage2.diameter)
    rocket.stage1.shoulder.cp_location = datum + ((2 / 3) * rocket.stage1.shoulder.length * taper_ratio)
    datum += rocket.stage1.shoulder.length

    # Stage 1 Body + Fins
    body(datum, rocket.stage1)


def calculate_flow_area(rocket):
    def body(stage):
        # Recovery
        stage.recovery.flow_area = stage.recovery.length * stage.recovery.diameter

        # Engine
        stage.engine.flow_area = stage.engine.length * stage.engine.diameter

        # Fins
        stage.fins.flow_area = 0.5 * stage.fins.span * (stage.fins.chord_root + stage.fins.chord_tip)

    # Nosecone
    rocket.stage2.nosecone.flow_area = (10 / 3) * rocket.stage2.nosecone.diameter ** 2

    # Stage 2 Body + Fins
    body(rocket.stage2)

    # Shoulder
    rocket.stage1.shoulder.flow_area = 0.5 * rocket.stage1.shoulder.length * (rocket.stage1.diameter + rocket.stage2.diameter)

    # Stage 1 Body + FIns
    body(rocket.stage1)


def calculate_total_cp(rocket):
    def cp_stage(stage, cp_list):
        stage.flow_area = sum([stage[key].flow_area for key in cp_list])
        cp_location: float = 0
        for system in cp_list:
            cp_location += (stage[system].cp_location * stage[system].flow_area) / stage.flow_area

        stage.cp_location = cp_location

        return stage.cp_location, stage.flow_area

    cp1: list = ["shoulder", "recovery", "engine", "fins"]
    cp2: list = ["nosecone", "recovery", "engine", "fins"]

    cp_location1, flow_area1 = cp_stage(rocket.stage1, cp1)  # Stage 1
    cp_location2, flow_area2 = cp_stage(rocket.stage2, cp2)  # Stage 2

    # Total
    rocket.flow_area = flow_area1 + flow_area2
    rocket.cp_location = (cp_location1 * flow_area1 + cp_location2 * flow_area2) / rocket.flow_area


def calculate_fin_span(rocket):
    # Stage 2
    # Calculate needed CP to maintain set SM
    needed_cp = rocket.stage2.diameter * rocket.stage2.stability_margin + rocket.stage2.max_cg_location

    # Get all the CP * flow area values of the different systems
    shoulder = rocket.stage1.shoulder.cp_location * rocket.stage1.shoulder.flow_area
    nosecone = rocket.stage2.nosecone.cp_location * rocket.stage2.nosecone.flow_area
    recovery1 = rocket.stage1.recovery.cp_location * rocket.stage1.recovery.flow_area
    recovery2 = rocket.stage2.recovery.cp_location * rocket.stage2.recovery.flow_area
    engine1 = rocket.stage1.engine.cp_location * rocket.stage1.engine.flow_area
    engine2 = rocket.stage2.engine.cp_location * rocket.stage2.engine.flow_area

    # Area needed to reach the CP value
    fin_flow_area = (needed_cp * rocket.stage2.flow_area - nosecone - recovery2 - engine2) / rocket.stage2.fins.cp_location
    # Span needed to reach the flow area value
    rocket.stage2.fins.span = fin_flow_area / (0.5 * (rocket.stage2.fins.chord_root + rocket.stage2.fins.chord_tip))

    # Stage 1
    # Calculate needed CP to maintain set SM
    needed_cp = rocket.diameter * rocket.stability_margin + rocket.max_cg_location

    # Area needed to reach the CP value
    fin_flow_area = (needed_cp * rocket.flow_area - nosecone - shoulder - recovery1 - recovery2 - engine1 - engine2) / rocket.stage1.fins.cp_location
    # Span needed to reach the flow area value
    rocket.stage1.fins.span = fin_flow_area / (0.5 * (rocket.stage1.fins.chord_root + rocket.stage1.fins.chord_tip))


def calculate_fin_thickness(rocket):
    def thickness_stage(stage, stage_num):
        shear_modulus = stage.fins.shear_modulus
        speed_of_sound = rocket.simulator[f"min_speed_of_sound{stage_num}"]
        pressure = 101225  # Highest pressure encountered

        chord_root = stage.fins.chord_root
        chord_tip = stage.fins.chord_tip
        span = stage.fins.span
        aspect_ratio = 2 * (span ** 2) / stage.fins.wetted_area
        taper_ratio = chord_tip / chord_root

        flutter_speed = stage.fins.flutter_margin * rocket.simulator[f"max_velocity{stage_num}"]

        print(aspect_ratio, shear_modulus)
        stage.fins.thickness = chord_root * (1.337 * pressure * (1 + taper_ratio) * (aspect_ratio ** 3) * (flutter_speed / speed_of_sound) ** 2) / \
                               (2 * (aspect_ratio + 2) * shear_modulus) ** (1 / 3)

    thickness_stage(rocket.stage1, "1")
    thickness_stage(rocket.stage2, "2")


def run(rocket):
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    # Calculate the wetted area of the rocket
    calculate_wetted_area(rocket)

    # Calculate CP and flow area of the rocket
    calculate_cp_locations(rocket)
    calculate_flow_area(rocket)
    calculate_total_cp(rocket)

    # Calculate the span and thickness of the fins
    calculate_fin_span(rocket)
    calculate_fin_thickness(rocket)

    return rocket


if __name__ == "__main__":
    pass
