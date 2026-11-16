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

<!-- Fill in which subjects were included, e.g. S1-S5 -->
Subjects: S1 to S5 (update if different).

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
