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

The film room opens on **Highlight reel possession** from my own game film. Choose another clip in the **Film library**, then use **Replay both** or **Toggle half speed**. Each selection has its own annotated MP4 and frame-level tracking CSV. The local Streamlit app also lets you inspect one frame at a time and plot the path of a track ID.

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

These scores cover three frames from one outdoor shot. The five personal clips let you inspect the results under different camera angles. The featured clip has a separate identity audit below. The general-purpose detector finds spectators and other people, and overlapping players can get new IDs. The 63 track IDs in this clip are track fragments, not a count of distinct people. A broader identity benchmark would need multiple fully labeled clips.

## Identity audit on my featured possession

I marked the torso position of white jerseys 2 and 12 across the 80-frame highlight. Labels sample every six frames, the last frame, and extra frames around the screen. A detection matches when exactly one box covers the torso point. Multiple boxes count as ambiguous. Out-of-view and uncertain labels are excluded. An ID change across overlapping boxes is tracked separately from a clear switch. A gap begins when a visible label has zero covering boxes.

| Jersey | Visible labels | Unique matches | Missed | Ambiguous | Clear switches | Changes across overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| White 2 | 22 | 18 | 0 | 4 | 0 | 1 |
| White 12 | 10 | 9 | 0 | 1 | 0 | 0 |

White 2 was track ID 2 at frame 32. Frame 33 was ambiguous and frame 34 matched ID 12. The film room can jump straight to both sides of that change. This is a small, sample-based audit of two jerseys on one possession. Misses or switches between sampled frames can go undetected. The labels are jersey references for the audit, independent of the model’s temporary IDs.

Reproduce it from the repository root with `python -m gamelens.identity_audit`. See the [manual labels](demo/film/highlight-reel/identity-labels.csv) and [scored output](demo/film/highlight-reel/identity-audit.json).

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
