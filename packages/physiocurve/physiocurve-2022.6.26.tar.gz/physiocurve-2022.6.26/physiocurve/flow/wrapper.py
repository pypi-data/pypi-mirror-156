from functools import cached_property

from physiocurve.flow import find_flow_cycles


class Flow:
    def __init__(self, values, samplerate):
        self._values = values
        self._samplerate = samplerate

    @property
    def samplerate(self):
        return self._samplerate

    @cached_property
    def _argstartstop(self):
        return find_flow_cycles(self._values)

    @property
    def argstarts(self):
        starts, _ = self._argstartstop
        return starts

    @property
    def argstops(self):
        _, stops = self._argstartstop
        return stops
