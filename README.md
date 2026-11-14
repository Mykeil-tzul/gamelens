# GameLens

[Open the film room](https://mykeil-tzul.github.io/gamelens/)

I built GameLens to help coaches and players review crowded basketball clips. The film room pairs original footage with a computer vision overlay. You can replay both videos, slow them down, and download the annotated clip and its track data. The local Streamlit app adds a frame inspector and a plot for each track.

The film room also includes [my 2020 NEBL highlights](https://www.youtube.com/watch?v=jmASDMBrTlQ) from Belize. Playing and reviewing game film inspired this project. The evaluation below uses the pickup clip with the tracking overlay.

## Personal film library

The film picker includes five short excerpts from my supplied videos. Each plays alongside its own YOLOX overlay and has downloadable frame-level track data. I trimmed the longer reels to individual plays and removed audio. I cropped decorative padding from three vertical exports so the court fills more of the model input. The Drive copy shows the same half-court play as one of the attachments.

The personal clips are qualitative examples. Track IDs may change during contact, occlusion, or camera movement. The hand-labeled results below apply to the outdoor pickup benchmark.

## What the model does

OpenCV runs a pretrained YOLOX detector on each frame and keeps boxes classified as people. An overlap tracker matches those boxes across frames and assigns temporary IDs. This can help a coach find the moment two players cross or an athlete disappears behind a defender. The IDs are temporary labels and the positions are measured in pixels. The project does not identify players by name or measure possession, team, speed, or court distance.

## Results from the demo

The included pickup clip contains 28 frames at 15 fps. I labeled on-court player boxes on three frames and matched detections one to one at an intersection-over-union threshold of 0.50.

| Metric | Result |
| --- | ---: |
| Matched player boxes | 15 |
| Missed player boxes | 1 |
| Extra person detections | 17 |
| Precision against player labels | 46.9% |
| Recall against player labels | 93.8% |

This is a small diagnostic check on one shot. The general-purpose detector finds spectators and other people, and overlapping players can get new IDs. The 63 track IDs in this clip are track fragments, not a count of distinct people. Identity accuracy still needs labels that follow each player over time. The next evaluation I would run is a fixed-camera clip with labeled identities and a court boundary to check whether off-court detections and ID switches drop.

## Run it

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m unittest discover -s tests -v
python -m gamelens.evaluate
```

To analyze your own single-shot clip, use Python 3.10+ and install `requirements-vision.txt`. Download the [OpenCV YOLOX ONNX model](https://huggingface.co/opencv/object_detection_yolox/blob/main/object_detection_yolox_2022nov.onnx) and run:

```bash
python -m pip install -r requirements-vision.txt
python -m gamelens.analyze my-clip.mp4 --model object_detection_yolox_2022nov.onnx --output runs/my-clip
```

The model used here has SHA-256 `c5c2d13e59ae883e6af3b45daea64af4833a4951c92d116ec270d9ddbe998063`. Trim clips to one continuous camera shot before running. The hosted film room plays precomputed results and the command-line tool runs inference on new footage.

## Footage credit

The demo is a silent, resized excerpt beginning at 15.35 seconds in [U.S., Indian Army Soldiers build camaraderie through basketball during Yudh Abhyas 2026](https://www.dvidshub.net/video/1023660/us-indian-army-soldiers-build-camaraderie-through-basketball-during-yudh-abhyas-2026), filmed by Sgt. Grayson Cavaliere, U.S. Army National Guard. [Wikimedia Commons identifies it as public domain in the United States](https://commons.wikimedia.org/wiki/File:U_S_,_Indian_Army_Soldiers_build_camaraderie_through_basketball_during_Yudh_Abhyas_2026_(1023660).webm).
