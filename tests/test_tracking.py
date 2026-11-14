import unittest

from gamelens.evaluate import evaluate
from gamelens.tracker import Tracker, iou, match


class TrackingTests(unittest.TestCase):
    def test_overlap_and_unique_assignment(self):
        box = (0, 0, 10, 10)
        self.assertEqual(iou(box, box), 1)
        self.assertEqual(len(match([box, box], [box], .5)), 1)

    def test_short_gap_and_expiry(self):
        tracker = Tracker(max_gap=2)
        self.assertEqual(tracker.update(0, [(0, 0, 10, 10)]), [1])
        self.assertEqual(tracker.update(1, []), [])
        self.assertEqual(tracker.update(2, [(1, 0, 11, 10)]), [1])
        self.assertEqual(tracker.update(5, [(1, 0, 11, 10)]), [2])

    def test_detection_report(self):
        box = (0, 0, 10, 10)
        result = evaluate({0: [box], 1: [box]}, {0: [box, (20, 20, 30, 30)]})
        self.assertEqual((result["matched"], result["missed"], result["extra"]), (1, 1, 1))
        self.assertEqual((result["precision"], result["recall"]), (.5, .5))
