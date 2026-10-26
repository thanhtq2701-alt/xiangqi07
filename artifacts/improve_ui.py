from pathlib import Path
p=Path('web/app.js')
s=p.read_text(encoding='utf-8')
def swap(a,b):
 global s
 assert a in s,a[:90]
 s=s.replace(a,b,1)
swap('<section class="hero"><div class="hero-copy">','${continuePanel()}<section class="hero"><div class="hero-copy">')
swap("return `${intro('Nhìn lại để đi xa hơn.'", "return `${continuePanel()}${intro('Nhìn lại để đi xa hơn.'")
swap('data-square="${s}" ${interactive?', 'data-square="${s}" tabindex="${i===order[0]?0:-1}" ${interactive?')
swap('${PIECES[p]}</span>', '${pieceLabels===\'vi\'?`<span class="piece-name">${NAMES[p.toLowerCase()]}</span>`:PIECES[p]}</span>')
swap('<div class="board-tools"><button', '<div class="board-tools"><button')
swap('</button><span class="small-note">${interactive?', '</button><label class="piece-label-control">Chữ quân<select id="piece-labels"><option value="han" ${pieceLabels===\'han\'?\'selected\':\'\'}>Chữ Hán</option><option value="vi" ${pieceLabels===\'vi\'?\'selected\':\'\'}>Tiếng Việt</option></select></label><span class="small-note">${interactive?')
swap('Ví dụ a0a1 = từ a0 đến a1.', 'Ví dụ a0a1 = từ a0 đến a1. Bàn phím: phím mũi tên để di chuyển, Enter chọn, Esc hủy.')
swap('<form id="reflect-form">', '<p id="draft-status" class="draft-status" role="status" aria-live="polite"></p><button type="button" class="subtle" data-action="save-draft">Lưu nháp ngay</button><form id="reflect-form">')
swap("  $('#main').innerHTML=({home,play,practice:practicePage,exercise,dashboard,lessons,settings}[state.page])();", "  $('#main').innerHTML=({home,play,practice:practicePage,exercise,dashboard,lessons,settings}[state.page])();\n  restoreDraft();\n  const id = state.page==='exercise'?state.exercise?.id:state.page==='play'?state.game?.id:null;\n  history.replaceState(null, '', '#'+state.page+(id?'/'+id:''));")
swap("async function navigate(page) {\n  state.selected=null;", "async function navigate(page) {\n  await saveDraft();\n  state.selected=null;")
swap("  if (!button || button.disabled || !state.boot) return;", "  if (!button || button.disabled) return;\n  if (button.dataset.action==='reconnect') return task(boot, 'Đang kết nối lại…');\n  if (!state.boot || !$('#busy').hidden) return;")
swap("  if (action==='flip')", "  if (action==='save-draft') { await saveDraft(); return; }\n  if (action==='flip')")
swap("state.game=null;state.exercise=null;state.moments=[];await navigate('home')", "drafts.clear();clearTimeout(draftTimer);state.game=null;state.exercise=null;state.moments=[];await navigate('home')")
swap("if (form.id==='reflect-form') {state.exercise=await api('/api/reflect',{id:state.exercise.id,...data});render();}", "if (form.id==='reflect-form') {clearTimeout(draftTimer);state.exercise=await api('/api/reflect',{id:state.exercise.id,...data});drafts.delete(state.exercise.id);render();}")
swap("task(async()=>{state.boot=await api('/api/bootstrap');render();},'Đang mở góc học tập…');", "task(boot,'Đang mở góc học tập…');")
p.write_text(s,encoding='utf-8')
