import {library, clipNames, searchMoments, validMoment} from "./replay-core.mjs";
const form = document.querySelector("#replay-search");
const input = form.elements.query;
const results = document.querySelector("#replay-results");
const status = document.querySelector("#replay-status");
const noteForm = document.querySelector("#moment-form");
const key = "gamelens-replay-notes-v1";
let notes = [];
let searchVersion = 0;
try {
  const saved = JSON.parse(localStorage.getItem(key) ?? "[]");
  if (!Array.isArray(saved) || !saved.every(validMoment) || saved.length > 200) throw Error();
  notes = saved;
} catch { status.textContent = "Saved notes could not load. Search the published film library below."; }
function persist() {
  try { localStorage.setItem(key, JSON.stringify(notes)); }
  catch { status.textContent = "Your notes are available in this tab. Use Download notes to keep a copy."; }
}
function seek(entry) {
  document.querySelectorAll("video").forEach(video => video.pause());
  const section = document.getElementById(entry.clip);
  for (const video of section.querySelectorAll("video")) {
    const start = () => {
      video.currentTime = Math.min(entry.start, Math.max(0, video.duration - .05));
      video.play().catch(() => { status.textContent = "Moment opened. Press play on the video to watch."; });
    };
    if (video.readyState >= 1) start();
    else { video.addEventListener("loadedmetadata", start, {once:true}); video.load(); }
  }
  section.scrollIntoView({behavior:"smooth", block:"start"});
}
async function runSearch() {
  const version=++searchVersion;
  const query=input.value;
  const entries=[...library,...notes];
  const clip=form.elements.clip.value;
  let matches;
  results.replaceChildren();
  if (document.querySelector("#meaning-search").checked) {
    status.textContent="Loading meaning search and ranking film notes. The first use downloads the model…";
    try {
      const {semanticSearch}=await import("./replay-semantic.mjs");
      matches=await semanticSearch(query,entries,clip);
    } catch {
      if(version!==searchVersion) return;
      status.textContent="Meaning search could not load. Turn it off to use the instant keyword search.";
      return;
    }
  } else matches=searchMoments(query,entries,clip);
  if(version!==searchVersion) return;
  results.replaceChildren();
  status.textContent = matches.length
    ? matches.length + " matching moments. Matches come from film notes and tags. Open the clip to confirm the play."
    : "No supported match. Try a simpler description, another clip filter, or add a timestamped note. Jersey searches need an explicitly labeled jersey.";
  for (const {entry, matched} of matches) {
    const card = document.createElement("article");
    const title = document.createElement("h3");
    title.textContent = entry.title;
    const meta = document.createElement("p");
    meta.className = "replay-meta";
    meta.textContent = clipNames[entry.clip] + " · " + entry.start.toFixed(2) + "–" + entry.end.toFixed(2) + " s";
    const note = document.createElement("p"); note.textContent = entry.note;
    const reason = document.createElement("p");
    reason.className = "replay-meta";
    const result=matches.find(row=>row.entry.id===entry.id);
    reason.textContent = (result.semantic ? "Meaning similarity "+result.similarity.toFixed(2)+" · " : "") +
      (matched.length ? "Matched words · "+matched.join(", ")+" · " : "") + (entry.source ?? "Your film note");
    const watch = document.createElement("button"); watch.type = "button"; watch.textContent = "Watch this moment ↗";
    watch.addEventListener("click", () => seek(entry));
    card.append(title, meta, note, reason, watch); results.append(card);
  }
}
form.addEventListener("submit", event => { event.preventDefault(); runSearch(); });
for (const button of document.querySelectorAll("[data-replay-query]")) {
  button.addEventListener("click", () => { input.value = button.dataset.replayQuery; form.elements.clip.value = ""; runSearch(); });
}
for (const select of document.querySelectorAll("[data-clip-options]")) {
  for (const [value,label] of Object.entries(clipNames)) select.add(new Option(label,value));
}
const savedList = document.querySelector("#saved-moments");
function renderNotes() {
  savedList.replaceChildren();
  for (const entry of notes) {
    const li = document.createElement("li"); const text = document.createElement("span");
    text.textContent = entry.title + " · " + clipNames[entry.clip] + " · " + entry.start.toFixed(2) + "s ";
    const remove = document.createElement("button"); remove.type = "button"; remove.textContent = "Delete";
    remove.setAttribute("aria-label","Delete note " + entry.title);
    remove.addEventListener("click", () => { notes = notes.filter(note => note.id !== entry.id); searchVersion++; persist(); renderNotes(); results.replaceChildren(); });
    li.append(text,remove); savedList.append(li);
  }
}
noteForm.addEventListener("submit", async event => {
  event.preventDefault();
  const data = new FormData(noteForm);
  const clip = String(data.get("clip"));
  const video = document.querySelector("#" + clip + " video");
  const message = document.querySelector("#moment-status");
  message.textContent = "Checking clip duration…";
  try {
    if (video.readyState < 1) {
      await new Promise((resolve,reject) => {
        const cleanup = () => { clearTimeout(timer); video.removeEventListener("loadedmetadata",loaded); video.removeEventListener("error",failed); };
        const loaded = () => { cleanup(); resolve(); };
        const failed = () => { cleanup(); reject(Error("Could not load clip metadata. Play the original clip first, then try again.")); };
        const timer = setTimeout(failed,10000);
        video.addEventListener("loadedmetadata",loaded); video.addEventListener("error",failed); video.load();
      });
    }
    const entry = {id:crypto.randomUUID(), clip, title:String(data.get("title")).trim(), note:String(data.get("note")).trim(),
      tags:String(data.get("tags")).split(",").map(s=>s.trim()).filter(Boolean), start:Number(data.get("start")), end:Number(data.get("end"))};
    const jersey = String(data.get("jersey")).trim(); if (jersey) entry.jersey = jersey;
    if (!validMoment(entry) || entry.end > video.duration || notes.length >= 200) throw Error("Use a valid start and end within the clip, up to 10 short tags, and a note of at least 8 characters. Limit 200 notes.");
    notes.push(entry); searchVersion++; persist(); renderNotes(); noteForm.reset();
    message.textContent = "Moment saved in this browser. You can search your note now.";
  } catch(error) { message.textContent = error.message; }
});
document.querySelector("#download-moments").addEventListener("click", () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(notes,null,2)],{type:"application/json"}));
  const a = document.createElement("a"); a.href=url; a.download="gamelens-film-notes.json"; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
});
renderNotes();
