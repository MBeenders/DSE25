import sys
import os

path = os.path.split(sys.argv[0])[0]
sys.path.append(path)

from sizing.rocket import Rocket
import numpy as np

# Constant values:
k = 1.38E-23  # boltzman constant
c = 3 * 10 ^ 8  # m/s

modulation = {
    "BPSK": 0.5, "OOK": 0.5, "QPSK": 1, "OQPSK": 1, "FSK": 0
}


def dB_to_W(value_dB):
    watt = 10 ^ (value_dB / 10)
    return watt


def W_to_dB(value_w):
    dB = 10 * np.log10(value_w)
    return dB


def antenna_gain(size, frequency, efficiency):
    wavelength = c / frequency
    gain = ((np.pi * size) ^ 2) * (efficiency / wavelength)
    gain_dB = W_to_dB(gain)
    return gain_dB


def power_received(gain_rx, gain_tx, distance, frequency, power_in, other):
    wavelength = c / frequency
    loss_freespace = ((4 * np.pi * distance) / wavelength) ^ 2
    loss_freespace_dB = W_to_dB(loss_freespace)

    power_out = power_in + gain_tx - loss_freespace_dB + gain_rx - other
    return power_out


def minimum_bandwidth_required(datarate, modulation_choice):
    ratio = modulation[modulation_choice]
    if (ratio == 0):
        return 10 * 10 ^ 6
    else:
        return (datarate / ratio)


def noise_received(bandwidth, antenna_SNR, gain):
    antenna_temp = dB_to_W(gain) / dB_to_W(antenna_SNR)
    noise = antenna_temp * k * bandwidth
    return noise


def doppler_shift(vel, frequency):
    wavelenght = c / frequency
    shift = vel / wavelenght
    return shift

def stage1_electronics(rocket: Rocket):
        #telemetry

    frequency = rocket.stage1.electronics.communicationsystem.frequency
    datarate = rocket.stage1.electronics.datarate
    margin = rocket.stage1.electronics.communicationsystem.margin

    gain_rx_db = antenna_gain(rocket.stage1.electronics.communicationsystem.diameter_antenna_gs, frequency, rocket.stage1.electronics.communicationsystem.antenna_efficiency_gs)
    power = W_to_dB(rocket.stage1.electronics.communicationsystem.power_com)
    gain_tx_db = W_to_dB(rocket.stage1.electronics.communicationsystem.gain_tx)
    power_rec = power_received(gain_rx_db, gain_tx_db, rocket.stage1.electronics.communicationsystem.max_range, frequency, power, 0)
    min_bw = minimum_bandwidth_required(datarate, rocket.stage1.electronics.communicationsystem.modulation)*(1+margin)
    
    N0 = noise_received(min_bw, rocket.stage1.electronics.communicationsystem.antenna_SNR, gain_rx_db)

    SNR = power_rec / N0

    capacity = (min_bw * np.log10(1 + SNR))

    assert capacity > (datarate * (1 + margin)), f" max capacity less than {datarate * (1 + margin)} expected, got: {capacity}"

    rocket.stage1.electronics.communicationsystem.capacity = capacity
    print("State 1 maximum allowable datarate is: ",capacity)

    rocket.stage1.electronics.communicationsystem.SNR = SNR
    print("State 1 total signal to noise ratio: ",SNR)

    delta_freq = doppler_shift(rocket.stage1.electronics.communicationsystem.max_speed, frequency)
    print("Expected doppler shift stage 1: ", delta_freq)
    assert min_bw > delta_freq, f"bandwidth greater than {delta_freq} expected, got: {min_bw}"
    assert min_bw < (10 * 10 ^ 6), f"bandwidth less than 10 MHz expected, got: {min_bw}"
    rocket.stage1.electronics.communicationsystem.bandwidth = min_bw
    print("State 1 total required bandwidth: ",min_bw)

    # power
    power_total = rocket.stage1.electronics.communicationsystem.power_com + rocket.stage1.electronics.power_sensors
    time = rocket.stage1.electronics.time

    energy = power_total * time / 3600

    rocket.stage1.electronics.powersystem.tot_power = power_total/(1-rocket.stage1.electronics.powersystem.dod)
    print("Stage 1 total required battery power: ", rocket.stage1.electronics.powersystem.tot_power)
    rocket.stage1.electronics.powersystem.mass_bat = energy/rocket.stage1.electronics.powersystem.power_density
    print("Stage 1 total required battery mass: ", rocket.stage1.electronics.powersystem.mass_bat)
    rocket.stage1.electronics.powersystem.volume_bat = energy/rocket.stage1.electronics.powersystem.power_volume
    print("Stage 1 total required battery volume: ", rocket.stage1.electronics.powersystem.mass_volume)
    bat_Ah = ((rocket.stage1.electronics.powersystem.tot_power)/rocket.stage1.electronics.powersystem.avg_voltage)*time
    rocket.stage1.electronics.powersystem.bat_size = bat_Ah
    print("State 1 total required battery Ah: ", bat_Ah)

    #blackbox
    storage = datarate*time*(1+rocket.stage1.electronics.blackbox.margin)
    print("State 1 total required storage: ",storage)
    rocket.stage1.electronics.blackbox.storage = storage

