from physiocurve.common import estimate_samplerate
from physiocurve.pressure import Pressure as PressureNp


class Pressure(PressureNp):
    def __init__(self, series, samplerate=None):
        self._series = series
        if samplerate is None:
            samplerate = estimate_samplerate(series)

        super().__init__(series.to_numpy(), samplerate)

    @property
    def idxfeet(self):
        return self._series.index[self.argfeet]

    @property
    def feet(self):
        return self._series.iloc[self.argfeet]

    @property
    def idxdia(self):
        return self._series.index[self.argdia]

    @property
    def diastolics(self):
        return self._series.iloc[self.argdia]

    @property
    def idxsys(self):
        return self._series.index[self.argsys]

    @property
    def systolics(self):
        return self._series.iloc[self.argsys]

    @property
    def idxdic(self):
        return self._series.index[self.argdic]

    @property
    def dicrotics(self):
        return self._series.iloc[self.argdic]
