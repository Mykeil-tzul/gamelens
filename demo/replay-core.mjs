// Retrieval is grounded in timestamped annotations. No video events are invented.
export const library = [
  {id:"shot-gather", clip:"highlight-reel", title:"Shot gather with a defender nearby", start:2.5, end:4.3,
   tags:["shooting","gather","defender","half court"], note:"The light-jersey ball handler bends his knees and lifts the ball into a shooting motion. Replay the gather and contest.", source:"Visual review of the published excerpt"},
  {id:"identity-overlap", clip:"highlight-reel", title:"A tracking ID changes across overlapping boxes", start:2.13, end:2.4,
   tags:["tracking","overlap","identity","screen"], note:"White jersey 2 matches track 2 at frame 32, becomes ambiguous at frame 33, then matches track 12 at frame 34.", source:"Published jersey audit, frames 32–34"},
  {id:"transition-run", clip:"broadcast-transition", title:"Running the floor in transition", start:0, end:4.8,
   tags:["transition","running","moving camera"], note:"Runners advance toward the right basket while the camera follows. The near-side runner's jersey number is blurred.", source:"Visual review of the published excerpt"},
  {id:"fast-break", clip:"broadcast-fast-break", title:"Fast break toward the basket", start:0, end:5.5,
   tags:["transition","fast break","basket","running"], note:"The possession moves quickly into the paint. Follow the runners entering and leaving the frame.", source:"Visual review of the published excerpt"},
  {id:"layup", clip:"broadcast-half-court", title:"Half-court play through the layup", start:0, end:10.8,
   tags:["half court","layup","finishing","drive"], note:"The full broadcast excerpt includes the setup and the finish. Myke identified this as his layup clip. The search indexes the play, with no automatic jersey identification.", source:"Published full clip and owner description"},
  {id:"paint-contact", clip:"baseline-camera", title:"Finishing angle near a defender", start:3, end:5.3,
   tags:["finishing","paint","defender","baseline"], note:"A dark-jersey player has a defender alongside in the paint. Rewatch the contact and finishing angle.", source:"Visual review of the published excerpt"},
  {id:"pickup", clip:"outdoor-pickup", title:"Outdoor pickup detection benchmark", start:0, end:1.8,
   tags:["outdoor","pickup","detection","benchmark","spectators"], note:"This short clip underlies the three-frame player detection check. Spectators contribute extra person detections.", source:"Published detection evaluation"}
];
export const clipNames = {
  "highlight-reel":"Highlight reel possession", "broadcast-transition":"End-to-end transition",
  "broadcast-fast-break":"Fast break", "broadcast-half-court":"Half-court set",
  "baseline-camera":"Baseline camera", "outdoor-pickup":"Outdoor pickup benchmark"
};
const aliases = new Map(Object.entries({
  shot:"shooting", shots:"shooting", shoot:"shooting", shooter:"shooting", jumpshot:"shooting",
  layups:"layup", finish:"finishing", finishes:"finishing", rim:"basket", basket:"basket",
  defenders:"defender", defensive:"defense", rotations:"rotation", switches:"switch",
  identities:"identity", ids:"identity", id:"identity", track:"tracking", tracker:"tracking",
  overlap:"overlap", overlapping:"overlap", screened:"screen", screening:"screen",
  runs:"running", run:"running", sprint:"running", sprinting:"running",
  spectators:"spectators", spectator:"spectators"
}));
const stop = new Set("a an the show me find where when with of in on to for and is are was were every all some clip clips possession possessions video videos please plays play during through his her their my at near see can you it that".split(" "));
export function terms(value) {
  return [...new Set(String(value).toLowerCase().replace(/half[- ]court/g,"half court").replace(/fast[- ]break/g,"fast break")
    .match(/[a-z0-9]+/g)?.filter(word => !stop.has(word)).map(word => aliases.get(word) ?? word) ?? [])];
}
export function searchMoments(query, entries = library, clip = "") {
  const words = terms(query);
  if (!words.length) return [];
  // An unindexed identity, tactical claim, or negation cannot be answered by loose keyword overlap.
  if (/\b(no|not|without|never|except|failed|failure|breakdown|breakdowns)\b/i.test(query)) return [];
  if (/\b(no\.?|number|jersey|#)\s*\d+|\b\d+\b/i.test(query)) {
    const number = query.match(/\d+/)?.[0];
    entries = entries.filter(entry => entry.jersey === number);
  }
  return entries.filter(entry => !clip || entry.clip === clip).map(entry => {
    const tagWords = terms(entry.tags.join(" ") + " " + entry.title);
    const allWords = terms(entry.note);
    const matched = words.filter(word => tagWords.includes(word) || allWords.includes(word));
    const coverage = matched.length / words.length;
    const score = matched.reduce((sum, word) => sum + (tagWords.includes(word) ? 3 : 1), 0);
    return {entry, matched, coverage, score};
  }).filter(result => result.coverage >= .6 && result.score > 0)
    .sort((a,b) => b.coverage - a.coverage || b.score - a.score || a.entry.id.localeCompare(b.entry.id)).slice(0,3);
}
export function validMoment(value) {
  return value && typeof value.id === "string" && value.id.length <= 100 &&
    Object.hasOwn(clipNames, value.clip) && typeof value.note === "string" &&
    value.note.trim().length >= 8 && value.note.length <= 500 &&
    typeof value.title === "string" && value.title.length <= 100 &&
    Array.isArray(value.tags) && value.tags.length <= 10 && value.tags.every(tag => typeof tag === "string" && tag.length <= 40) &&
    Number.isFinite(value.start) && Number.isFinite(value.end) && value.start >= 0 && value.end > value.start &&
    (value.jersey === undefined || /^\d{1,3}$/.test(value.jersey));
}
