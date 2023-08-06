from .pressure import Pressure


class PPG(Pressure):
    def sqi(self):
        raise NotImplementedError
