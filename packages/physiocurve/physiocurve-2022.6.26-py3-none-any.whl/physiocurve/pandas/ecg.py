from physiocurve.common import estimate_samplerate
from physiocurve.ecg import Ecg as EcgNp


class Ecg(EcgNp):
    def __init__(self, series, samplerate=None):
        self._series = series
        if samplerate is None:
            samplerate = estimate_samplerate(series)

        super().__init__(series.to_numpy(), samplerate)

    @property
    def idxrwave(self):
        return self._series.index[self.argrwave]

    @property
    def rwaves(self):
        return self._series.iloc[self.argrwave]
