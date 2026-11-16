"""Train and evaluate the gesture model on Ninapro DB2 files.

Example:
    python scripts/train_ninapro.py data/ninapro/S1_E1_A1.mat data/ninapro/S2_E1_A1.mat
    python scripts/train_ninapro.py data/ninapro/S1_E1_A1.mat --db emg.db --plot
"""

import argparse
from pathlib import Path

import joblib
import numpy as np

from emg import db, ninapro
from emg.config import GESTURES, NINAPRO_CHANNELS
from emg.model import evaluate, make_lda, make_random_forest
from emg.signal import clean, rest_noise
from emg.windows import balance_rest, cut_windows


def prepare(path, channels):
    """Load a subject and return balanced X, y, groups plus window end times."""
    emg, labels, reps = ninapro.load(path, channels)
    emg = clean(emg)
    thresh = rest_noise(emg, labels)
    X, y, groups = cut_windows(emg, labels, reps, thresh, GESTURES)
    keep = balance_rest(y)
    return X[keep], y[keep], groups[keep]


def save_to_db(conn, path, X, y, groups, accuracy, models_dir: Path):
    """Store a subject as a fake 'calibration' and its final model, to exercise the database."""
    user_id = db.get_or_create_user(conn, ninapro.subject_name(path))
    session_id = db.start_session(conn, user_id, "calibration", raw_file=str(path),
                                  notes="Ninapro DB2, electrodes 8 + 9")
    t_ms = np.arange(len(y))  # Ninapro windows have no wall-clock time; keep their order
    db.save_windows(conn, session_id, t_ms, [GESTURES[k] for k in y], groups, X)
    db.end_session(conn, session_id)

    model = make_lda().fit(X, y)
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / f"{ninapro.subject_name(path)}_lda.joblib"
    joblib.dump(model, model_path)
    db.save_model(conn, user_id, "lda", 1, accuracy, model_path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+", help="Ninapro DB2 .mat files (exercise B, the E1 files)")
    p.add_argument("--channels", type=int, nargs="+", default=NINAPRO_CHANNELS,
                   help="0-based electrode indices (default: electrodes 8 and 9)")
    p.add_argument("--forest", action="store_true", help="also evaluate a random forest")
    p.add_argument("--db", help="save each subject and its model to this SQLite file")
    p.add_argument("--plot", action="store_true", help="show a confusion matrix per subject")
    args = p.parse_args()

    conn = db.connect(args.db) if args.db else None
    names = [GESTURES[k] for k in sorted(GESTURES)]
    results = []

    for path in ninapro.expand(args.files):
        X, y, groups = prepare(path, args.channels)
        pred = evaluate(make_lda(), X, y, groups)
        acc = float(np.mean(pred == y))
        line = f"{ninapro.subject_name(path)}: LDA {acc:.1%}"
        if args.forest:
            pred_rf = evaluate(make_random_forest(), X, y, groups)
            line += f", random forest {np.mean(pred_rf == y):.1%}"
        print(line)
        results.append(acc)

        if conn:
            save_to_db(conn, path, X, y, groups, acc, Path("models"))
        if args.plot:
            import matplotlib.pyplot as plt
            from sklearn.metrics import ConfusionMatrixDisplay
            ConfusionMatrixDisplay.from_predictions(y, pred, display_labels=names)
            plt.title(f"{ninapro.subject_name(path)} (LDA {acc:.1%})")
            plt.show()

    if len(results) > 1:
        print(f"Average {np.mean(results):.1%}, worst {np.min(results):.1%}")


if __name__ == "__main__":
    main()
