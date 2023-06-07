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

    

def do_stuff(rocket: Rocket):
    """
    :param rocket: Rocket class
    :return: None
    """

    pass


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