def stage2_electronics(rocket: Rocket):
    #telemetry

    frequency = rocket.stage2.electronics.communicationsystem.frequency
    datarate = rocket.stage2.electronics.datarate
    margin = rocket.stage2.electronics.communicationsystem.margin

    gain_rx_db = antenna_gain(rocket.stage2.electronics.communicationsystem.diameter_antenna_gs, frequency, rocket.stage2.electronics.communicationsystem.antenna_efficiency_gs)
    power = W_to_dB(rocket.stage2.electronics.communicationsystem.power_com)
    gain_tx_db = W_to_dB(rocket.stage2.electronics.communicationsystem.gain_tx)
    power_rec = power_received(gain_rx_db, gain_tx_db, rocket.stage2.electronics.communicationsystem.max_range, frequency, power, 0)
    min_bw = minimum_bandwidth_required(datarate, rocket.stage2.electronics.communicationsystem.modulation)

    N0 = noise_received(min_bw, rocket.stage2.electronics.communicationsystem.antenna_SNR, gain_rx_db)

    SNR = power_rec / N0

    capacity = (min_bw * np.log10(1 + SNR))

    assert capacity > (datarate * (1 + margin)), f" max capacity less than {datarate * (1 + margin)} expected, got: {capacity}"

    rocket.stage2.electronics.communicationsystem.capacity = capacity
    print("State 2 maximum allowable datarate is: ",capacity)


    rocket.stage2.electronics.communicationsystem.SNR = SNR
    print("State 2 total signal to noise ratio: ",SNR)

    delta_freq = doppler_shift(rocket.stage2.electronics.communicationsystem.max_speed, frequency)
    print("Expected doppler shift stage 2: ", delta_freq)

    assert min_bw > delta_freq, f"bandwidth greater than {delta_freq} expected, got: {min_bw}"
    assert min_bw < (10 * 10 ^ 6), f"bandwidth less than 10 MHz expected, got: {min_bw}"
    rocket.stage2.electronics.communicationsystem.bandwidth = min_bw
    print("State 2 total required bandwidth: ",min_bw)

    #power
    power_total = rocket.stage2.electronics.communicationsystem.power_com + rocket.stage2.electronics.power_sensors
    time = rocket.stage2.electronics.time

    energy = power_total * time / 3600

    rocket.stage2.electronics.powersystem.tot_power = power_total/(1-rocket.stage2.electronics.powersystem.dod)
    print("Stage 2 total required battery power: ", rocket.stage2.electronics.powersystem.tot_power)
    rocket.stage2.electronics.powersystem.mass_bat = energy/rocket.stage2.electronics.powersystem.power_density
    print("Stage 2 total required battery mass: ", rocket.stage2.electronics.powersystem.mass_bat)
    rocket.stage2.electronics.powersystem.volume_bat = energy/rocket.stage2.electronics.powersystem.power_volume
    print("Stage 2 total required battery volume: ", rocket.stage2.electronics.powersystem.mass_volume)
    bat_Ah = ((rocket.stage2.electronics.powersystem.tot_power)/rocket.stage2.electronics.powersystem.avg_voltage)*time
    rocket.stage2.electronics.powersystem.bat_size = bat_Ah
    print("Stage 2 total required battery Ah: ", bat_Ah)

    #blackbox
    storage = datarate*time*(1+rocket.stage2.electronics.blackbox.margin)
    print("State 2 total required storage: ",storage)
    rocket.stage2.electronics.blackbox.storage = storage


def stage2_payload(rocket: Rocket):
    datarate = rocket.stage2.payload.datarate
    #power
    power_total = rocket.stage2.payload.communicationsystem.power_com + rocket.stage2.payload.power_sensors
    time = rocket.stage2.payload.time

    energy = power_total*time/3600

    rocket.stage2.payload.powersystem.tot_power = power_total/(1-rocket.stage2.payload.powersystem.dod)
    print("Stage 2 total required battery power for payload: ", rocket.stage2.payload.powersystem.tot_power)
    rocket.stage2.payload.powersystem.mass_bat = energy/rocket.stage2.payload.powersystem.power_density
    print("Stage 2 total required battery mass for payload: ", rocket.stage2.payload.powersystem.mass_bat)
    rocket.stage2.payload.powersystem.volume_bat = energy/rocket.stage2.payload.powersystem.power_volume
    print("Stage 2 total required battery volume for payload: ", rocket.stage2.payload.powersystem.mass_volume)
    bat_Ah = ((rocket.stage2.payload.powersystem.tot_power)/rocket.stage2.payload.powersystem.avg_voltage)*time
    rocket.stage2.payload.powersystem.bat_size = bat_Ah
    print("Stage 2 total required battery Ah for the payload: ", bat_Ah)

    #blackbox
    storage = datarate*time*(1+rocket.stage2.payload.blackbox.margin)
    print("State 2 total required storage for the payload: ",storage)
    rocket.stage2.payload.blackbox.storage = storage


def do_stuff(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    #Stage 1

    stage1_electronics(rocket)
    #Stage 2

    #electronics
    stage2_electronics(rocket)

    #payload

    stage2_payload(rocket)















    


def run(rocket: Rocket) -> Rocket:
    """
    :param rocket: Original Rocket class
    :return: Updated Rocket class
    """

    do_stuff(rocket)

    return rocket


if __name__ == "__main__":
    test_rocket = Rocket()
    run(test_rocket)
