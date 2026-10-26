'use strict';
// Runs the real app + account screen handlers with a minimal DOM and controlled
// HTTP responses. Browser layout checks are separate from these race regressions.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const Cloud = require('../online-preview/cloud-client.js');
const XQ = require('../online-preview/xiangqi.js');
const CC = {...require('../online-preview/learning.js'), ...require('../online-preview/experience.js'), ...require('../online-preview/game-tools.js')};
const tests=[]; const test=(name,fn)=>tests.push({name,fn});
const response=data=>({ok:true,status:200,headers:{get:()=> 'application/json'},json:async()=>data});
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
async function settle(){for(let i=0;i<30;i++)await Promise.resolve();}

function harness({guest=CC.fresh(),session={authenticated:false},remote=CC.fresh(),stateRead=null,initialHash='#account',initialStorage={}}={}){
  const listeners={},elements=new Map(),storage=new Map(),writes=[],intervals=[];
  storage.set('co-chill-v4-browser',JSON.stringify(guest));
  for(const [key,value] of Object.entries(initialStorage))storage.set(key,JSON.stringify(value));
  function element(id){if(!elements.has(id))elements.set(id,{innerHTML:'',textContent:'',hidden:false,dataset:{},classList:{toggle(){}},setAttribute(){},focus(){}});return elements.get(id);}
  let revision=0;
  const fetcher=async(url,options={})=>{
    if(url==='/api/session')return response(session);
    if(url==='/api/content')return response({puzzles:[]});
    if(url==='/api/state'&&options.method==='GET')return stateRead?stateRead.promise:response({revision,state:remote});
    if(url==='/api/state'&&options.method==='PUT'){remote=JSON.parse(options.body).state;return response({revision:++revision});}
    throw new Error('Unexpected test request '+url+' '+options.method);
  };
  const document={getElementById:element,documentElement:{dataset:{}},body:{classList:{toggle(){}}},querySelector:()=>null,querySelectorAll:()=>[],addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),hidden:false};
  const sandbox={CC,XQ,FIXTURES:[],document,location:{hash:initialHash},console,Date,AbortController,
    CoChillCloud:{...Cloud,Client:class extends Cloud.Client{constructor(options){super({...options,fetcher});}}},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>{writes.push({key,value});storage.set(key,value);},removeItem:key=>storage.delete(key)},
    setInterval(callback,delay){intervals.push({callback,delay});},setTimeout(){return 1;},clearTimeout(){},confirm:()=>true,
    FormData:class extends Map{constructor(form){super(form.data||[]);}getAll(key){const value=this.get(key);return value===undefined?[]:[value];}},
    addEventListener(){},scrollTo(){}};
  sandbox.window=sandbox;vm.createContext(sandbox);
  for(const file of ['app.js','v5-ui.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../online-preview',file),'utf8'),sandbox,{filename:file});
  return {run:source=>vm.runInContext(source,sandbox),storage,writes,element,client:()=>sandbox.CCCloudUI.snapshot().client,tick:()=>intervals.filter(i=>i.delay===300).forEach(i=>i.callback()),
    async dispatch(kind,event){for(const listener of listeners[kind]||[])await listener(event);}};
}

test('session expiry renders the account page without recursive expiry transitions',async()=>{
  const app=harness();await settle();
  assert.doesNotThrow(()=>app.client().expire());
  assert.equal(app.run('location.hash'),'#account');
  assert.match(app.element('main').innerHTML,/Tài khoản Cờ Chill/);
  assert.equal(app.run('KEY'),'co-chill-v4-browser');
  assert.equal(app.client().session.authenticated,false);
  for(let i=0;i<3;i++)assert.doesNotThrow(()=>app.run('render()'));
});

