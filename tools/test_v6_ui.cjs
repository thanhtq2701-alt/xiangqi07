'use strict';
// Contract and lifecycle tests. Real browser typography/layout is checked separately.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const UI=require('../online-preview/v6-ui.js');
const Cloud=require('../online-preview/cloud-client.js');
const XQ=require('../online-preview/xiangqi.js');
const CC={...require('../online-preview/learning.js'),...require('../online-preview/experience.js'),...require('../online-preview/game-tools.js')};
const tests=[];const test=(name,fn)=>tests.push({name,fn});
const response=data=>({ok:true,status:200,headers:{get:()=> 'application/json'},json:async()=>data});
const account=id=>({authenticated:true,user:{id,username:'user_'+id,displayName:'Player '+id,role:'user'},csrf:'test-csrf'});
async function settle(){for(let i=0;i<40;i++)await Promise.resolve();}
function harness({session={authenticated:false},available=true,initialHash='#home',initialStorage={}}={}){
  const listeners={},elements=new Map(),storage=new Map(Object.entries(initialStorage)),writes=[];
  function element(id){if(!elements.has(id))elements.set(id,{innerHTML:'',textContent:'',hidden:false,dataset:{},classList:{toggle(){}},setAttribute(){},focus(){}});return elements.get(id);}
  const fetcher=async(url,options={})=>{
    if(url==='/api/session')return available?response(session):{ok:false,status:404,headers:{get:()=> 'text/html'},text:async()=>'<html></html>'};
    if(url==='/api/content')return response({puzzles:[]});
    if(url==='/api/state'&&options.method==='GET')return response({revision:0,state:CC.fresh()});
    if(url==='/api/state'&&options.method==='PUT')return response({revision:1});
    throw new Error('Unexpected test request '+url);
  };
  const document={getElementById:element,documentElement:{dataset:{},lang:'vi'},body:{classList:{toggle(){}}},querySelector:()=>null,querySelectorAll:()=>[],addEventListener:(kind,fn)=>(listeners[kind]??=[]).push(fn),hidden:false};
  const sandbox={CC,XQ,FIXTURES:[],document,location:{hash:initialHash},console,Date,AbortController,
    CoChillCloud:{...Cloud,Client:class extends Cloud.Client{constructor(options){super({...options,fetcher});}}},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>{writes.push({key,value});storage.set(key,value);},removeItem:key=>storage.delete(key)},
    setInterval(){},setTimeout(){return 1;},clearTimeout(){},confirm:()=>true,
    FormData:class extends Map{constructor(form){super(form.data||[]);}getAll(key){const v=this.get(key);return v===undefined?[]:[v];}},
    addEventListener(){},scrollTo(){}};
  sandbox.window=sandbox;vm.createContext(sandbox);
  for(const name of ['app.js','v5-ui.js','v6-ui.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../online-preview',name),'utf8'),sandbox,{filename:name});
  return {run:s=>vm.runInContext(s,sandbox),api:sandbox.CCV6UI,storage,writes,element,document,client:()=>sandbox.CCCloudUI.snapshot().client,
    async dispatch(kind,event){for(const listener of listeners[kind]||[])await listener(event);}};
}

