import numpy as np
from physiocurve.common import truncatevecs


def find_flow_cycles(values):
    bincycles = values > np.min(values)
    diff = np.diff(bincycles)
    cycle_starts = np.flatnonzero(diff > 0)
    cycle_stops = np.flatnonzero(diff < 0)

    # Handle the case where we start within a cycle
    for n, s in enumerate(cycle_stops):
        if s > cycle_starts[0]:
            break

    return truncatevecs((cycle_starts, cycle_stops[n:]))