test('pending account activation never writes guest state into the account cache',async()=>{
  const guest=CC.fresh();guest.profile.name='Private guest marker';
  guest.games=[{id:'guest-live',mode:'local',player:'w',initialFen:XQ.START_FEN,fen:XQ.START_FEN,moves:[],status:{over:false},clock:{enabled:true,w:1,b:1000,last:Date.now()-10000,increment:0}}];
  const hold=deferred(),session={authenticated:true,user:{id:'B',username:'account_b',displayName:'Account B',role:'user'},csrf:'test-csrf'};
  const app=harness({guest,session,stateRead:hold});await settle();
  assert.equal(app.run('booting'),true);
  assert.equal(app.run('KEY'),'co-chill-v4-browser');
  app.run('save();');app.tick();
  assert.equal(app.storage.has('co-chill-account-B'),false);
  assert.equal(app.run('state.games[0].status.over'),false);
  const server=CC.fresh();server.profile.name='Account B';
  hold.resolve(response({revision:3,state:server}));await settle();
  assert.equal(app.run('booting'),false);
  assert.equal(app.run('KEY'),'co-chill-account-B');
  const saved=app.storage.get('co-chill-account-B');
  assert.ok(saved);assert.equal(saved.includes('Private guest marker'),false);assert.equal(saved.includes('guest-live'),false);
  assert.equal(app.run('state.profile.name'),'Account B');
});

test('saving account settings immediately queues preferences for synchronization',async()=>{
  const session={authenticated:true,user:{id:'A',username:'account_a',displayName:'Account A',role:'user'},csrf:'test-csrf'};
  const app=harness({session});await settle();
  await app.dispatch('submit',{target:{id:'settings-form',dataset:{},data:[['theme','dark'],['pieces','vi'],['font','large'],['level','beginner'],['tone','friendly'],['sound','on']]},preventDefault(){}});
  const pending=app.client().pending;
  assert.ok(pending,'Settings save must queue cloud data without waiting for an unrelated game or learning action.');
  const data=JSON.parse(pending);assert.equal(data.preferences.theme,'dark');assert.equal(data.preferences.font,'large');assert.equal(data.preferences.pieces,'vi');
  assert.equal(JSON.parse(app.storage.get('co-chill-account-A')).preferences.theme,'dark');
});

test('an account read completed after expiry cannot revive the session or write its cache',async()=>{
  const hold=deferred(),session={authenticated:true,user:{id:'A',username:'account_a',displayName:'Account A',role:'user'},csrf:'test-csrf'};
  const app=harness({session,stateRead:hold});await settle();
  app.client().expire();
  const oldAccount=CC.fresh();oldAccount.profile.name='Expired private marker';
  hold.resolve(response({revision:4,state:oldAccount}));await settle();
  assert.equal(app.client().session.authenticated,false);
  assert.equal(app.run('KEY'),'co-chill-v4-browser');
  assert.equal(app.storage.has('co-chill-account-A'),false);
  assert.notEqual(app.run('state.profile.name'),'Expired private marker');
  assert.equal(app.run('booting'),false);
});

test('offline account activation restores its own cached preferences',async()=>{
  const hold=deferred(),session={authenticated:true,user:{id:'A',username:'account_a',displayName:'Account A',role:'user'},csrf:'test-csrf'};
  const cached={...CC.fresh(),preferences:{theme:'dark',font:'large',pieces:'vi'}};
  const app=harness({session,stateRead:hold,initialStorage:{'co-chill-account-A':cached}});await settle();
  hold.reject(new Error('Test connection unavailable'));await settle();
  assert.equal(app.run('KEY'),'co-chill-account-A');
  assert.equal(app.run('prefs.theme'),'dark');
  assert.equal(app.run('prefs.font'),'large');
  assert.equal(app.client().stateReady,false);
});

test('choosing the server copy restores and caches server preferences together with progress',async()=>{
  const session={authenticated:true,user:{id:'A',username:'account_a',displayName:'Account A',role:'user'},csrf:'test-csrf'};
  const server={...CC.fresh(),preferences:{theme:'dark',font:'large',pieces:'vi'}};
  const app=harness({session,remote:server});await settle();
  app.run("prefs=CC.preferences({theme:'warm',font:'normal',pieces:'han'});");
  const target={dataset:{action:'cloud-use-server'},disabled:false};
  await app.dispatch('click',{target:{closest:selector=>selector==='[data-action]'?target:null}});
  assert.equal(app.run('prefs.theme'),'dark');
  assert.equal(app.run('prefs.font'),'large');
  assert.equal(JSON.parse(app.storage.get('co-chill-account-A')).preferences.theme,'dark');
});

