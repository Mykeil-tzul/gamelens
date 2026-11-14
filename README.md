# GameLens

[**Open the live GameLens film room**](https://mykeil-tzul.github.io/gamelens/)

I built GameLens because reviewing game film as a player taught me how much you can miss at full speed. It puts the original play beside a computer vision overlay so a player or coach can replay the action, slow it down, and see where the tracker follows someone or loses them in traffic.

## Explore the film library

| Clip | What to look for |
| --- | --- |
| Half-court set | Players moving through a crowded half court |
| End-to-end transition | How the tracker handles a moving camera |
| Fast break | Players entering and leaving the frame |
| Highlight reel possession | Tracking in a wide game-film shot |
| Baseline camera | Players overlapping near the basket |
| Outdoor pickup benchmark | The clip used for the hand-labeled detection check |

Choose a clip in the **Film library**, then use **Replay both** or **Toggle half speed**. Each selection has its own annotated MP4 and frame-level tracking CSV. The local Streamlit app also lets you inspect one frame at a time and plot the path of a track ID.

The five excerpts come from my own game-film collection. I trimmed them to short plays, removed audio, and cropped padding from three vertical exports so the court fills more of the model input. The film room also links to [my 2020 NEBL highlights](https://www.youtube.com/watch?v=jmASDMBrTlQ) and [my Senior Mixtape](https://www.youtube.com/watch?v=GedXUBbXi3s).

## What the model does

OpenCV runs a pretrained YOLOX detector on each frame and keeps boxes classified as people. An overlap tracker matches those boxes across frames and assigns temporary IDs. This can help a coach find the moment two players cross or an athlete disappears behind a defender. The IDs are temporary labels and the positions are measured in pixels. Track IDs are clip-local. Identifying players or measuring court distance would require additional models and validation.

## Evaluation on the outdoor pickup clip

The included pickup clip contains 28 frames at 15 fps. I labeled on-court player boxes on three frames and matched detections one to one at an intersection-over-union threshold of 0.50.

| Metric | Result |
| --- | ---: |
| Matched player boxes | 15 |
| Missed player boxes | 1 |
| Extra person detections | 17 |
| Precision against player labels | 46.9% |
| Recall against player labels | 93.8% |

These scores cover three frames from one outdoor shot. The five personal clips let you inspect the results under different camera angles and are unscored. The general-purpose detector finds spectators and other people, and overlapping players can get new IDs. The 63 track IDs in this clip are track fragments, not a count of distinct people. Identity accuracy still needs labels that follow each player over time. The next evaluation I would run is a fixed-camera clip with labeled identities and a court boundary to check whether off-court detections and ID switches drop.

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

The outdoor pickup benchmark is a silent, resized excerpt beginning at 15.35 seconds in [U.S., Indian Army Soldiers build camaraderie through basketball during Yudh Abhyas 2026](https://www.dvidshub.net/video/1023660/us-indian-army-soldiers-build-camaraderie-through-basketball-during-yudh-abhyas-2026), filmed by Sgt. Grayson Cavaliere, U.S. Army National Guard. [Wikimedia Commons identifies it as public domain in the United States](https://commons.wikimedia.org/wiki/File:U_S_,_Indian_Army_Soldiers_build_camaraderie_through_basketball_during_Yudh_Abhyas_2026_(1023660).webm).
