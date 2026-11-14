"""Run pretrained YOLOX person detection and annotate a short video."""
import argparse
import csv
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import imageio_ffmpeg
import numpy as np

from gamelens.tracker import Tracker

SIZE = 640


class Detector:
    def __init__(self, model, threshold):
        self.network = cv2.dnn.readNetFromONNX(str(model))
        self.threshold = threshold
        grids = []
        strides = []
        for stride in (8, 16, 32):
            side = SIZE // stride
            x, y = np.meshgrid(np.arange(side), np.arange(side))
            grids.append(np.column_stack([x.ravel(), y.ravel()]))
            strides.extend([stride] * (side * side))
        self.grid = np.concatenate(grids)
        self.strides = np.asarray(strides)[:, None]

    def detect(self, frame):
        height, width = frame.shape[:2]
        ratio = min(SIZE / height, SIZE / width)
        resized = cv2.resize(frame, (int(width * ratio), int(height * ratio)))
        canvas = np.full((SIZE, SIZE, 3), 114, dtype=np.uint8)
        canvas[:resized.shape[0], :resized.shape[1]] = resized
        self.network.setInput(cv2.dnn.blobFromImage(canvas, swapRB=True))
        output = self.network.forward()[0]
        confidence = output[:, 4] * output[:, 5]
        mask = (confidence >= self.threshold) & (output[:, 5:].argmax(axis=1) == 0)
        scores = confidence[mask]
        center = (output[mask, :2] + self.grid[mask]) * self.strides[mask] / ratio
        size = np.exp(output[mask, 2:4]) * self.strides[mask] / ratio
        top = np.clip(center - size / 2, 0, [width - 1, height - 1])
        bottom = np.clip(center + size / 2, 0, [width - 1, height - 1])
        boxes = np.column_stack([top, bottom - top]).astype(int)
        kept = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), self.threshold, 0.45)
        return [
            (tuple(np.r_[boxes[i, :2], boxes[i, :2] + boxes[i, 2:]].tolist()), float(scores[i]))
            for i in np.asarray(kept, dtype=int).ravel()
            if min(boxes[i, 2:]) > 0
        ]


def analyze(source, model, destination, threshold=0.35):
    destination.mkdir(parents=True, exist_ok=True)
    cv2.setNumThreads(2)
    detector = Detector(model, threshold)
    tracker = Tracker()
    video = cv2.VideoCapture(str(source))
    rows = []
    with TemporaryDirectory() as directory:
        raw = Path(directory) / "annotated.mp4"
        fps = video.get(cv2.CAP_PROP_FPS)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not video.isOpened() or not fps or not width or not height:
            video.release()
            raise ValueError("Could not open video")
        writer = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        frame_id = 0
        try:
            if not writer.isOpened():
                raise RuntimeError("Could not initialize video writer")
            while True:
                ok, frame = video.read()
                if not ok:
                    break
                detections = detector.detect(frame)
                boxes = [box for box, _ in detections]
                for key, (box, score) in zip(tracker.update(frame_id, boxes), detections):
                    x1, y1, x2, y2 = box
                    rows.append((frame_id, round(frame_id / fps, 3), key, *box, round(score, 4)))
                    color = ((key * 53) % 155 + 100, (key * 89) % 155 + 100, (key * 31) % 155 + 100)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"#{key}", (x1, max(15, y1 - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, .52, color, 2, cv2.LINE_AA)
                writer.write(frame)
                frame_id += 1
        finally:
            writer.release()
            video.release()
        subprocess.run([
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(raw),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destination / "tracked.mp4"),
        ], check=True)
    with (destination / "tracks.csv").open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["frame", "seconds", "track_id", "x1", "y1", "x2", "y2", "confidence"])
        writer.writerows(rows)
    metadata = dict(frames=frame_id, fps=fps, width=width, height=height,
                    detections=len(rows), tracks=tracker.next_id - 1, threshold=threshold)
    (destination / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=.35)
    args = parser.parse_args()
    if not 0 < args.threshold < 1:
        parser.error("threshold must be between 0 and 1")
    analyze(args.video, args.model, args.output, args.threshold)


if __name__ == "__main__":
    main()
