"""Overlap-based multi-object tracking for a single continuous camera shot."""
from dataclasses import dataclass


def iou(left, right):
    x = max(0, min(left[2], right[2]) - max(left[0], right[0]))
    y = max(0, min(left[3], right[3]) - max(left[1], right[1]))
    intersection = x * y
    union = ((left[2] - left[0]) * (left[3] - left[1])
             + (right[2] - right[0]) * (right[3] - right[1]) - intersection)
    return intersection / union if union > 0 else 0


def match(previous, current, threshold):
    scores = sorted(
        ((iou(a, b), i, j) for i, a in enumerate(previous) for j, b in enumerate(current)),
        reverse=True,
    )
    used_previous, used_current = set(), set()
    pairs = []
    for score, i, j in scores:
        if score < threshold:
            break
        if i not in used_previous and j not in used_current:
            pairs.append((i, j))
            used_previous.add(i)
            used_current.add(j)
    return pairs


@dataclass
class Track:
    box: tuple
    frame: int


class Tracker:
    def __init__(self, threshold=0.2, max_gap=5):
        self.threshold = threshold
        self.max_gap = max_gap
        self.active = {}
        self.next_id = 1

    def update(self, frame, boxes):
        self.active = {
            key: track for key, track in self.active.items() if frame - track.frame <= self.max_gap
        }
        keys = list(self.active)
        matches = match([self.active[key].box for key in keys], boxes, self.threshold)
        assigned = {j: keys[i] for i, j in matches}
        for index, box in enumerate(boxes):
            key = assigned.get(index)
            if key is None:
                key = self.next_id
                self.next_id += 1
            self.active[key] = Track(tuple(box), frame)
            assigned[index] = key
        return [assigned[index] for index in range(len(boxes))]
