import numpy as np
from matplotlib.patches import Patch
from collections.abc import Sequence

import logging

logger = logging.getLogger(__name__)

MAGNET_WIDTH = 0.1

# DEFAULT_COLOUR_MAP = Quadrupole

# If this was actually good: the survey would be generated AUTOMATICALLY from
# the beam angles and tilts! And some offset (with angle) would just belong to
# the beamline! instance. And could maybe even support different visualistion
# backends 🤔.

# Actually to get rotations to work properly, this is more or less necessary,
# because otherwise I have no way of knowing the orientation of a given element
# in XYZ space (survey) without inspecting surrounding elements. So could also
# just be an interface change, without so much work, but i think a
# "beamline.getRotation(element)" etc approach would be the best approach.

class Beamline(Sequence):
    def __init__(self, items):
        self._sequence = list(items)

    def __getitem__(self, key):
        return self._sequence[key]

    def __len__(self):
        return len(self._sequence)

    def add_offset(self, position):
        for element in self:
            element.position += position


class Element:
    def __init__(self, name, position, length, **misc):
        """For now position is the END?  survey and S can be dengerate, x and y
        just stay 0...

        """
        self.name = name
        self.position = np.array(position)
        self.length = length
        self.misc = misc

    def __repr__(self):
        typename = type(self).__name__
        return f"<{typename}: name={self.name}, r={self.position}, l={self.length}>"

    def is_powered(self):
        return True


class ThinElement(Element):
    def __init__(self, name, position, **misc):
        super().__init__(name, position, 0, **misc)

class Marker(ThinElement):
    pass


class Monitor(ThinElement):
    pass


class Drift(Element):
    pass


class SimpleDipole(Element):
    def __init__(self, name, position, length, angle, **misc):
        super().__init__(name, position, length, **misc)
        self.angle = angle

    def is_powered(self):
        return self.angle != 0


    # def strength(self):
    #     return self.k1


class RBend(SimpleDipole):
    pass


class SBend(SimpleDipole):
    pass


class HKicker(SimpleDipole):
    pass


class VKicker(SimpleDipole):
    pass


class Kicker(SimpleDipole):
    pass


class Quadrupole(Element):
    def __init__(self, name, position, length, k1, **misc):
        super().__init__(name, position, length, **misc)
        self.k1 = k1

    def is_powered(self):
        # import numpy as np
        return True
        return self.k1 != 0

    # def strength(self):
    #     # return np.random.rand() - 0.5
    #     return self.k1

class Sextupole(Element):
    def __init__(self, name, position, length, k2, **misc):
        super().__init__(name, position, length, **misc)
        self.k2 = k2


class Octupole(Element):
    def __init__(self, name, position, length, k3, **misc):
        super().__init__(name, position, length, **misc)
        self.k3 = k3


class RFCavity(Element):
    pass


class Solenoid(Element):
    def __init__(self, name, position, length, ks, **misc):
        super().__init__(name, position, length, **misc)
        self.ks = ks

class Collimator(Element):
    pass


class Cavity(Element):
    pass


class GenericMap(Element):
    pass


class TransverseDeflectingCavity(Element):
    def __init__(self, name, position, length, voltage, **misc):
        super().__init__(name, position, length, **misc)
        self.voltage = voltage


class Undulator(Element):
    pass
