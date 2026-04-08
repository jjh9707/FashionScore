"""
착용 빈도 기반 개인화 학습 알고리즘
- 착용/거절 피드백으로 옷별 가중치 업데이트
- 최근 착용일수록 높은 점수 (시간 감쇠 적용)
- 사용자별 독립적인 가중치 관리
"""

import time


# 사용자별 옷 가중치 저장소
# 구조: { user_id: { cloth_id: { "weight": float, "last_worn": timestamp } } }
_store: dict = {}

# ──────────────────────────────────────────
# 상수
# ──────────────────────────────────────────
INITIAL_WEIGHT  = 0.5    # 처음 등록된 옷의 기본 가중치
WEAR_BOOST      = 0.10   # 착용 시 가중치 증가량
REJECT_PENALTY  = 0.05   # 거절 시 가중치 감소량
MAX_WEIGHT      = 1.0
MIN_WEIGHT      = 0.0
DECAY_DAYS      = 30     # 시간 감쇠 기준 (30일)


# ──────────────────────────────────────────
# 핵심 알고리즘
# ──────────────────────────────────────────

def _time_decay(last_worn_ts: float) -> float:
    """
    시간 감쇠 계수 계산 (0.5 ~ 1.0)

    최근에 자주 입은 옷일수록 높은 점수를 유지하고
    오래 안 입은 옷은 점수가 자연스럽게 낮아지는 효과
    
    공식: decay = 0.5 + 0.5 × exp(-경과일 / 30)
    - 오늘 입었으면 decay ≈ 1.0
    - 30일 전이면 decay ≈ 0.68
    - 90일 전이면 decay ≈ 0.52
    """
    if last_worn_ts == 0:
        return 0.7   # 한 번도 안 입은 옷 기본값

    elapsed_days = (time.time() - last_worn_ts) / 86400.0
    import math
    decay = 0.5 + 0.5 * math.exp(-elapsed_days / DECAY_DAYS)
    return round(decay, 4)


def get_frequency_score(user_id: str, cloth_id: str) -> float:
    """
    해당 사용자의 옷 착용 빈도 점수 반환 (0~100)
    가중치 × 시간 감쇠 계수로 최종 점수 계산
    """
    user_data = _store.get(user_id, {})
    cloth_data = user_data.get(cloth_id, {
        "weight": INITIAL_WEIGHT,
        "last_worn": 0
    })

    weight     = cloth_data["weight"]
    last_worn  = cloth_data["last_worn"]
    decay      = _time_decay(last_worn)

    score = weight * decay * 100.0
    return round(min(100.0, max(0.0, score)), 1)


def update_weight(user_id: str, cloth_id: str, worn: bool):
    """
    착용 피드백 반영 → 가중치 업데이트
    
    착용(worn=True)  → 가중치 +0.10, 최근 착용 시간 갱신
    거절(worn=False) → 가중치 -0.05
    """
    if user_id not in _store:
        _store[user_id] = {}

    if cloth_id not in _store[user_id]:
        _store[user_id][cloth_id] = {
            "weight": INITIAL_WEIGHT,
            "last_worn": 0
        }

    current = _store[user_id][cloth_id]["weight"]

    if worn:
        _store[user_id][cloth_id]["weight"]    = min(MAX_WEIGHT, current + WEAR_BOOST)
        _store[user_id][cloth_id]["last_worn"] = time.time()
    else:
        _store[user_id][cloth_id]["weight"]    = max(MIN_WEIGHT, current - REJECT_PENALTY)


def get_user_favorites(user_id: str, top_n: int = 5) -> list:
    """
    사용자의 자주 입는 옷 top_n개 반환
    개인화 추천에서 우선순위 부스터로 활용
    """
    user_data = _store.get(user_id, {})
    scored = [
        (cloth_id, get_frequency_score(user_id, cloth_id))
        for cloth_id in user_data
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]

# ──────────────────────────────────────────
# 스타일 선호도 학습 (추가)
# ──────────────────────────────────────────

_style_store = {}

def update_style_preference(user_id: str, tags: list, liked: bool):
    if user_id not in _style_store:
        _style_store[user_id] = {}

    for tag in tags:
        if tag not in _style_store[user_id]:
            _style_store[user_id][tag] = 0.5

        if liked:
            _style_store[user_id][tag] = min(1.0, _style_store[user_id][tag] + 0.1)
        else:
            _style_store[user_id][tag] = max(0.0, _style_store[user_id][tag] - 0.05)


def get_style_preference_score(user_id: str, tags: list) -> float:
    user_data = _style_store.get(user_id, {})

    if not tags:
        return 50.0

    scores = [user_data.get(tag, 0.5) for tag in tags]
    return round((sum(scores) / len(scores)) * 100, 1)




# ──────────────────────────────────────────
# 테스트
# ──────────────────────────────────────────

if __name__ == "__main__":
    import math

    user = "user_001"

    print("\n" + "=" * 50)
    print("  착용 빈도 학습 테스트")
    print("=" * 50)

    # 초기 점수
    score_init = get_frequency_score(user, "cloth_white_tee")
    print(f"\n  [초기] 흰 티 점수:  {score_init}점")

    # 5번 착용
    for _ in range(5):
        update_weight(user, "cloth_white_tee", worn=True)
    score_worn = get_frequency_score(user, "cloth_white_tee")
    print(f"  [5번 착용 후] 흰 티: {score_worn}점")

    # 2번 거절
    update_weight(user, "cloth_black_pants", worn=False)
    update_weight(user, "cloth_black_pants", worn=False)
    score_rej = get_frequency_score(user, "cloth_black_pants")
    print(f"  [2번 거절 후] 검정 팬츠: {score_rej}점")

    # 시간 감쇠 시뮬레이션
    print(f"\n  [ 시간 감쇠 시뮬레이션 ]")
    for days in [0, 7, 14, 30, 60, 90]:
        decay = 0.5 + 0.5 * math.exp(-days / DECAY_DAYS)
        bar = "█" * int(decay * 10) + "░" * (10 - int(decay * 10))
        print(f"  {days:>3}일 경과  [{bar}]  감쇠계수: {decay:.3f}")

    print("\n" + "=" * 50)
