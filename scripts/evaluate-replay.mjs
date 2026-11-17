import {readFile,writeFile} from "node:fs/promises";
import {searchMoments,library} from "../demo/replay-core.mjs";
const queries=JSON.parse(await readFile(new URL("../demo/replay-queries.json",import.meta.url)));
const results=queries.map(({query,relevant})=>{
  const returned=searchMoments(query).map(row=>row.entry.id);
  return {query,relevant,returned,pass:relevant.length ? returned.some(id=>relevant.includes(id)) : returned.length===0};
});
const positive=results.filter(row=>row.relevant.length);
const negative=results.filter(row=>!row.relevant.length);
const output={
  method:"Fixed diagnostic queries written alongside the seven-annotation index. Development check, not an independent or held-out benchmark.",
  indexedMoments:library.length,queryCount:results.length,
  hitAt3:{correct:positive.filter(row=>row.pass).length,total:positive.length},
  noMatch:{correct:negative.filter(row=>row.pass).length,total:negative.length},
  results
};
await writeFile(new URL("../demo/replay-evaluation.json",import.meta.url),JSON.stringify(output,null,2)+"\n");
console.log(JSON.stringify({hitAt3:output.hitAt3,noMatch:output.noMatch}));
if (results.some(row=>!row.pass)) process.exitCode=1;
