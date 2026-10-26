'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const Online=require('../online-preview/online-play.js'),XQ=require('../online-preview/xiangqi.js');
const tests=[],test=(name,fn)=>tests.push({name,fn});
const code='012345ABCD';
const initialRoom=(extra={})=>({code,gameId:'game1',ownerId:'guest_a',players:{w:{id:'guest_a',displayName:'A'},b:{id:'guest_b',displayName:'B'}},spectators:[],side:'w',status:'waiting',revision:0,options:{preset:'rapid',seconds:600,increment:5},ready:[],fen:XQ.START_FEN,initialFen:XQ.START_FEN,moves:[],clock:{w:600000,b:600000},serverNow:100,result:{over:false},messages:[],chatOptions:{hello:'Chào bạn!'},rematch:[],...extra});
const response=(data,status=200)=>({ok:status<400,status,headers:{get:()=> 'application/json'},json:async()=>data});
async function settle(){for(let i=0;i<80;i++)await Promise.resolve();}
function harness({hash='#online',memberRoom=null,responder=null,booting=false}={}){
  const events={},requests=[],elements=new Map(),timers=[],storage=new Map();let cloudEpoch=0,user=null,room=memberRoom;
  const session={authenticated:false,guest:true,user:{id:'guest_a',displayName:'A'},csrf:'test-csrf'};
  const element=id=>{if(!elements.has(id))elements.set(id,{innerHTML:'',textContent:''});return elements.get(id);};
  const sandbox={console,XQ,AbortController,crypto:require('node:crypto').webcrypto,Date,Math,Set,Map,
    document:{addEventListener:(kind,fn)=>(events[kind]??=[]).push(fn),getElementById:element,querySelector:()=>null},location:{hash},
    state:{games:[]},booting,boardFlipped:false,
    CCCloudUI:{snapshot:()=>({client:{epoch:cloudEpoch}}),sessionUser:()=>user},
    esc:v=>String(v??'').replace(/[<>"&]/g,c=>({'<':'&lt;','>':'&gt;','"':'&quot;','&':'&amp;'}[c])),
    heading:t=>'<h1>'+t+'</h1>',empty:(t,c,l)=>t+' '+c+' '+l,
    boardHTML:()=>'<div data-square="a3">board</div>',notationTable:()=>'<table>notation</table>',activeGame:()=>null,
    render:()=>{element('main').innerHTML='legacy';},save:()=>{sandbox.saved=(sandbox.saved||0)+1;},toast:msg=>{sandbox.toastText=msg;},
    $:element,route:()=>sandbox.location.hash.slice(1).split('/'),go:value=>{sandbox.location.hash='#'+value;sandbox.render();},
    setInterval:fn=>timers.push(fn),setTimeout:()=>1,clearTimeout(){},addEventListener(){},confirm:()=>true,
    sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},FormData:class extends Map{constructor(form){super(Object.entries(form.values));}},
    fetch:async(url,options)=>{requests.push({url,options});if(responder){const answer=await responder(url,options);if(answer)return answer;}
      if(url==='/api/rooms/session')return response(session);
      if(url==='/api/rooms')return response({rooms:[],mine:room?[{code}]:[]});
      if(url==='/api/rooms/history')return response({games:[]});
      if(url==='/api/rooms/'+code)return room?response(room):response({error:'not member'},403);
      if(url.endsWith('/join')||url.endsWith('/watch')){room=initialRoom({side:url.endsWith('/watch')?null:'w'});return response(room);}
      if(url.endsWith('/move')){const data=JSON.parse(options.body);room={...room,fen:XQ.Position.fromFen(room.fen).play(data.move).fen(),moves:[...room.moves,data.move],revision:room.revision+1};return response(room);}
      throw new Error('Unexpected request '+url);
    }};
  sandbox.window=sandbox;vm.createContext(sandbox);vm.runInContext(fs.readFileSync(require.resolve('../online-preview/online-play.js'),'utf8'),sandbox);
  return {sandbox,api:sandbox.CCOnline,requests,element,timers,storage,
    switchAccount:()=>{cloudEpoch++;user={id:'other'};sandbox.render();},
    async submit(type,values,submitter='join'){const form={dataset:{onlineForm:type},values};await events.submit[0]({target:{closest:()=>form},submitter:{value:submitter},preventDefault(){},stopImmediatePropagation(){}});await settle();},
    async click(action,value){const target={dataset:{onlineAction:action,value}};await events.click[0]({target:{closest:s=>s==='[data-online-action]'?target:null},preventDefault(){},stopImmediatePropagation(){}});await settle();},
    async square(value){const target={dataset:{square:value}};await events.click[0]({target:{closest:s=>s==='[data-square]'?target:null},preventDefault(){},stopImmediatePropagation(){}});await settle();}};
}
test('room codes reject paths, HTML and invalid lengths',()=>{assert.equal(Online.code(' abcdef1234 '),'ABCDEF1234');for(const bad of ['../rooms','<script>','123','A'.repeat(11)])assert.equal(Online.code(bad),null);});
test('clock labels convert authoritative milliseconds, including zero',()=>{assert.equal(Online.clockLabel(61000),'1:01');assert.equal(Online.clockLabel(-1),'0:00');assert.match(Online.PRESETS.blitz,/5 phút \+ 3/);});
test('finished history reconstructs legal board, turn and before/after',()=>{const g=Online.historyGame({id:'online-g1',gameId:'g1',mode:'online',serverVerified:true,player:'w',initialFen:XQ.START_FEN,moves:[{move:'a3a4',side:'w'}],status:{over:true,winner:'b',reason:'resigned'},endedAt:1790000000,opponent:'B'},XQ);assert.equal(g.moves[0].before,XQ.START_FEN);assert.equal(g.fen,XQ.Position.fromFen(XQ.START_FEN).play('a3a4').fen());assert.equal(g.clock.enabled,false);assert.equal(g.status.over,true);});
test('history refuses unverified, unfinished, wrong-turn and illegal moves',()=>{const base={id:'online-g1',gameId:'g1',mode:'online',serverVerified:true,player:'w',initialFen:XQ.START_FEN,moves:[],status:{over:true},endedAt:1790000000};for(const patch of [{serverVerified:false},{status:{over:false}},{moves:[{move:'a3a4',side:'b'}]},{moves:[{move:'a3a8',side:'w'}]}])assert.throws(()=>Online.historyGame({...base,...patch},XQ));});
test('opening an invite never silently joins a seat; watch is explicit and CSRF protected',async()=>{const app=harness({hash:'#online/'+code});await settle();assert.equal(app.requests.some(r=>r.options.method==='POST'),false);assert.match(app.element('main').innerHTML,/Vào chơi/);await app.submit('join',{code},'watch');const sent=app.requests.find(r=>r.url.endsWith('/watch'));assert.equal(sent.options.headers['X-CSRF-Token'],'test-csrf');assert.equal(sent.options.credentials,'same-origin');assert.equal(app.api.snapshot().room.side,null);});
test('live room blocks coaching routes and preserves local board orientation',async()=>{const app=harness({hash:'#online/'+code,memberRoom:initialRoom({status:'playing'})});await settle();for(const page of ['learn','line','practice','lesson','lessons','replay','moments','path','editor'])assert.equal(app.api.blocks(page),true);assert.equal(app.api.blocks('settings'),false);assert.equal(app.sandbox.boardFlipped,false);app.sandbox.location.hash='#learn';app.sandbox.render();assert.match(app.element('main').innerHTML,/trực tuyến đang diễn ra/);});
test('a move carries revision and nonce; board changes only after server response',async()=>{const app=harness({hash:'#online/'+code,memberRoom:initialRoom({status:'playing'})});await settle();await app.square('a3');await app.square('a4');const sent=app.requests.find(r=>r.url.endsWith('/move')),body=JSON.parse(sent.options.body);assert.equal(body.move,'a3a4');assert.equal(body.expectedRevision,0);assert.match(body.nonce,/^move_/);assert.equal(app.api.snapshot().room.moves[0],'a3a4');assert.equal('fen' in body,false);});
test('spectators cannot send moves',async()=>{const app=harness({hash:'#online/'+code,memberRoom:initialRoom({status:'playing',side:null})});await settle();await app.square('a3');await app.square('a4');assert.equal(app.requests.some(r=>r.url.endsWith('/move')),false);});

test('direct reload into learning restores server membership and blocks every curriculum route',async()=>{const app=harness({hash:'#lessons',memberRoom:initialRoom({status:'playing'})});await settle();assert.equal(app.api.isLive(),true);for(const page of ['course','chapter','chapter-lesson'])assert.equal(app.api.blocks(page),true);assert.match(app.element('main').innerHTML,/trực tuyến đang diễn ra/);});

test('quiet startup refresh restores an invite room after account boot finishes',async()=>{const app=harness({hash:'#online/'+code,memberRoom:initialRoom({status:'playing'}),booting:true});await settle();assert.equal(app.requests.length,0);app.sandbox.booting=false;await app.api.refresh({quiet:true});await settle();assert.equal(app.api.isLive(),true);assert.equal(app.api.snapshot().room.code,code);});
test('background polling does not erase account forms or lobby drafts',async()=>{const app=harness({hash:'#online/'+code,memberRoom:initialRoom({status:'playing'})});await settle();app.sandbox.location.hash='#account';app.element('main').innerHTML='typed account draft';await app.api.refresh({quiet:true});assert.equal(app.element('main').innerHTML,'typed account draft');app.sandbox.location.hash='#online';app.element('main').innerHTML='typed room draft';await app.api.refresh({quiet:true});assert.equal(app.element('main').innerHTML,'typed room draft');});
test('changing accounts immediately discards previous room identity and board',async()=>{const app=harness({hash:'#online/'+code,memberRoom:initialRoom({status:'playing'})});await settle();assert.ok(app.api.snapshot().room);app.switchAccount();assert.equal(app.api.snapshot().room,null);assert.equal(app.api.snapshot().session,null);assert.equal(app.api.isLive(),false);});
test('static hosting is labeled unavailable rather than pretending a server exists',async()=>{const app=harness({responder:async()=>({ok:true,status:200,headers:{get:()=> 'text/html'},json:async()=>({})})});await settle();assert.match(app.api.snapshot().problem,/chưa chạy máy chủ phòng cờ/);assert.equal(app.api.snapshot().session,null);});
(async()=>{let failed=0;for(const {name,fn} of tests){try{await fn();console.log('PASS '+name);}catch(e){failed++;console.error('FAIL '+name,e);}}console.log(`${tests.length-failed}/${tests.length} V6 online UI checks passed`);process.exitCode=failed?1:0;})();
