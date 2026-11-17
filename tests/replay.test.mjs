import test from "node:test";
import assert from "node:assert/strict";
import {searchMoments,validMoment,terms,library} from "../demo/replay-core.mjs";
test("retrieves synonyms, filters by clip, and links audited identity evidence",()=>{
  assert.equal(searchMoments("Show me a layup")[0].entry.clip,"broadcast-half-court");
  assert.equal(searchMoments("tracking identity overlap")[0].entry.id,"identity-overlap");
  assert.equal(searchMoments("shots")[0].entry.clip,"highlight-reel");
  assert.equal(searchMoments("fast break",library,"baseline-camera").length,0);
});
test("unsupported events, identities and negation abstain",()=>{
  for (const query of ["No. 3 attacking the basket","show failed rotations","three point buzzer beater","without a defender","pottery","show me every play"]) {
    assert.equal(searchMoments(query).length,0,query);
  }
});
test("only explicitly labeled notes can match jersey searches",()=>{
  const note={id:"personal",clip:"broadcast-half-court",title:"Jersey 3 layup",jersey:"3",note:"Confirmed jersey 3 completes the layup",tags:["layup"],start:1,end:4};
  assert.ok(validMoment(note));
  assert.equal(searchMoments("jersey 3 layup",[...library,note])[0].entry.id,"personal");
  assert.equal(searchMoments("jersey 12 layup",[...library,note]).length,0);
  assert.equal(validMoment({...note,end:0}),false);
  assert.equal(validMoment({...note,clip:"../../"}),false);
  assert.deepEqual(terms("half-court shots"),["half","court","shooting"]);
});
