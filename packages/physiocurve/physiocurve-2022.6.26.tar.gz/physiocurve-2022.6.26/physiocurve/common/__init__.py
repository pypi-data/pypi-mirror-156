import numpy as np
from numba import njit


def estimate_samplerate(series):
    # This assumes datetime index
    idx = series.index.view(np.int64)
    intervals = np.diff(idx)
    # 1e9 to account for ns -> Hz
    fs = 1e9 // np.median(intervals)
    return fs if fs != np.inf else 0


def truncatevecs(vecs):
    # Ensure all vectors have the same length by truncating the end
    maxidx = min(map(len, vecs))
    return [vec[0:maxidx] for vec in vecs]


@njit
def find_local_max(arr, reference):
    sample_indexes = [reference - 1, reference, reference + 1]
    direction_window = np.take(arr, sample_indexes)
    direction = np.argmax(direction_window) - 1
    if direction == 0:
        # We're already at the local minimum
        return reference
    current_index = reference
    while True:
        nextloc = current_index + direction
        samplesoi = np.take(arr, [current_index, nextloc])
        nextisbetter = np.argmax(samplesoi)
        if not nextisbetter:
            # Minimum found
            break
        current_index = nextloc
    return current_index
