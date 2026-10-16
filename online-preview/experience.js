(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CC = Object.assign(root.CC || {}, api);
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const DEFAULT_PREFS = {theme:'warm',pieces:'han',font:'normal',sound:false,sidebar:false,level:'intermediate',tone:'neutral'};
  function preferences(raw) {
    raw = raw && typeof raw === 'object' ? raw : {};
    const result = {...DEFAULT_PREFS};
    for (const [key, choices] of Object.entries({theme:['warm','cool','dark'],pieces:['han','vi'],font:['normal','large'],level:['new','beginner','intermediate'],tone:['neutral','friendly']})) {
      if (choices.includes(raw[key])) result[key]=raw[key];
    }
    result.sound=raw.sound===true;result.sidebar=raw.sidebar===true;
    return result;
  }
  const PROMPTS = [
    'Bên nào đang thuận lợi hơn? Hãy nêu một điều bạn nhìn thấy trên bàn.',
    'Quân hoặc vị trí nào cần chú ý? Có quân đang bị đe dọa hoặc đường đi bị cản không?',
    'Bạn muốn đạt điều gì với nước định đi? Đối thủ có thể đáp lại ra sao?'
  ];
  const HINTS = [
    'Nhìn lần lượt hai Tướng, số quân và vị trí các quân. Chỉ viết điều bạn quan sát được; chưa cần kết luận thắng thua.',
    'Chọn một quân để kiểm tra: nó có đang bị tấn công, có quân bảo vệ, hoặc có quân khác chặn đường không?',
    'Nêu một mục tiêu như bảo vệ Tướng, bảo vệ quân hoặc cải thiện vị trí. Sau đó thử nghĩ một phản ứng hợp lệ của đối thủ.'
  ];
  function reflectionCheck(session, puzzle) {
    const missing= [0,1,2].filter(i=>!String(session.answers?.[i]||'').trim());
    if (missing.length || !session.candidate) return {ready:false,missing,needsMove:!session.candidate};
    // This checks only the candidate, never claims to grade free-form reasoning.
    const matches=session.candidate===puzzle.solution||(puzzle.alternatives||[]).includes(session.candidate);
    const attempts=Math.min(3,Math.max(0,Math.floor(Number(session.submissionCount)||0))+1);
    return {ready:true,matches,attempts,reveal:matches||attempts>=3,assisted:session.assisted===true||attempts>1||!matches};
  }
  function safeExport(state) {
    // Exports deliberately contain no hidden solutions, generated moments or answer key snapshots.
    const list=value=>Array.isArray(value)?value:[], string=value=>typeof value==='string'?value:'';
    const answers=value=>list(value).slice(0,3).map(string);
    const status=value=>({over:value?.over===true,winner:['w','b'].includes(value?.winner)?value.winner:null,
      reason:string(value?.reason),needsVerification:value?.needsVerification===true});
    return {format:'co-chill-personal-export',version:1,exportedAt:new Date().toISOString(),
      profile:{name:string(state.profile?.name)},
      games:list(state.games).filter(Boolean).map(g=>({id:string(g.id),title:string(g.title),createdAt:Number.isFinite(g.createdAt)?g.createdAt:null,initialFen:string(g.initialFen),player:string(g.player),mode:string(g.mode),status:status(g.status),moves:list(g.moves).map(m=>string(typeof m==='string'?m:m?.move))})),
      records:Object.values(state.records||{}).filter(Boolean).map(r=>({puzzleId:string(r.puzzleId),skill:string(r.skill),dueAt:string(r.dueAt),attempts:list(r.attempts).filter(Boolean).map(a=>({startedAt:string(a.startedAt),completedAt:string(a.completedAt),answers:answers(a.answers),candidate:string(a.candidate),firstAnswers:Array.isArray(a.firstAnswers)?answers(a.firstAnswers):null,firstCandidate:string(a.firstCandidate),success:a.success===true,assisted:a.assisted===true,source:string(a.source)}))})),
      draft:state.session?{puzzleId:string(state.session.puzzleId),stage:string(state.session.stage),answers:answers(state.session.answers),candidate:string(state.session.candidate),firstAnswers:Array.isArray(state.session.firstAnswers)?answers(state.session.firstAnswers):null,firstCandidate:string(state.session.firstCandidate),summaryNote:string(state.session.summaryNote),summaryChecks:list(state.session.summaryChecks).map(string)}:null,
      summaries:list(state.summaries).filter(Boolean).map(s=>({id:string(s.id),kind:'self_report',sessionId:string(s.sessionId),at:string(s.at),checks:list(s.checks).map(string),note:string(s.note)}))};
  }
  function evidence(records,skill) {
    const attempts=Object.values(records||{}).filter(r=>!skill||r.skill===skill).flatMap(r=>r.attempts||[]);
    // First encounters only: repeated practice must not inflate unseen accuracy.
    const firsts=Object.values(records||{}).filter(r=>!skill||r.skill===skill).map(r=>(r.attempts||[])[0]).filter(Boolean);
    return {count:attempts.length,eligible:attempts.length>=6,firstCount:firsts.length,
      firstEligible:firsts.length>=6,firstCorrect:firsts.filter(a=>a.success&&!a.assisted).length,
      independent:attempts.filter(a=>a.success&&!a.assisted).length,assisted:attempts.filter(a=>a.assisted).length};
  }
  function applyClockMove(clock,side,now) {
    const next={...clock};
    if (!next.enabled) return {clock:next,expired:false};
    const remaining=Number(next[side])-Math.max(0,now-Number(next.last));
    if (remaining<=0) return {clock:{...next,[side]:0,last:now},expired:true};
    next[side]=remaining+Math.max(0,Number(next.increment)||0);next.last=now;
    return {clock:next,expired:false};
  }
  return {DEFAULT_PREFS,PROMPTS,HINTS,preferences,reflectionCheck,safeExport,evidence,applyClockMove};
});