test('entry is a presentation choice and never masks real account/help/privacy routes',()=>{
  assert.equal(UI.shouldShowEntry({}),true);
  for(const page of ['account','help','privacy'])assert.equal(UI.shouldShowEntry({page}),false);
  assert.equal(UI.shouldShowEntry({booting:true}),false);
  assert.equal(UI.shouldShowEntry({user:{id:'A'}}),false);
  assert.equal(UI.shouldShowEntry({guest:true,page:'learn'}),false);
});
test('language keys isolate guest and account identities',()=>{
  assert.notEqual(UI.languageKey(null),UI.languageKey({id:'A'}));
  assert.notEqual(UI.languageKey({id:'A'}),UI.languageKey({id:'B'}));
  assert.equal(UI.languageKey({id:'a/b'}).endsWith('account:a%2Fb'),true);
});
test('only declared shell strings translate, lesson prose remains unchanged',()=>{
  assert.equal(UI.t('Trang chủ','en'),'Home');
  assert.equal(UI.t('  Đăng nhập  ','en'),'  Sign in  ');
  assert.equal(UI.t('3 hình cờ đã đến lúc ôn','en'),'3 positions are ready for review');
  assert.equal(UI.t('Kiểm tra chân Mã trước khi chọn đường tiến.','en'),'Kiểm tra chân Mã trước khi chọn đường tiến.');
  assert.equal(UI.t('Trang chủ','vi'),'Trang chủ');
});
test('preview entry disables account creation when no service exists',()=>{
  const unavailable=UI.entryHTML(false),available=UI.entryHTML(true);
  assert.match(unavailable,/<button[^>]+disabled>Đăng nhập hoặc tạo tài khoản/);
  assert.doesNotMatch(unavailable,/<a href="#account"/);
  assert.match(unavailable,/data-v6-action="guest"/);
  assert.match(available,/<a href="#account"/);
  assert.doesNotMatch(available,/Google|OAuth/);
});
test('all three theme controls submit normal preference values',()=>{
  const html=UI.themePicker('cool');
  for(const theme of ['warm','cool','dark'])assert.match(html,new RegExp('name="theme" value="'+theme+'"'));
  assert.match(html,/value="cool" checked/);
  assert.equal((html.match(/ checked/g)||[]).length,1);
});
test('first visit gates home, guest choice persists without creating an account',async()=>{
  const app=harness({available:false});await settle();
  assert.match(app.element('main').innerHTML,/v6-entry/);
  const button={dataset:{v6Action:'guest'},closest(){return this;}};
  await app.dispatch('click',{target:{closest:selector=>selector==='[data-v6-action]'?button:null},preventDefault(){}});
  assert.equal(app.storage.get(UI.ENTRY_KEY),'guest');
  assert.match(app.element('main').innerHTML,/v6-home/);
  assert.equal(app.client().session.authenticated,false);
});
test('saved guest choice keeps the home cover and four actions on reload',async()=>{
  const app=harness({initialStorage:{[UI.ENTRY_KEY]:'guest'}});await settle();
  const html=app.element('main').innerHTML;
  assert.match(html,/v6-cover/);
  assert.doesNotMatch(html,/class="home-intro"/);
  for(const href of ['#play','#lessons','#mistakes','#review'])assert.ok(html.includes('href="'+href+'"'));
});
test('language changes preserve live learning state and do not call save or send passwords',async()=>{
  const app=harness({session:account('A'),initialHash:'#account'});await settle();
  app.run("state.session={puzzleId:'test-draft',stage:'reflect',answers:['Private answer','',''],candidate:'a0a1'};selected='a0';");
  const before=app.run('JSON.stringify(state.session)'),count=app.writes.length;
  assert.equal(app.api.setLanguage('en'),true);
  assert.equal(app.run('JSON.stringify(state.session)'),before);
  assert.equal(app.run('selected'),'a0');
  assert.equal(app.document.documentElement.lang,'en');
  const writes=app.writes.slice(count);
  assert.equal(writes.length,1);assert.equal(writes[0].key,UI.languageKey({id:'A'}));assert.equal(writes[0].value,'en');
  assert.equal(app.api.setLanguage('injected'),false);
});
test('one account does not inherit another account language',async()=>{
  const app=harness({session:account('A'),initialHash:'#account'});await settle();app.api.setLanguage('en');
  app.client().session=account('B');app.api.refresh();
  assert.equal(app.api.language(),'vi');
  app.client().session=account('A');app.api.refresh();
  assert.equal(app.api.language(),'en');
  app.client().session={authenticated:false};app.api.refresh();
  assert.equal(app.api.language(),'vi');
});
test('theme preview preserves settings values and queues account sync',async()=>{
  const app=harness({session:account('A'),initialHash:'#settings'});await settle();
  assert.match(app.element('main').innerHTML,/v6-theme-picker/);
  const form={data:[['theme','dark'],['pieces','vi'],['font','large'],['level','beginner'],['tone','friendly'],['sound','on']]};
  const target={name:'theme',closest:selector=>selector==='#settings-form'||selector==='form'?form:null};
  await app.dispatch('change',{target});
  assert.equal(app.run('prefs.theme'),'dark');assert.equal(app.run('prefs.pieces'),'vi');assert.equal(app.run('prefs.font'),'large');
  assert.equal(JSON.parse(app.client().pending).preferences.theme,'dark');
});

(async()=>{let passed=0;for(const {name,fn} of tests){try{await fn();passed++;console.log('PASS '+name);}catch(error){console.error('FAIL '+name);throw error;}}console.log(`${passed}/${tests.length} V6 UI checks passed.`);})().catch(error=>{console.error(error);process.exitCode=1;});
