import math

# ──────────────────────────────────────────
# ✅ 태그 정리
# ──────────────────────────────────────────

STYLE_TAGS = [
    "캐주얼","포멀","스트리트","미니멀","스포티",
    "오버핏","슬림핏"
]

TAG_INDEX = {tag: i for i, tag in enumerate(STYLE_TAGS)}

TAG_WEIGHT = {
    "캐주얼": 1.0,
    "포멀": 1.2,
    "스트리트": 1.1,
    "미니멀": 1.0,
    "스포티": 0.9,
    "오버핏": 0.7,
    "슬림핏": 0.8,
}

# ──────────────────────────────────────────
# ✅ 스타일 그룹
# ──────────────────────────────────────────

STYLE_GROUP = {
    "캐주얼": "데일리",
    "스트리트": "데일리",
    "미니멀": "데일리",
    "포멀": "포멀",
    "스포티": "활동",
}

# ──────────────────────────────────────────
# ✅ 호환성 룰
# ──────────────────────────────────────────

COMPATIBILITY_RULES = {
    ("캐주얼","캐주얼"): 10,
    ("포멀","포멀"): 10,
    ("스트리트","스트리트"): 9,

    ("캐주얼","스트리트"): 8,
    ("캐주얼","미니멀"): 6,
    ("미니멀","포멀"): 5,
    ("스포티","캐주얼"): 5,

    ("캐주얼","포멀"): -8,
    ("스트리트","포멀"): -7,
}

# ──────────────────────────────────────────
# 🔥 그룹 유사도 (개선)
# ──────────────────────────────────────────

def group_similarity(tags1, tags2):
    if not tags1 or not tags2:
        return 40

    # 🔥 완전 동일
    if set(tags1) == set(tags2):
        return 90

    groups1 = set(STYLE_GROUP.get(t) for t in tags1 if t in STYLE_GROUP)
    groups2 = set(STYLE_GROUP.get(t) for t in tags2 if t in STYLE_GROUP)

    if groups1 & groups2:
        return 80

    return 35

# ──────────────────────────────────────────
# 호환성 점수
# ──────────────────────────────────────────

def compatibility_score(tags1, tags2):
    total = 0
    count = 0

    for t1 in tags1:
        for t2 in tags2:
            if t1 == t2:
                continue
            total += COMPATIBILITY_RULES.get((t1, t2), 0)
            total += COMPATIBILITY_RULES.get((t2, t1), 0)
            count += 1

    if count == 0:
        return 0

    return total / count

# ──────────────────────────────────────────
# 🔥 실루엣 점수 (강화)
# ──────────────────────────────────────────

def silhouette_score(tags1, tags2):
    score = 0

    if ("오버핏" in tags1 and "슬림핏" in tags2) or \
       ("슬림핏" in tags1 and "오버핏" in tags2):
        score += 10   # 🔥 증가

    if "슬림핏" in tags1 and "슬림핏" in tags2:
        score += 6

    if "오버핏" in tags1 and "오버핏" in tags2:
        score += 4

    return score

# ──────────────────────────────────────────
# 🔥 최종 점수 계산
# ──────────────────────────────────────────

def style_score(tags1, tags2):

    if not tags1 or not tags2:
        return 0

    # 🔥 완전 동일 보너스
    if set(tags1) == set(tags2):
        if "포멀" in tags1:
            return 95
        return 90

    style1 = [t for t in tags1 if t in STYLE_GROUP]
    style2 = [t for t in tags2 if t in STYLE_GROUP]

    # 1. 그룹 유사도
    sim = group_similarity(style1, style2)

    # 🔥 핏-only 보정
    if not style1 and not style2:
        sim = 60

    # 2. 호환성
    comp_raw = compatibility_score(style1, style2)
    comp = (comp_raw + 10) * 5

    # 3. 실루엣
    sil_raw = silhouette_score(tags1, tags2)
    sil = sil_raw * 10

    # 🔥 가중치 튜닝 (스타일 더 중요)
    score = (
        sim * 0.55 +
        comp * 0.25 +
        sil * 0.20
    )

    return round(max(0, min(100, score)), 1)

# ──────────────────────────────────────────
# 🔥 설명 개선
# ──────────────────────────────────────────

def explain(tags1, tags2):
    reasons = []

    if set(tags1) == set(tags2):
        reasons.append("완전히 동일한 스타일 조합")

    elif set(tags1) & set(tags2):
        reasons.append("같은 스타일이라 안정적인 조합")

    if ("오버핏" in tags1 and "슬림핏" in tags2) or \
       ("슬림핏" in tags1 and "오버핏" in tags2):
        reasons.append("핏 대비로 실루엣 밸런스가 좋음")

    comp = compatibility_score(tags1, tags2)

    if comp > 2:
        reasons.append("스타일 조합이 자연스럽고 조화로움")
    elif comp < -2:
        reasons.append("대비되는 스타일로 개성 있는 코디")

    return reasons