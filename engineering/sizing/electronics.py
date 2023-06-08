from engineering.sizing.rocket import Rocket
import numpy as np
#Constant values:
k = 1.38*10^-23  #boltzman constant
c = 3*10^8       #m/s

modulation = {
    "BPSK": 0.5, "OOK": 0.5, "QPSK": 1, "OQPSK": 1, "FSK": 0
    }

def dB_to_W(value_dB):
    watt = 10^(value_dB/10)
    return watt

def W_to_dB(value_w):
    dB = 10* np.log10(value_w)
    return dB

def antenna_gain(size, frequency, efficiency):
    wavelength = c/frequency
    gain = ((np.pi * size)^2)*(efficiency/wavelength)
    gain_dB = W_to_dB(gain)
    return gain_dB

def power_received(gain_rx, gain_tx, distance, frequency, power_in, other):
    wavelength = c/frequency
    loss_freespace = ((4*np.pi*distance)/wavelength)^2
    loss_freespace_dB = W_to_dB(loss_freespace)

    power_out = power_in + gain_tx - loss_freespace_dB + gain_rx - other
    return power_out

def minimum_bandwidth_required(datarate, modulation_choice):
    ratio = modulation[modulation_choice]
    if (ratio == 0):
        return 10*10^6
    else:
        return (datarate/ratio)


def noise_received(bandwidth, antenna_SNR, gain):
    antenna_temp = dB_to_W(gain)/dB_to_W(antenna_SNR)
    noise = antenna_temp*k*bandwidth
    return noise

def doppler_shift(vel, frequency):
    wavelenght = c/frequency
    shift = vel/wavelenght
    return shift

    

def do_stuff(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """
    #Stage 1

    #telemetry

    frequency = rocket.stage1.electronics.communicationsystem.frequency
    datarate = rocket.stage1.electronics.datarate
    margin = rocket.stage1.electronics.communicationsystem.margin
    
    gain_rx_db = antenna_gain(rocket.stage1.electronics.communicationsystem.diameter_antenna_gs, frequency, rocket.stage1.electronics.communicationsystem. antenna_efficiency_gs)
    power = W_to_dB(rocket.stage1.electronics.communicationsystem.power_com)
    gain_tx_db = W_to_dB(rocket.stage1.electronics.communicationsystem.gain_tx)
    power_rec = power_received(gain_rx_db, gain_tx_db, rocket.stage1.electronics.communicationsystem.max_range, frequency, power, 0)
    min_bw = minimum_bandwidth_required(datarate, rocket.stage1.electronics.communicationsystem.modulation)
    
    N0 = noise_received(min_bw, rocket.stage1.electronics.communicationsystem.antenna_SNR, gain_rx_db)

    SNR = power_rec/N0

    capacity = (min_bw*np.log10(1+SNR))

    assert capacity > (datarate*(1+margin)), f" max capacity less than {datarate*(1+margin)} expected, got: {capacity}"

    rocket.stage1.electronics.communicationsystem.capacity = capacity

    rocket.stage1.electronics.communicationsystem.SNR = SNR

    delta_freq = doppler_shift(rocket.stage1.electronics.communicationsystem.max_speed, frequency)

    assert min_bw > delta_freq, f"bandwidth greater than {delta_freq} expected, got: {min_bw}"
    assert min_bw < (10*10^6), f"bandwidth less than 10 MHz expected, got: {min_bw}"
    rocket.stage1.electronics.communicationsystem.bandwidth = min_bw


    #power
    power_total = rocket.stage1.electronics.communicationsystem.power_com + rocket.stage1.electronics.power_sensors
    time = rocket.stage1.electronics.time

    energy = power_total*time/3600

    rocket.stage1.electronics.powersystem.tot_power = power_total
    rocket.stage1.electronics.powersystem.mass_bat = energy/rocket.stage1.electronics.powersystem.power_density
    rocket.stage1.electronics.powersystem.volume_bat = energy/rocket.stage1.electronics.powersystem.power_volume

    #blackbox
    storage = datarate*time*(1+rocket.stage1.electronics.blackbox.margin)
    rocket.stage1.electronics.blackbox.storage = storage

    #Stage 2

        #telemetry

    frequency = rocket.stage2.electronics.communicationsystem.frequency
    datarate = rocket.stage2.electronics.datarate
    margin = rocket.stage2.electronics.communicationsystem.margin
    
    gain_rx_db = antenna_gain(rocket.stage2.electronics.communicationsystem.diameter_antenna_gs, frequency, rocket.stage2.electronics.communicationsystem. antenna_efficiency_gs)
    power = W_to_dB(rocket.stage2.electronics.communicationsystem.power_com)
    gain_tx_db = W_to_dB(rocket.stage2.electronics.communicationsystem.gain_tx)
    power_rec = power_received(gain_rx_db, gain_tx_db, rocket.stage2.electronics.communicationsystem.max_range, frequency, power, 0)
    min_bw = minimum_bandwidth_required(datarate, rocket.stage2.electronics.communicationsystem.modulation)
    
    N0 = noise_received(min_bw, rocket.stage2.electronics.communicationsystem.antenna_SNR, gain_rx_db)

    SNR = power_rec/N0

    capacity = (min_bw*np.log10(1+SNR))

    assert capacity > (datarate*(1+margin)), f" max capacity less than {datarate*(1+margin)} expected, got: {capacity}"

    rocket.stage2.electronics.communicationsystem.capacity = capacity

    rocket.stage2.electronics.communicationsystem.SNR = SNR

    delta_freq = doppler_shift(rocket.stage2.electronics.communicationsystem.max_speed, frequency)

    assert min_bw > delta_freq, f"bandwidth greater than {delta_freq} expected, got: {min_bw}"
    assert min_bw < (10*10^6), f"bandwidth less than 10 MHz expected, got: {min_bw}"
    rocket.stage2.electronics.communicationsystem.bandwidth = min_bw


    #power
    power_total = rocket.stage2.electronics.communicationsystem.power_com + rocket.stage2.electronics.power_sensors
    time = rocket.stage2.electronics.time

    energy = power_total*time/3600

    rocket.stage2.electronics.powersystem.tot_power = power_total
    rocket.stage2.electronics.powersystem.mass_bat = energy/rocket.stage2.electronics.powersystem.power_density
    rocket.stage2.electronics.powersystem.volume_bat = energy/rocket.stage2.electronics.powersystem.power_volume

    #blackbox
    storage = datarate*time*(1+rocket.stage2.electronics.blackbox.margin)
    rocket.stage2.electronics.blackbox.storage = storage









    


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