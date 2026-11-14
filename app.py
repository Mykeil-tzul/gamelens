"""GameLens film review. The hosted demo uses precomputed tracking."""
import csv
import json
from collections import Counter
from pathlib import Path

import streamlit as st

DEMO = Path(__file__).resolve().parent / "demo"
st.set_page_config(page_title="GameLens", page_icon="🏀", layout="wide")
st.html("""
<style>
.film-header {background:linear-gradient(110deg,#211d38,#3d2849,#773823);
border:1px solid #67415d;border-radius:18px;padding:1.5rem 2rem;margin-bottom:1rem}
.film-header h1 {color:#fff4df;padding:0;margin:0}
.film-header p {color:#f5d9c7;margin:.4rem 0 0}
[data-testid=stMetric] {background:#1d2031;border-radius:12px;padding:.75rem}
</style>
<header class="film-header"><h1>🏀 GameLens</h1><p>Basketball film review with computer vision</p></header>
""")
catalog = json.loads((DEMO / "film" / "catalog.json").read_text())
options = {clip["title"]: clip for clip in catalog}
choice = st.selectbox("Film library", ["Outdoor pickup benchmark", *options])
clip = options.get(choice)
folder = DEMO / "film" / clip["id"] if clip else DEMO
run = json.loads((folder / "run.json").read_text())
with (folder / "tracks.csv").open() as file:
    tracks = [
        {key: float(value) if key in ("seconds", "confidence") else int(value)
         for key, value in row.items()}
        for row in csv.DictReader(file)
    ]
st.caption(clip["source"] if clip else "Outdoor pickup · U.S. and Indian Army players · Single camera shot")
for col, label, value in zip(
    st.columns(4), ("Clip duration", "Frames analyzed", "Person detections", "Track IDs"),
    (f"{run['frames'] / run['fps']:.1f} s", run["frames"], run["detections"], run["tracks"]),
):
    col.metric(label, value)

film, timeline, methods = st.tabs(["🎬 Film room", "📍 Track review", "🔍 Evaluation"])
with film:
    a, b = st.columns(2)
    for column, label, filename in [(a, "Original film", "original.mp4"), (b, "Computer vision overlay", "tracked.mp4")]:
        with column:
            st.subheader(label)
            st.video(str(folder / filename))
    st.caption("Boxes show person detections. IDs link overlapping boxes across frames and can change when people cross or disappear.")
    st.download_button("Download annotated clip", (folder / "tracked.mp4").read_bytes(),
                       "gamelens-tracked.mp4", "video/mp4")

    st.subheader("From my playing days")
    st.write("Mykeil Tzul · 2020 NEBL highlights from Belize. Reviewing film as a player is what inspired GameLens.")
    st.video("https://www.youtube.com/watch?v=jmASDMBrTlQ")
    st.markdown("[Watch on YouTube](https://www.youtube.com/watch?v=jmASDMBrTlQ) · Personal highlights shown as published.")
    st.markdown("[Watch my Senior Mixtape on YouTube](https://www.youtube.com/watch?v=GedXUBbXi3s)")

with timeline:
    frame = st.slider("Review frame", 0, run["frames"] - 1)
    selected = [row for row in tracks if row["frame"] == frame]
    st.write(f"**{frame / run['fps']:.2f}s** · {len(selected)} person detections")
    if selected:
        st.dataframe(selected, hide_index=True)
    else:
        st.info("No detections at the selected frame.")
    if tracks:
        counts = Counter(row["track_id"] for row in tracks)
        track = st.selectbox("Follow track ID", sorted(counts))
        trajectory = [row for row in tracks if row["track_id"] == track]
        st.write(f"Track #{track} appears in {counts[track]} frames, from {trajectory[0]['seconds']:.2f}s "
                 f"to {trajectory[-1]['seconds']:.2f}s.")
        st.scatter_chart({
            "Horizontal position": [(row["x1"] + row["x2"]) / 2 for row in trajectory],
            "Height above image bottom": [run["height"] - row["y2"] for row in trajectory],
        }, x="Horizontal position", y="Height above image bottom")
        st.caption("Positions are in video pixels. Camera movement affects the plot.")
    st.download_button("Download detection and track data", (folder / "tracks.csv").read_bytes(),
                       "gamelens-tracks.csv", "text/csv")

with methods:
    st.subheader("What GameLens measures")
    st.write("YOLOX detects people in each frame. The tracker matches overlapping boxes between "
             "frames, keeping short gaps open when a person disappears behind someone else.")
    st.write("Coaches and players can replay crowded clips, follow a track, and export timestamps "
             "for manual film review. The detector can also box spectators or officials.")
    st.write("Counts describe this run. A person may get multiple IDs, and the same ID may switch "
             "between people. Positions are in pixels. Team identity, possession, and court distance require separate validation.")
    evaluation = folder / "evaluation.json"
    if evaluation.exists():
        scores = json.loads(evaluation.read_text())
        st.subheader("Hand-labeled frame check")
        st.write(f"{scores['frames']} frames · IoU ≥ 0.50 · "
                 f"{scores['matched']} matches, {scores['missed']} misses, {scores['extra']} extra detections.")
        st.write(f"Precision {scores['precision']:.0%} · Recall {scores['recall']:.0%}")
        st.caption("One short shot. Detection check only; track identity accuracy is unmeasured.")
    if clip:
        st.caption("This personal clip has no hand-labeled accuracy score.")
    st.markdown("[Pickup benchmark footage credit · Sgt. Grayson Cavaliere, U.S. Army National Guard]"
                "(https://www.dvidshub.net/video/1023660/us-indian-army-soldiers-build-camaraderie-through-basketball-during-yudh-abhyas-2026)")
