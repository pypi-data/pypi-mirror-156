from functools import cached_property

import neurokit2 as nk


class Ecg:
    def __init__(self, values, samplerate):
        self._samplerate = samplerate
        self._values = nk.ecg_clean(values, sampling_rate=samplerate)

    @property
    def samplerate(self):
        return self._samplerate

    @cached_property
    def argrwave(self):
        info = nk.ecg_findpeaks(self._values, sampling_rate=self._samplerate)
        return info['ECG_R_Peaks']

    @cached_property
    def _otherpeaks(self):
        info, _ = nk.ecg_delineate(
            self._values, rpeaks=self.argrwave, sampling_rate=self._samplerate
        )
        # ['ECG_P_Peaks', 'ECG_P_Onsets', 'ECG_P_Offsets', 'ECG_Q_Peaks',
        # 'ECG_R_Onsets', 'ECG_R_Offsets', 'ECG_S_Peaks', 'ECG_T_Peaks',
        # 'ECG_T_Onsets', 'ECG_T_Offsets']
        return info
