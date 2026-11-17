import {env,pipeline} from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1";
import {searchMoments,terms} from "./replay-core.mjs";
env.allowLocalModels=false;
env.backends.onnx.wasm.numThreads=1;
let model;
const vectors=new Map();
let queue=Promise.resolve();
async function retrieve(query,entries,clip) {
  // Explicit jersey questions and negated/tactical failure claims require exact annotation evidence.
  if (/\d|\b(no|not|without|never|except|failed|failure|breakdown|breakdowns)\b/i.test(query)) return searchMoments(query,entries,clip);
  if (!terms(query).length) return [];
  if (!model) model=await pipeline("feature-extraction","Xenova/all-MiniLM-L6-v2",{dtype:"q8",device:"wasm"});
  const pool={pooling:"mean",normalize:true};
  const missing=entries.filter(entry=>!vectors.has(JSON.stringify(entry)));
  if (missing.length) {
    const values=(await model(missing.map(entry=>entry.title+". "+entry.tags.join(", ")+". "+entry.note),pool)).tolist();
    missing.forEach((entry,i)=>vectors.set(JSON.stringify(entry),values[i]));
    if (vectors.size>250) {
      const current=new Set(entries.map(entry=>JSON.stringify(entry)));
      for(const key of vectors.keys()) if(!current.has(key)) vectors.delete(key);
    }
  }
  const [queryVector]=(await model(query,pool)).tolist();
  const keyword=searchMoments(query,entries,clip);
  return entries.filter(entry=>!clip || entry.clip===clip).map(entry=>{
    const vector=vectors.get(JSON.stringify(entry));
    const similarity=vector.reduce((sum,value,i)=>sum+value*queryVector[i],0);
    const exact=keyword.find(row=>row.entry.id===entry.id);
    return {entry,similarity,score:similarity+(exact?.coverage??0)*.12,matched:exact?.matched??[],semantic:true};
  }).filter(row=>row.similarity>=.42)
    .sort((a,b)=>b.score-a.score || a.entry.id.localeCompare(b.entry.id)).slice(0,3);
}
export function semanticSearch(query,entries,clip="") {
  const task=queue.then(()=>retrieve(query,entries,clip));
  queue=task.catch(()=>{});
  return task;
}
