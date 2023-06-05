import numpy as np


class Bolt:
    def __init__(self, length: float, diameter: int, pitch: float):
        """
        :param length: The length of the bolt [mm]
        :param diameter: The diameter of the bolt shaft [mm]
        :param pitch: The pitch of the thread [mm]
        """
        self.length = length
        self.diameter = diameter

        self.thread = self.Thread(pitch)

    class Thread:
        def __init__(self, pitch: float):
            """
            :param pitch:
            """
            self.pitch = pitch

        def check_fit(self, pitch_hole):
            if self.pitch == pitch_hole:
                print('fits')
            else:
                print('does not fit')


m5 = Bolt(20, 5, 0.5)
m5.length = 5
print(m5.length)

m5.thread.check_fit(0.5)
