/* Evidence normalization against real browser Xiangqi rules; no engine download. */
'use strict';
const assert = require('node:assert/strict');
const XQ = require('../online-preview/xiangqi.js');
const Engine = require('../online-preview/engine-client.js');
const tests = [];
function test(name, run) { tests.push({name, run}); }
const position = XQ.Position.fromFen(XQ.START_FEN);
const moves = position.legalMoves();
const rootMove = moves[0];
const reply = position.play(rootMove).legalMoves()[0];
function candidate(overrides = {}) {
  return {move:rootMove,pv:[rootMove,reply],score:45,score_type:'cp',perspective:'w',bound:'exact',...overrides};
}
function result(overrides = {}) { return {best_move:rootMove,candidates:[candidate()],selected:candidate(),...overrides}; }

test('valid root and opponent reply replay legally without changing the original board', () => {
  const before=position.fen();const checked=Engine.validate(position,result());
  assert.deepEqual(checked.candidates[0].pv,[rootMove,reply]);
  assert.equal(position.fen(),before);
});

test('rejects an illegal root move even if it resembles coordinate notation', () => {
  assert.throws(()=>Engine.validate(position,result({candidates:[candidate({move:'a0a9',pv:['a0a9']})]})));
});

test('replays every PV ply and rejects a second move by the same side', () => {
  assert.throws(()=>Engine.validate(position,result({candidates:[candidate({pv:[rootMove,rootMove]})]})));
});

test('rejects empty or mismatched principal variations', () => {
  assert.throws(()=>Engine.validate(position,result({candidates:[candidate({pv:[]})]})));
  assert.throws(()=>Engine.validate(position,result({candidates:[candidate({pv:[moves[1]]})]})));
});

test('selected move outside MultiPV is allowed only with its own legal line', () => {
  const selected=candidate({move:moves[1],pv:[moves[1]],score:10});
  assert.equal(Engine.validate(position,result({selected})).selected.move,moves[1]);
  assert.throws(()=>Engine.validate(position,result({selected:{...selected,pv:['a0a9']}})));
});

test('rejects non-finite and missing evaluation evidence', () => {
  for(const score of [NaN,Infinity,-Infinity,undefined,'45'])
    assert.throws(()=>Engine.validate(position,result({candidates:[candidate({score})]})));
  assert.throws(()=>Engine.validate(position,result({candidates:[candidate({score_type:'elo'})]})));
  assert.throws(()=>Engine.validate(position,{}));
});

test('centipawn comparison is a same-unit subtraction', () => {
  assert.equal(Engine.difference(candidate({score:95}),candidate({score:-20})),115);
  assert.equal(Engine.difference(candidate({score:-40}),candidate({score:-60})),20);
});

test('mate distance is never converted to a centipawn loss', () => {
  assert.equal(Engine.difference(candidate({score_type:'mate',score:3}),candidate({score:50})),null);
  assert.equal(Engine.difference(candidate({score_type:'mate',score:3}),candidate({score_type:'mate',score:8})),null);
  assert.equal(Engine.difference(candidate(),candidate({score_type:'heuristic_cp'})),null);
  assert.equal(Engine.difference(candidate(),null),null);
});

test('bounded evaluations and opposite perspectives are not exact loss evidence', () => {
  assert.equal(Engine.difference(candidate({bound:'lowerbound'}),candidate()),null);
  assert.equal(Engine.difference(candidate(),candidate({bound:'upperbound'})),null);
  assert.equal(Engine.difference(candidate({perspective:'w'}),candidate({perspective:'b'})),null);
});

test('local fallback remains labelled and its legal evidence is independently checked', () => {
  const local=Engine.local(position,moves[1],XQ.analyze);
  assert.equal(local.fallback,true);assert.equal(local.engine,'browser-basic');
  assert.equal(local.confidence,'limited');assert.equal(local.search.exhaustive_root,false);
  assert.ok(local.candidates.length>0);assert.ok(local.warnings.length>0);
  for(const line of [...local.candidates,local.selected].filter(Boolean)) {
    assert.equal(line.score_type,'heuristic_cp');
    let p=position;for(const move of line.pv)p=p.play(move);
  }
});

let failed=0;
for(const {name,run} of tests) {
  try {run();console.log('PASS '+name);}
  catch(error){failed++;console.error('FAIL '+name+'\n'+error.stack);}
}
console.log(`${tests.length-failed}/${tests.length} engine client tests passed`);
if(failed)process.exitCode=1;
