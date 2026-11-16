# Results

All results use Ninapro DB2, exercise B, with 4 gestures: rest, fist, wrist down (flexion) and
wrist up (extension). Features: MAV, RMS, WL, ZC and SSC per electrode, on 200 ms windows every
50 ms. Model: LDA. Testing holds out one whole repetition at a time (6 repetitions).
Chance is 25%.

## Subject 1 only

| Electrodes | Accuracy | Notes |
|---|---|---|
| 9 + 10 | 81.8% | Wrist up and wrist down were the main confusion |
| 1 + 12 | 73.5% | Wrist up dropped to 42% |
| 7 + 8 | 85.5% | Wrist up/down accuracy 83.6% |
| All 12 | 90.5% | Fist confusion almost gone; wrist up/down still the main error |

## Across subjects

Subjects: 14 (S1, S2, S3, S4, S7, S9, S12, S14, S15, S17, S23, S24, S35, S40). This table came
from the MATLAB version of the pair search (movmean downsampling, 50 Hz notch), not from
`scripts/pair_search.py`. Rerun that script to confirm it with this repo's pipeline.

| Electrodes | Average | Worst subject |
|---|---|---|
| **8 + 9** | **74.4%** | **60.2%** |
| 4 + 8 | 74.2% | 57.6% |
| 8 + 10 | 73.9% | 59.6% |
| 3 + 8 | 73.4% | 54.3% |
| 9 + 10 | 72.7% (rank 8 of 66) | 47.0% |

## What this showed

- **Electrodes 7 + 8 were luck.** They were best on subject 1 but not in the top 5 across
  subjects. Choosing the best of 66 pairs on one person overstates how good that pair is.
- **Electrode 8 is the real finding.** It's in every one of the top 4 pairs; its partner
  barely matters (the top 4 averages are within 1 point).
- **The worst case matters as much as the average.** 9 + 10 is only about 2 points behind on
  average, but its worst subject falls to 47%, compared with 60.2% for 8 + 9.
- **Subject 1 was an easy case** (82-86%), about 10 points above the average.

## Decision

Use **electrodes 8 + 9**: the best average and the best worst subject. The MyoWare sensors go
where those electrodes sit in the DB2 electrode diagram.

## Python pipeline check (electrodes 8 + 9, 13 subjects)

`python scripts/train_ninapro.py "S*_E1_A1.mat" --db emg.db` on S2, S3, S4, S7, S9, S12, S14,
S15, S17, S23, S24, S35, S40: **average 73.5%, worst 57.0% (S4)**. That is within about a point of
the MATLAB result for 8 + 9; the subject sets differ (no S1 here). Note the worst subject here
(S4, 57.0%) is lower than the MATLAB worst for this pair (60.2%).

| Subject | LDA | | Subject | LDA |
|---|---|---|---|---|
| S4 | 57.0% | | S24 | 77.4% |
| S7 | 59.9% | | S12 | 79.3% |
| S35 | 63.9% | | S14 | 79.9% |
| S17 | 65.1% | | S15 | 80.7% |
| S2 | 67.1% | | S9 | 88.6% |
| S23 | 68.8% | | S40 | 91.5% |
| S3 | 76.6% | | | |

## Database checks (emg.db from the run above)

- 13 users, 13 sessions, 13 models, 24,094 windows; `actions` and `prompts` empty, as expected.
- Windows per subject: 1,087 (S15) to 2,927 (S7).
- Balancing works: in every subject, rest has exactly as many windows as the largest gesture.

Average MAV per gesture across all subjects (microvolts; subjects differ in scale, so compare
within a column):

| Gesture | Sensor 1 (electrode 8) | Sensor 2 (electrode 9) |
|---|---|---|
| rest | 7.6 | 5.2 |
| fist | 25.0 | 20.5 |
| wrist_down | 27.1 | **51.6** |
| wrist_up | **66.6** | 19.6 |

What this shows:

- **Each sensor owns one wrist direction.** Electrode 9 fires hardest for wrist down (flexion),
  electrode 8 for wrist up (extension). That is why two sensors separate the wrist gestures.
- **Fist is co-contraction:** both sensors moderately active, neither dominant. Fist sits
  between the two wrist gestures, which is where confusion with them comes from.
- **The `flex_`/`ext_` column names are backwards.** `flex_` is electrode 8, which acts as the
  extensor here; `ext_` is electrode 9, which acts as the flexor. Rename in `emg/config.py`
  before real calibration data goes into the database.
