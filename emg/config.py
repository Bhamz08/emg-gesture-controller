"""Settings shared by every part of the project. Change them here, nowhere else."""

FS = 1000    # samples per second (Ninapro is downsampled to match the Pico)
WIN = 200    # window length in samples (200 ms)
STEP = 50    # a new window starts every 50 samples (50 ms)

# Ninapro DB2 exercise B gesture numbers. Check against the DB2 movement list.
GESTURES = {0: "rest", 6: "fist", 13: "wrist_down", 14: "wrist_up"}

# Ninapro electrodes 8 and 9 (Python counts from 0). Chosen by scripts/pair_search.py:
# best average and best worst-subject accuracy across subjects. See results.md.
NINAPRO_CHANNELS = [7, 8]

# Feature names, in the order emg.features.features() returns them.
# Sensor 1 = "flex", sensor 2 = "ext" (for Ninapro: electrode 8 and electrode 9).
FEATURE_NAMES = [
    f"{sensor}_{feat}"
    for sensor in ("flex", "ext")
    for feat in ("mav", "rms", "wl", "zc", "ssc")
]
