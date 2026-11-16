# EMG Gesture Controller

Control a laptop with forearm gestures. Two EMG muscle sensors stream to a Python model that
recognizes the gesture and presses the matching key: flick your wrist to change slides, make a
fist to pause a video. A SQLite database records every session, model and action, so the system
can measure its own accuracy and improve.

| Gesture | Action |
|---|---|
| Rest | Nothing |
| Wrist flick up | Next slide (right arrow) |
| Wrist flick down | Previous slide (left arrow) |
| Fist | Play or pause (space bar) |
| Double fist | Turn control on or off |

## Status

- [x] Model pipeline built and tested on Ninapro DB2 (filters, features, LDA, honest evaluation)
- [x] Electrode placement chosen from data: electrodes 8 + 9 (see [results.md](results.md))
- [x] SQLite database schema and save/load functions
- [x] Pico firmware that streams both sensors at 1,000 Hz
- [ ] Sensors wired, live signal plot
- [ ] Calibration app
- [ ] Live control with smoothing and on/off
- [ ] Prompt test, typing test, multi-person results
- [ ] Demo video

## How it works

1. Two MyoWare 2.0 sensors on the forearm pick up muscle signals (EMG).
2. A Raspberry Pi Pico reads both at 1,000 Hz and streams them over USB (`firmware/main.c`).
3. Python filters the signal (20 Hz high-pass, 60 Hz notch) and cuts it into 200 ms windows.
4. Each window becomes 10 features: MAV, RMS, waveform length, zero crossings and slope sign
   changes for each sensor.
5. An LDA classifier picks the gesture; smoothing makes sure it was intended before a key is pressed.
6. Everything is logged to SQLite for measurement and retraining.

## Repo layout

```
emg/                  the core code, shared by offline training and the live system
  config.py           all settings (sample rate, windows, gestures, electrodes)
  signal.py           filtering
  features.py         the 10 features per window
  windows.py          cutting windows and balancing classes
  ninapro.py          loading Ninapro DB2 files
  model.py            models and leave-one-repetition-out evaluation
  db.py               SQLite schema and helpers
scripts/
  train_ninapro.py    train and evaluate on Ninapro subjects
  pair_search.py      rank all 66 electrode pairs across subjects
firmware/main.c       Pico code that streams both sensors
tests/                pytest tests, run on every push by GitHub Actions
data/                 put Ninapro files here (not committed)
results.md            findings so far
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac or Linux
pip install -e ".[dev]"
pytest
```

## Usage

```
python scripts/train_ninapro.py data/ninapro/S1_E1_A1.mat --plot
python scripts/train_ninapro.py data/ninapro/S*_E1_A1.mat --forest --db emg.db
python scripts/pair_search.py data/ninapro/S1_E1_A1.mat data/ninapro/S2_E1_A1.mat
```

See [data/README.md](data/README.md) for getting the Ninapro files.

## Safety

Only connect the sensors to your body while the laptop runs on battery, unplugged from the wall.
Keep electrodes on the forearm.
