"""Score visible jersey identities, using hand-marked torso points and saved boxes."""
import csv
import json
from collections import defaultdict
from pathlib import Path

CLIP = Path(__file__).resolve().parents[1] / "demo/film/highlight-reel"


def audit(labels, tracks):
    by_frame = defaultdict(list)
    for box in tracks:
        by_frame[int(box["frame"])].append(box)
    results = {}
    observations = []
    for mark in sorted(labels, key=lambda row: (int(row["frame"]), row["player"])):
        player = mark["player"]
        frame = int(mark["frame"])
        if player not in results:
            results[player] = dict(visible=0, matched=0, missed=0, ambiguous=0, switches=0, across_ambiguity=0, gaps=0)
        counts = results[player]
        status, track_id = mark["state"], None
        if status == "visible":
            counts["visible"] += 1
            x, y = int(mark["x"]), int(mark["y"])
            candidates = [box for box in by_frame[frame]
                          if int(box["x1"]) <= x <= int(box["x2"]) and int(box["y1"]) <= y <= int(box["y2"])]
            status = "missed"
            if len(candidates) == 1:
                status, track_id = "matched", int(candidates[0]["track_id"])
            elif candidates:
                status = "ambiguous"
            counts[status] += 1
        observations.append(dict(frame=frame, player=player, status=status, track_id=track_id))

    for player, counts in results.items():
        previous_id = None
        in_gap = crossed_ambiguity = False
        for row in (item for item in observations if item["player"] == player):
            current = row["track_id"]
            if row["status"] in ("out", "uncertain"):
                previous_id, in_gap, crossed_ambiguity = None, False, False
            elif row["status"] == "missed":
                counts["gaps"] += not in_gap
                in_gap = True
            else:
                in_gap = False
            if row["status"] == "ambiguous":
                crossed_ambiguity = True
            if current is not None:
                if previous_id is not None and previous_id != current:
                    counts["across_ambiguity" if crossed_ambiguity else "switches"] += 1
                    row["id_changed"] = True
                previous_id, crossed_ambiguity = current, False
    return {"players": results, "observations": observations}


def main():
    with (CLIP / "identity-labels.csv").open(newline="") as labels, (CLIP / "tracks.csv").open(newline="") as tracks:
        result = audit(csv.DictReader(labels), csv.DictReader(tracks))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
