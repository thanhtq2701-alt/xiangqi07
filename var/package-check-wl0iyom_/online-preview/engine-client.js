/* Normalizes engine evidence; neither the UI nor an explanation may invent a line. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.CoChillEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  function validate(position, result) {
    if (!result || !Array.isArray(result.candidates)) throw new Error('Thiếu bằng chứng phân tích.');
    const legal = position.legalMoves();
    if (result.turn && result.turn !== position.turn) throw new Error('Phân tích không cùng bên đến lượt.');
    if (result.best_move != null && (!legal.includes(result.best_move) || result.candidates[0]?.move !== result.best_move)) throw new Error('Nước đề xuất không khớp bằng chứng phân tích.');
    const line = candidate => {
      if (!candidate || !legal.includes(candidate.move) || !Array.isArray(candidate.pv) || candidate.pv[0] !== candidate.move || candidate.pv.length>20) throw new Error('Engine trả chuỗi không hợp lệ.');
      let p=position;
      for (const move of candidate.pv) {if(!p.legalMoves().includes(move))throw new Error('Chuỗi phân tích không qua kiểm tra luật.');p=p.play(move);}
      if (!Number.isFinite(candidate.score) || !['cp','mate','heuristic_cp'].includes(candidate.score_type)) throw new Error('Điểm phân tích không xác định.');
      if (candidate.perspective && candidate.perspective !== position.turn) throw new Error('Điểm phân tích không cùng góc nhìn.');
      if (candidate.bound && !['exact','lowerbound','upperbound'].includes(candidate.bound)) throw new Error('Giới hạn điểm phân tích không xác định.');
      return {...candidate,pv:candidate.pv.slice()};
    };
    return {...result,candidates:result.candidates.map(line),selected:result.selected?line(result.selected):null};
  }
  function difference(best, selected) {
    // Mate distance is never subtracted from centipawns or represented as a fake numeric swing.
    if (!best||!selected||best.score_type!==selected.score_type||!['cp','heuristic_cp'].includes(best.score_type)) return null;
    // UCI lower/upper bounds are not exact evaluations. Subtracting them would
    // manufacture a precise-looking loss and could falsely label a mistake.
    if (!Number.isFinite(best.score)||!Number.isFinite(selected.score)) return null;
    if ([best,selected].some(line=>line.bound && line.bound!=='exact')) return null;
    if (best.perspective && selected.perspective && best.perspective!==selected.perspective) return null;
    return best.score-selected.score;
  }
  function local(position, selectedMove, analyze) {
    const raw=analyze(position,{depth:2,maxMs:220});
    const lines=raw.ranked.map(x=>({...x,score_type:'heuristic_cp',depth:raw.depth,perspective:position.turn,bound:'exact'}));
    return validate(position,{engine:'browser-basic',engine_name:'Máy cơ bản trên thiết bị',fallback:true,status:'fallback',confidence:'limited',best_move:raw.bestMove,
      candidates:lines.slice(0,3),selected:lines.find(x=>x.move===selectedMove)||null,search:{depth:raw.depth,exhaustive_root:false},warnings:['Tìm kiếm nông; chưa chứng minh nước tối ưu.']});
  }
  return {validate,difference,local};
});
