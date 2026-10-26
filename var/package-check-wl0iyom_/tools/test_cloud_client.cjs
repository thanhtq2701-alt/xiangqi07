/* Pure transport/state tests. No browser, server, network, passwords or real accounts. */
'use strict';
const assert = require('node:assert/strict');
const {Client} = require('../online-preview/cloud-client.js');

const tests = [];
function test(name, run) { tests.push({name, run}); }
function response(data, status = 200) {
  return {ok:status >= 200 && status < 300, status,
    headers:{get:name => name === 'content-type' ? 'application/json; charset=utf-8' : null},
    json:async () => data};
}
function deferred() {
  let resolve, reject;
  const promise = new Promise((yes,no) => {resolve=yes;reject=no;});
  return {promise,resolve,reject};
}
function logged(fetcher, notify = () => {}) {
  const client = new Client({fetcher,notify});
  client.session = {authenticated:true,user:{id:'account-A',username:'test-A'},csrf:'test-csrf-not-secret'};
  client.stateReady = true;
  client.revision = 5;
  return client;
}
const tick = () => new Promise(resolve => setImmediate(resolve));

test('serializes concurrent edits with next CAS revision and keeps newest state', async () => {
  const first = deferred(), calls = [], notices = [];
  const client = logged(async (url, options) => {
    calls.push({url,options,body:JSON.parse(options.body)});
    return calls.length === 1 ? first.promise : response({revision:7});
  }, value => notices.push(value));
  client.queue({step:1});
  const saving = client.flush();
  assert.equal(calls.length,1);
  client.queue({step:2});
  client.queue({step:3});
  assert.equal(await client.flush(),false,'parallel flush must not duplicate write');
  first.resolve(response({revision:6}));
  assert.equal(await saving,true);
  assert.deepEqual(calls.map(call=>call.body),[
    {revision:5,state:{step:1}}, {revision:6,state:{step:3}}
  ]);
  assert.equal(client.revision,7);
  assert.equal(client.lastSaved,JSON.stringify({step:3}));
  assert.equal(client.pending,null);
  assert.equal(client.sending,false);
  assert.equal(notices.at(-1),'saved');
  assert.equal(calls[0].options.credentials,'same-origin');
  assert.equal(calls[0].options.headers['X-CSRF-Token'],'test-csrf-not-secret');
});

test('queue stores a snapshot, not a mutable reference', async () => {
  let sent;
  const client = logged(async (url, options) => {sent=JSON.parse(options.body);return response({revision:6});});
  const state = {draft:{text:'original'}};
  client.queue(state);state.draft.text='changed without saving';
  await client.flush();
  assert.equal(sent.state.draft.text,'original');
});

test('does not upload until account state revision has been loaded', async () => {
  let writes=0;
  const client = logged(async (url, options) => {
    if(options.method === 'PUT'){writes++;return response({revision:10});}
    return response({revision:9,state:{server:true}});
  });
  client.stateReady=false;
  client.queue({draft:'new'});
  assert.equal(await client.flush(),false);
  assert.equal(writes,0);
  await client.readState();
  assert.equal(await client.flush(),true);
  assert.equal(writes,1);
});

test('CAS conflict preserves draft and blocks automatic overwrite', async () => {
  let calls=0;const notices=[];
  const client = logged(async () => {calls++;return response({error:'New server revision',code:'revision_conflict',revision:8},409);}, value=>notices.push(value));
  client.queue({answer:'my unsaved thought'});
  assert.equal(await client.flush(),false);
  assert.equal(client.pending,JSON.stringify({answer:'my unsaved thought'}));
  assert.ok(client.conflict);
  assert.equal(client.revision,5);
  assert.equal(await client.flush(),false);
  assert.equal(calls,1);
  assert.equal(notices.at(-1),'conflict');
});

test('explicit useDraft reads current revision before replacing server state', async () => {
  const calls=[];
  const client=logged(async (url,options)=>{
    calls.push({method:options.method,body:options.body&&JSON.parse(options.body)});
    return options.method==='GET'?response({revision:11,state:{old:true}}):response({revision:12});
  });
  client.queue({answer:'local'});client.conflict={message:'conflict'};
  assert.equal(await client.useDraft({answer:'local'}),true);
  assert.deepEqual(calls,[{method:'GET',body:undefined},{method:'PUT',body:{revision:11,state:{answer:'local'}}}]);
  assert.equal(client.conflict,null);
  assert.equal(client.revision,12);
});

test('useServer cannot discard a new edit created while remote state loads', async () => {
  const remote=deferred();
  const client=logged(async()=>remote.promise);
  client.queue({draft:'before choosing'});client.conflict={message:'conflict'};
  const choosing=client.useServer();
  client.queue({draft:'typed while loading'});
  remote.resolve(response({revision:9,state:{server:'older text'}}));
  await assert.rejects(choosing,error=>error.data?.code==='draft_changed');
  assert.equal(client.pending,JSON.stringify({draft:'typed while loading'}));
  assert.ok(client.conflict);
  assert.equal(await client.flush(),false);
});

