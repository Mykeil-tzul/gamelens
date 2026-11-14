"""Check person detection on manually labeled frames."""
import csv
import json
from pathlib import Path

from gamelens.tracker import match


def grouped_boxes(path):
    frames = {}
    with path.open() as file:
        for row in csv.DictReader(file):
            box = tuple(int(row[key]) for key in ("x1", "y1", "x2", "y2"))
            frames.setdefault(int(row["frame"]), []).append(box)
    return frames


def evaluate(labels, predictions):
    matched = missed = extra = 0
    for frame, expected in labels.items():
        detected = predictions.get(frame, [])
        hits = len(match(expected, detected, .50))
        matched += hits
        missed += len(expected) - hits
        extra += len(detected) - hits
    return dict(
        frames=len(labels), matched=matched, missed=missed, extra=extra,
        precision=matched / (matched + extra) if matched + extra else 0,
        recall=matched / (matched + missed) if matched + missed else 0,
    )


if __name__ == "__main__":
    demo = Path("demo")
    scores = evaluate(grouped_boxes(demo / "labels.csv"), grouped_boxes(demo / "tracks.csv"))
    (demo / "evaluation.json").write_text(json.dumps(scores, indent=2) + "\n")
    print(scores)
