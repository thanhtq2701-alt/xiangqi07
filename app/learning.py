"""Transparent recommendation, explanation and scheduling policies."""
from datetime import datetime, timedelta, timezone
from typing import Protocol
from app.rules import Position, describe, parse_move

SKILLS = {
    'material': 'Quan sát quân không được bảo vệ',
    'cannon': 'Tính đường Pháo và quân ngòi',
    'horse': 'Tính đường Mã và chân Mã',
    'safety': 'An toàn của Tướng',
}
LESSONS = {
    'material': 'Trước khi lập kế hoạch, đếm quân đang bị tấn công của cả hai bên. Với mỗi nước ăn quân, kiểm tra đối phương có ăn lại được không.',
    'cannon': 'Pháo đi như Xe khi không ăn. Khi ăn quân, giữa Pháo và mục tiêu phải có đúng một quân ngòi. Đếm lại ngòi sau mỗi nước đi.',
    'horse': 'Mã đi một bước thẳng rồi một bước chéo. Ô đầu tiên là chân Mã: nếu bị chặn, nước đi đó không hợp lệ. Kiểm tra cả đường vào và đường lui.',
    'safety': 'Khi bị chiếu, ưu tiên thoát chiếu: di chuyển Tướng, bắt quân chiếu, hoặc che đường chiếu nếu có thể. Không được để hai Tướng nhìn thẳng nhau.',
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def diagnose(pos, played, loss):
    if pos.in_check():
        skill = 'safety'
    else:
        piece = pos.board[parse_move(played)[0]].lower()
        skill = {'c': 'cannon', 'h': 'horse'}.get(piece, 'material')
    return {'skill': skill, 'severity': 'major' if loss >= 400 else 'moderate' if loss >= 100 else 'explore', 'tentative': True}


def schedule(previous, correct, assisted, unseen, now=None):
    """No automated reasoning grade or scientifically validated mastery claim."""
    now = now or datetime.now(timezone.utc)
    previous = previous or {}
    evidence = previous.get('evidence_count', 0) + 1
    transfers = previous.get('transfer_success_count', 0) + int(correct and unseen and not assisted)
    if not correct:
        days, delta = 1, -6
    elif assisted:
        days, delta = 2, 0
    elif unseen:
        days, delta = (30 if transfers >= 2 else 14), 5
    else:
        days, delta = 7, 3
    return dict(mastery_score=max(0, min(100, previous.get('mastery_score', 50) + delta)),
                evidence_count=evidence, transfer_success_count=transfers,
                lapse_count=previous.get('lapse_count', 0) + int(not correct),
                stability=days, last_review_at=now.isoformat(),
                next_review_at=(now + timedelta(days=days)).isoformat())


def recommend(puzzles, skill, exposures, exclude_family=None):
    """Same skill first; prefer a genuinely different unseen family."""
    seen_ids = {x['puzzle_id'] for x in exposures if x.get('puzzle_id')}
    seen_families = {x['family'] for x in exposures if x.get('family')}
    if exclude_family:
        seen_families.add(exclude_family)
    candidates = [p for p in puzzles if p['skill'] == skill] or list(puzzles)
    candidates.sort(key=lambda p: (p['family'] in seen_families, p['id'] in seen_ids, p['family'] == exclude_family, p['id']))
    p = candidates[0]
    return p, p['family'] not in seen_families


class ExplanationProvider(Protocol):
    def explain(self, facts: dict, reflection: dict) -> dict: ...


class TemplateProvider:
    def explain(self, facts, reflection):
        pos = Position.from_fen(facts['fen'])
        best = facts['analysis']['lines'][0]
        played = facts.get('played')
        actual = next((x for x in facts['analysis']['lines'] if x['move'] == played), None)
        loss = best['score'] - actual['score'] if actual else 0
        # Describe the exact legal sequence, not a generic tactical claim.
        state, sequence = pos, []
        for move in best['pv']:
            sequence.append(describe(state, move))
            state = state.play(move)
        return {
            'provider': 'template-v1', 'fallback': True,
            'what': (f'Bạn đã đi {describe(pos, played)}. Trong tìm kiếm cục bộ sâu {facts["analysis"]["depth"]} nửa nước, nước này kém lựa chọn dẫn đầu {loss} điểm quy ước.' if actual else f'Tìm kiếm cục bộ sâu {facts["analysis"]["depth"]} nửa nước gợi ý {describe(pos, best["move"])}.'),
            'why': 'Dòng cụ thể để so sánh: ' + '; sau đó '.join(sequence) + '. Điểm dựa trên giá trị quân và Tốt qua sông. Đây là một dòng tìm kiếm nông, không khẳng định đối thủ buộc phải đi như vậy hoặc đây là nước tốt nhất toàn cục.',
            'how': LESSONS[facts['skill']] + ' Hãy nêu ít nhất hai nước ứng viên, dự đoán một nước đáp của đối thủ rồi so sánh kết quả.',
            'move': best['move'], 'pv': best['pv'], 'score': best['score'],
            'caution': 'Nhãn kỹ năng là gợi ý theo thế cờ, chưa kết luận lỗi tư duy của bạn. Phần tự giải thích được lưu, chưa có AI chấm chất lượng lập luận.',
        }


def explain_grounded(facts, reflection, provider=None):
    """Strict allowlist: external prose cannot add unverifiable chess claims.

    Until a stronger semantic verifier exists, providers must return the
    canonical grounded template. Failure, invented lines or prose falls back.
    """
    canonical = TemplateProvider().explain(facts, reflection)
    try:
        result = (provider or TemplateProvider()).explain(facts, reflection)
        if result != canonical:
            raise ValueError('Unverified explanation output')
        return result
    except Exception:
        return {**canonical, 'provider_error': True}