test('useDraft cannot replace newer edits with an earlier chosen snapshot', async () => {
  const remote=deferred();let writes=0;
  const client=logged(async(url,options)=>{if(options.method==='PUT')writes++;return remote.promise;});
  client.queue({draft:'chosen version'});client.conflict={message:'conflict'};
  const choosing=client.useDraft({draft:'chosen version'});
  client.queue({draft:'newest version'});
  remote.resolve(response({revision:10,state:{server:true}}));
  await assert.rejects(choosing,error=>error.data?.code==='draft_changed');
  assert.equal(client.pending,JSON.stringify({draft:'newest version'}));
  assert.equal(writes,0);
});

test('state read from account A cannot change account B revision or data', async () => {
  const oldRead=deferred();
  const client=logged(async(url)=>url==='/api/state'?oldRead.promise:response({authenticated:true,user:{id:'account-B'},csrf:'csrf-B'}));
  const loading=client.readState();
  await client.authenticate('login',{username:'test-B',password:'fake-test-password'});
  assert.equal(client.stateReady,false);
  client.revision=17;client.lastSaved=JSON.stringify({private:'B only'});
  oldRead.resolve(response({revision:3,state:{private:'A only'}}));
  await assert.rejects(loading,error=>error.data?.code==='stale_session');
  assert.equal(client.revision,17);
  assert.equal(client.lastSaved,JSON.stringify({private:'B only'}));
  assert.equal(client.session.user.id,'account-B');
});

test('older same-account GET cannot replace a newer read result', async () => {
  const first=deferred(),second=deferred();let calls=0;
  const client=logged(async()=>++calls===1?first.promise:second.promise);
  const older=client.readState(),newer=client.readState();
  second.resolve(response({revision:20,state:{new:true}}));await newer;
  first.resolve(response({revision:19,state:{old:true}}));
  await assert.rejects(older,error=>error.data?.code==='stale_read');
  assert.equal(client.revision,20);
  assert.equal(client.lastSaved,JSON.stringify({new:true}));
});

test('read started before a successful save cannot roll back its CAS revision', async () => {
  const remote=deferred();
  const client=logged(async(url,options)=>options.method==='GET'?remote.promise:response({revision:6}));
  const reading=client.readState();
  client.queue({answer:'new saved answer'});
  await client.flush();
  remote.resolve(response({revision:5,state:{answer:'old answer'}}));
  await assert.rejects(reading,error=>error.code==='stale_read');
  assert.equal(client.revision,6);
  assert.equal(client.lastSaved,JSON.stringify({answer:'new saved answer'}));
  assert.equal(client.pending,null);
});

test('read during an active save cannot prematurely adopt its unacknowledged revision', async () => {
  const write=deferred();let reads=0;
  const client=logged(async(url,options)=>{
    if(options.method==='GET'){reads++;return response({revision:6,state:{answer:'saved'}});}
    return write.promise;
  });
  client.queue({answer:'saved'});const saving=client.flush();
  await assert.rejects(client.readState(),error=>error.code==='save_in_progress');
  assert.equal(reads,0);
  write.resolve(response({revision:6}));
  assert.equal(await saving,true);
  assert.equal(client.revision,6);assert.equal(client.conflict,null);
});

test('offline queue retries the latest draft after reconnect using the same revision', async () => {
  const calls=[];let online=false;
  const client=logged(async(url,options)=>{
    calls.push(JSON.parse(options.body));
    if(!online)throw new TypeError('offline');
    return response({revision:6});
  });
  client.queue({answer:'first draft'});await client.flush();
  client.queue({answer:'edited offline'});online=true;
  assert.equal(await client.flush(),true);
  assert.deepEqual(calls,[{revision:5,state:{answer:'first draft'}},{revision:5,state:{answer:'edited offline'}}]);
  assert.equal(client.pending,null);assert.equal(client.revision,6);
});

test('401 invalidates session and stops retries while preserving recovery draft', async () => {
  let calls=0;const notices=[];
  const client=logged(async()=>{calls++;return response({error:'Session expired',code:'session_expired'},401);},value=>notices.push(value));
  client.queue({answer:'do not lose me'});
  assert.equal(await client.flush(),false);
  assert.equal(client.session.authenticated,false);
  assert.equal(client.stateReady,false);
  assert.equal(client.pending,JSON.stringify({answer:'do not lose me'}));
  assert.equal(await client.flush(),false);
  assert.equal(calls,1);
  assert.equal(notices.at(-1),'expired');
});

test('401 loading state cannot revive an authenticated account', async () => {
  const client=logged(async()=>response({error:'Session expired'},401));
  await assert.rejects(client.readState(),error=>error.status===401);
  assert.equal(client.session.authenticated,false);
  assert.equal(client.stateReady,false);
});