test('an account without saved preferences starts with defaults rather than another profile theme',async()=>{
  const session={authenticated:true,user:{id:'B',username:'account_b',displayName:'Account B',role:'user'},csrf:'test-csrf'};
  const app=harness({session,initialStorage:{'co-chill-preferences-v1':{theme:'dark',font:'large',pieces:'vi'}}});await settle();
  assert.equal(app.run('prefs.theme'),CC.DEFAULT_PREFS.theme);
  assert.equal(app.run('prefs.font'),CC.DEFAULT_PREFS.font);
  assert.equal(app.run('prefs.pieces'),CC.DEFAULT_PREFS.pieces);
});

function publishedPuzzle(version=1){return {id:'custom-test',version,status:'published',title:'Owner-reviewed test',skill:'cannon',fen:XQ.START_FEN,solution:'h2e2',alternatives:[],what:'VERSIONED_ANSWER_SECRET',why:'SOURCE_REASON_SECRET',how:'NEXT_STEP_SECRET',source:'Original synthetic test'};}

test('guest transfer recognizes V6-only drafts and refuses overwriting V6 account progress',async()=>{
  const C=require('../online-preview/curriculum.js'),L=require('../online-preview/line-practice.js');
  const guest=CC.fresh();guest.lineSession=L.create(C.exercises[0]);
  const session={authenticated:true,user:{id:'A',username:'account_a',displayName:'Account A',role:'user'},csrf:'test-csrf'};
  const target={dataset:{action:'cloud-import-guest'},disabled:false};
  const event={target:{closest:selector=>selector==='[data-action]'?target:null}};
  const empty=harness({guest,session});await settle();await empty.dispatch('click',event);
  assert.equal(empty.run('state.lineSession.exerciseId'),C.exercises[0].id);
  const remote=CC.fresh();remote.lineSession=L.create(C.exercises[1]);
  const occupied=harness({guest,session,remote});await settle();await occupied.dispatch('click',event);
  assert.equal(occupied.run('state.lineSession.exerciseId'),C.exercises[1].id);
  assert.match(occupied.element('toast').textContent,/đã có tiến độ/);
});

test('custom lesson version survives saved draft migration',()=>{
  const puzzle=publishedPuzzle(7),state=CC.fresh();state.session=CC.createSession(puzzle);
  state.session.answers=['Private answer 1','Private answer 2','Private answer 3'];
  const roundtrip=CC.sanitize(JSON.parse(JSON.stringify(state)));
  assert.equal(roundtrip.session.puzzle.version,7);
  assert.deepEqual(roundtrip.session.answers,state.session.answers);
});

test('a changed custom lesson pauses the old draft without revealing or completing it',async()=>{
  const app=harness();await settle();
  app.run(`state.session=CC.createSession(${JSON.stringify(publishedPuzzle(1))});state.session.answers=['Old draft 1','Old draft 2','Old draft 3'];publishedPuzzles=[${JSON.stringify(publishedPuzzle(2))}];publishedLoaded=true;location.hash='#learn';render();`);
  const html=app.element('main').innerHTML;
  assert.match(html,/Bài có nội dung mới/);
  assert.doesNotMatch(html,/VERSIONED_ANSWER_SECRET|reflection-form|data-action="finish"/);
  assert.equal(app.run('state.session.puzzle.version'),1);
  assert.equal(app.run('state.session.answers[0]'),'Old draft 1');
  assert.equal(app.run('Object.keys(state.records).length'),0);
});

test('a withdrawn custom lesson keeps its draft but removes grading controls',async()=>{
  const app=harness();await settle();
  app.run(`state.session=CC.createSession(${JSON.stringify(publishedPuzzle())});publishedPuzzles=[];publishedLoaded=true;location.hash='#learn';render();`);
  assert.match(app.element('main').innerHTML,/Bài đang được kiểm tra lại/);
  assert.doesNotMatch(app.element('main').innerHTML,/VERSIONED_ANSWER_SECRET|reflection-form|data-action="finish"/);
  assert.equal(app.run('state.session.puzzleId'),'custom-test');
  assert.equal(app.run('state.session.stage'),'reflect');
});

(async()=>{let failed=0;for(const {name,fn} of tests){try{await fn();console.log('PASS '+name);}catch(error){failed++;console.error('FAIL '+name+'\n'+error.stack);}}console.log(`${tests.length-failed}/${tests.length} V5 UI regression tests passed`);process.exitCode=failed?1:0;})();
