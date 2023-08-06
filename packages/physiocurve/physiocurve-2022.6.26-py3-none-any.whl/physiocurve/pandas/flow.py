from physiocurve.common import estimate_samplerate
from physiocurve.flow import Flow as FlowNp


class Flow(FlowNp):
    def __init__(self, series, samplerate=None):
        self._series = series
        if samplerate is None:
            samplerate = estimate_samplerate(series)

        super().__init__(series.to_numpy(), samplerate)

    @property
    def idxstarts(self):
        return self._series.index[self.argstarts]

    @property
    def starts(self):
        return self._series.iloc[self.argstarts]

    @property
    def idxstops(self):
        return self._series.index[self.argstops]

    @property
    def stops(self):
        return self._series.iloc[self.argstops]