test('logout invalidates inflight save and clears personal queue', async () => {
  const write=deferred();
  const client=logged(async(url)=>url==='/api/state'?write.promise:response({ok:true}));
  client.queue({private:'A'});const saving=client.flush();
  await client.logout();
  assert.equal(client.session.authenticated,false);
  assert.equal(client.pending,null);
  assert.equal(client.lastSaved,null);
  write.resolve(response({revision:6}));
  assert.equal(await saving,false);
  assert.equal(client.revision,0);
  assert.equal(client.pending,null);
  assert.equal(client.lastSaved,null);
});

test('late old save completion cannot unlock a new account save', async () => {
  const oldWrite=deferred(),newWrite=deferred();let writes=0;
  const client=logged(async(url,options)=>{
    if(url==='/api/state'&&options.method==='PUT')return ++writes===1?oldWrite.promise:newWrite.promise;
    return response({authenticated:true,user:{id:'account-B'},csrf:'csrf-B'});
  });
  client.queue({private:'A'});const oldSaving=client.flush();
  await client.authenticate('login',{username:'B',password:'fake-test-password'});
  client.stateReady=true;client.revision=0;client.queue({private:'B'});
  const newSaving=client.flush();assert.equal(writes,2);
  oldWrite.resolve(response({revision:6}));await oldSaving;
  assert.equal(client.sending,true,'old finally must not release the new sending lock');
  assert.equal(client.pending,JSON.stringify({private:'B'}));
  newWrite.resolve(response({revision:1}));assert.equal(await newSaving,true);
  assert.equal(client.lastSaved,JSON.stringify({private:'B'}));
});

test('offline write retains draft without inventing a successful save', async () => {
  const notices=[];
  const client=logged(async()=>{throw new TypeError('network unavailable');},value=>notices.push(value));
  client.queue({draft:'offline'});
  assert.equal(await client.flush(),false);
  assert.equal(client.revision,5);
  assert.equal(client.lastSaved,null);
  assert.equal(client.pending,JSON.stringify({draft:'offline'}));
  assert.equal(notices.at(-1),'offline');
});

test('already aborted request never starts fetch', async () => {
  let calls=0;const client=new Client({fetcher:async()=>{calls++;return response({ok:true});}});
  const controller=new AbortController();controller.abort();
  await assert.rejects(client.request('/api/engine/analyze',{signal:controller.signal}),error=>error.name==='AbortError');
  assert.equal(calls,0);
});

test('credentials only travel in request body, never persist in Client or browser storage', async () => {
  const descriptors={};
  for(const name of ['localStorage','sessionStorage']){
    descriptors[name]=Object.getOwnPropertyDescriptor(globalThis,name);
    Object.defineProperty(globalThis,name,{configurable:true,get(){throw new Error('Credential transport must not touch browser storage');}});
  }
  const password='TEST-ONLY-PASSWORD-NOT-REAL',totpCode='000000';let body;
  try {
    const client=new Client({fetcher:async(url,options)=>{body=JSON.parse(options.body);return response({authenticated:true,user:{id:'test-user'},csrf:'test-csrf'});}});
    await client.authenticate('login',{username:'test-user',password,totpCode});
    assert.equal(body.password,password);
    const retained=JSON.stringify(client);
    assert.ok(!retained.includes(password));assert.ok(!retained.includes(totpCode));
    assert.equal(client.pending,null);
    assert.equal(client.controllers.size,0);
  } finally {
    for(const name of ['localStorage','sessionStorage']){
      if(descriptors[name])Object.defineProperty(globalThis,name,descriptors[name]);else delete globalThis[name];
    }
  }
});

test('invalid success revision never silently marks draft saved', async () => {
  const client=logged(async()=>response({revision:50}));
  client.queue({important:true});
  assert.equal(await client.flush(),false);
  assert.equal(client.revision,5);assert.ok(client.pending);assert.ok(client.conflict);
});

test('parallel authentication is blocked before a second cookie-changing request', async () => {
  const auth=deferred();let calls=0;
  const client=new Client({fetcher:async()=>{calls++;return auth.promise;}});
  const login=client.authenticate('login',{username:'A',password:'fake-password'});
  await assert.rejects(client.authenticate('register',{username:'B',password:'fake-password'}),error=>error.data?.code==='auth_busy');
  assert.equal(calls,1);
  auth.resolve(response({authenticated:true,user:{id:'A'},csrf:'csrf-A'}));await login;
});

(async()=>{
  let failed=0;
  for(const {name,run} of tests){
    try {await run();console.log('PASS '+name);}
    catch(error){failed++;console.error('FAIL '+name+'\n'+error.stack);}
    await tick();
  }
  console.log(`${tests.length-failed}/${tests.length} cloud client tests passed`);
  if(failed)process.exitCode=1;
})();
