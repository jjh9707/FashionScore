from algorithms.style_matching import style_score
from algorithms.frequency_learning import (
    get_frequency_score,
    update_weight,
    update_style_preference,
    get_style_preference_score
)


# ──────────────────────────────────────────
# 최종 점수 계산
# ──────────────────────────────────────────

def final_outfit_score(user_id, cloth1, cloth2, tags1, tags2):

    # 1. 스타일 점수
    style = style_score(tags1, tags2)

    # 2. 개인화 (착용 빈도)
    freq1 = get_frequency_score(user_id, cloth1)
    freq2 = get_frequency_score(user_id, cloth2)
    freq_score = (freq1 + freq2) / 2

    # 3. 스타일 선호도
    pref = get_style_preference_score(user_id, tags1 + tags2)

    # 4. 최종 점수
    final = (
        style * 0.5 +
        freq_score * 0.3 +
        pref * 0.2
    )

    return round(min(100, max(0, final)), 1)


# ──────────────────────────────────────────
# 사용자 행동 반영 (학습)
# ──────────────────────────────────────────

def on_user_select(user_id, cloth1, cloth2, tags1, tags2):

    update_weight(user_id, cloth1, True)
    update_weight(user_id, cloth2, True)

    update_style_preference(user_id, tags1 + tags2, True)


def on_user_reject(user_id, cloth1, cloth2, tags1, tags2):

    update_weight(user_id, cloth1, False)
    update_weight(user_id, cloth2, False)

    update_style_preference(user_id, tags1 + tags2, False)