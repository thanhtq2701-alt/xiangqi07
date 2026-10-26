const fs=require('node:fs'),XQ=require('../online-preview/xiangqi.js');
function position(pieces,turn='w'){const b=Array(90).fill('.');for(const [sq,p] of Object.entries(pieces))b[XQ.index(sq)]=p;try{return XQ.Position.fromFen(new XQ.Position(b,turn).fen());}catch{return null;}}
function solver(root,checksOnly=false){const memo=new Map();let nodes=0;function win(p,d){nodes++;const key=p.fen()+'|'+d;if(memo.has(key))return memo.get(key);const ms=p.legalMoves();if(!ms.length)return p.turn==='b'&&p.inCheck();if(d===0)return false;let result;if(p.turn==='w'){result=false;for(const m of ms){const c=p.afterUnchecked(m);if(checksOnly&&!c.inCheck())continue;if(win(c,d-1)){result=true;break;}}}else{result=ms.every(m=>win(p.afterUnchecked(m),d-1));}memo.set(key,result);return result;}return {win,nodes:()=>nodes};}
let seed=928471;const rand=n=>{seed=(seed*1664525+1013904223)>>>0;return seed%n;};const out=[];
const debug=position({e9:'k',e0:'K',e4:'P',a8:'R',g7:'H'});const qs=solver(debug,true);console.log('debug',debug.fen(),qs.win(debug,1),qs.win(debug,5),qs.nodes());
for(let n=150;n<900&&out.length<3;n++){
 const sqs=[];while(sqs.length<2){const sq=XQ.square(rand(63));if(!['e9','e4'].includes(sq)&&!sqs.includes(sq))sqs.push(sq);}
 const pieces={e9:'k',d0:'K',d9:'a',f9:'a',[sqs[0]]:'R',[sqs[1]]:'R'}; const p=position(pieces);if(!p)continue;
 const quick=solver(p,true);if(!quick.win(p,7))continue;
 const full=solver(p,true);
 const accepted=p.legalMoves().filter(m=>p.afterUnchecked(m).inCheck()&&full.win(p.afterUnchecked(m),6)&&!full.win(p.afterUnchecked(m),2));if(!accepted.length)continue;
 let pos=p,line=[];for(let d=7;d>0;d--){const moves=pos.legalMoves();if(!moves.length)break;const valid=moves.filter(m=>(pos.turn==='b'||pos.afterUnchecked(m).inCheck())&&full.win(pos.afterUnchecked(m),d-1));valid.sort((a,b)=>{let da=0,db=0;for(let r=0;r<d;r++){if(full.win(pos.afterUnchecked(a),r)){da=r;break;}}for(let r=0;r<d;r++){if(full.win(pos.afterUnchecked(b),r)){db=r;break;}}return db-da;});const m=valid[0];if(!m)break;line.push(m);pos=pos.afterUnchecked(m);}
 out.push({fen:p.fen(),pieces,accepted,line,nodes:full.nodes()});console.log(JSON.stringify(out.at(-1)));
}
fs.writeFileSync('var/v6_found_lines.json',JSON.stringify(out,null,2));
