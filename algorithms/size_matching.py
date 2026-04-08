"""
체형 치수 기반 사이즈 매칭 알고리즘
- kNN을 직접 구현 (sklearn 없이)
- SAM3DBody에서 받은 체형 데이터 기반
- 상의 / 하의 / 아우터 각각 지원
"""

import math
from dataclasses import dataclass
from typing import Optional


# ──────────────────────────────────────────
# 데이터 구조
# ──────────────────────────────────────────

@dataclass
class BodyMeasurement:
    """SAM3DBody에서 받아오는 체형 치수 (단위: cm)"""
    height: float        # 키
    shoulder: float      # 어깨너비
    chest: float         # 가슴둘레
    waist: float         # 허리둘레
    hip: float           # 힙둘레
    arm_length: float    # 팔 길이
    inseam: float        # 인심 (하의용)


@dataclass
class SizeSpec:
    """옷 사이즈 스펙"""
    label: str           # "S", "M", "L", "XL", "XXL"
    height_range: tuple  # (최소 키, 최대 키)
    shoulder: float
    chest: float
    waist: float
    hip: float
    arm_length: float
    inseam: float


@dataclass
class MatchResult:
    """매칭 결과"""
    rank: int
    size_label: str
    distance: float
    fit_score: float     # 0~100점
    fit_comment: str     # "딱 맞음", "약간 여유 있음" 등


# ──────────────────────────────────────────
# 사이즈 데이터베이스
# ──────────────────────────────────────────

# 상의 사이즈 스펙 (한국 표준 기준)
TOP_SIZE_DB: list[SizeSpec] = [
    SizeSpec("XS",  (155, 162), 38, 82, 66, 88,  57, 0),
    SizeSpec("S",   (160, 167), 40, 86, 70, 92,  58, 0),
    SizeSpec("M",   (165, 172), 42, 90, 74, 96,  59, 0),
    SizeSpec("L",   (170, 177), 44, 94, 78, 100, 60, 0),
    SizeSpec("XL",  (175, 182), 46, 98, 82, 104, 61, 0),
    SizeSpec("XXL", (180, 187), 48, 102,86, 108, 62, 0),
]

# 하의 사이즈 스펙
BOTTOM_SIZE_DB: list[SizeSpec] = [
    SizeSpec("XS",  (155, 162), 0, 0, 64, 86,  0, 72),
    SizeSpec("S",   (160, 167), 0, 0, 68, 90,  0, 74),
    SizeSpec("M",   (165, 172), 0, 0, 72, 94,  0, 76),
    SizeSpec("L",   (170, 177), 0, 0, 76, 98,  0, 78),
    SizeSpec("XL",  (175, 182), 0, 0, 80, 102, 0, 80),
    SizeSpec("XXL", (180, 187), 0, 0, 84, 106, 0, 82),
]


# ──────────────────────────────────────────
# 핵심 알고리즘
# ──────────────────────────────────────────

# 부위별 중요도 가중치 (합계 = 1.0)
# 어깨는 수선이 어렵기 때문에 가중치가 높음
TOP_WEIGHTS = {
    "shoulder":   0.35,
    "chest":      0.25,
    "waist":      0.20,
    "hip":        0.10,
    "arm_length": 0.10,
}

BOTTOM_WEIGHTS = {
    "waist":   0.40,
    "hip":     0.35,
    "inseam":  0.25,
}


def euclidean_distance(body: BodyMeasurement,
                       spec: SizeSpec,
                       weights: dict) -> float:
    """
    가중 유클리드 거리 계산 (kNN의 핵심)

    일반 유클리드:  √(Σ(xi - yi)²)
    가중 유클리드:  √(Σ wi × (xi - yi)²)

    가중치를 주는 이유: 어깨처럼 수선이 어려운 부위는
    조금만 달라도 불편하기 때문에 더 큰 패널티를 줌
    """
    total = 0.0
    for part, weight in weights.items():
        body_val = getattr(body, part)
        spec_val = getattr(spec, part)
        if spec_val == 0:   # 해당 부위 데이터 없으면 스킵
            continue
        diff = body_val - spec_val
        total += weight * (diff ** 2)
    return math.sqrt(total)


def normalize_distance_to_score(distance: float,
                                 max_distance: float = 10.0) -> float:
    """
    거리값을 0~100 점수로 변환
    거리가 0이면 100점, max_distance 이상이면 0점
    """
    score = max(0.0, 100.0 - (distance / max_distance) * 100.0)
    return round(score, 1)


def get_fit_comment(body: BodyMeasurement,
                    spec: SizeSpec,
                    clothes_type: str) -> str:
    """
    실제 치수 차이를 분석해서 코멘트 생성
    예: "어깨가 약간 넓을 수 있어요", "허리가 여유 있어요"
    """
    comments = []

    if clothes_type == "top":
        shoulder_diff = body.shoulder - spec.shoulder
        chest_diff    = body.chest - spec.chest
        waist_diff    = body.waist - spec.waist

        if abs(shoulder_diff) <= 1:
            comments.append("어깨 딱 맞음")
        elif shoulder_diff > 1:
            comments.append(f"어깨 {shoulder_diff:.1f}cm 더 넓을 수 있음")
        else:
            comments.append(f"어깨 {abs(shoulder_diff):.1f}cm 여유 있음")

        if chest_diff > 3:
            comments.append("가슴 여유 있음 (루즈핏)")
        elif chest_diff < -2:
            comments.append("가슴 약간 타이트")

        if waist_diff > 4:
            comments.append("허리 여유 있음")

    elif clothes_type == "bottom":
        waist_diff  = body.waist - spec.waist
        hip_diff    = body.hip - spec.hip
        inseam_diff = body.inseam - spec.inseam

        if abs(waist_diff) <= 1:
            comments.append("허리 딱 맞음")
        elif waist_diff > 1:
            comments.append(f"허리 {waist_diff:.1f}cm 더 클 수 있음")
        else:
            comments.append(f"허리 {abs(waist_diff):.1f}cm 여유 있음")

        if inseam_diff > 2:
            comments.append(f"기장 {inseam_diff:.1f}cm 길 수 있음")
        elif inseam_diff < -2:
            comments.append(f"기장 {abs(inseam_diff):.1f}cm 짧을 수 있음")

    return " / ".join(comments) if comments else "잘 맞을 것 같아요"


def knn_size_match(body: BodyMeasurement,
                   clothes_type: str = "top",
                   k: int = 3) -> list[MatchResult]:
    """
    kNN 사이즈 매칭 메인 함수

    Args:
        body: SAM3DBody에서 받은 체형 치수
        clothes_type: "top" | "bottom"
        k: 상위 k개 결과 반환

    Returns:
        거리 가까운 순으로 정렬된 MatchResult 리스트
    """
    if clothes_type == "top":
        size_db = TOP_SIZE_DB
        weights = TOP_WEIGHTS
    else:
        size_db = BOTTOM_SIZE_DB
        weights = BOTTOM_WEIGHTS

    # 모든 사이즈와의 거리 계산
    distances = []
    for spec in size_db:
        dist = euclidean_distance(body, spec, weights)
        distances.append((spec, dist))

    # 거리 오름차순 정렬
    distances.sort(key=lambda x: x[1])

    # 최대 거리 (점수 정규화용)
    max_dist = max(d for _, d in distances) if distances else 10.0

    # 상위 k개 결과 생성
    results = []
    for rank, (spec, dist) in enumerate(distances[:k], start=1):
        score   = normalize_distance_to_score(dist, max_dist)
        comment = get_fit_comment(body, spec, clothes_type)
        results.append(MatchResult(
            rank=rank,
            size_label=spec.label,
            distance=round(dist, 4),
            fit_score=score,
            fit_comment=comment,
        ))

    return results


# ──────────────────────────────────────────
# 출력 헬퍼
# ──────────────────────────────────────────

def print_results(results: list[MatchResult], clothes_type: str):
    label = "상의" if clothes_type == "top" else "하의"
    print(f"\n{'='*45}")
    print(f"  {label} 사이즈 추천 결과 (Top {len(results)})")
    print(f"{'='*45}")
    for r in results:
        bar = "█" * int(r.fit_score / 10) + "░" * (10 - int(r.fit_score / 10))
        print(f"  {r.rank}위  {r.size_label:>3}  [{bar}] {r.fit_score:>5.1f}점")
        print(f"       → {r.fit_comment}")
    print(f"{'='*45}")
    print(f"  최종 추천: {results[0].size_label} 사이즈")
    print(f"{'='*45}\n")


# ──────────────────────────────────────────
# 테스트
# ──────────────────────────────────────────

if __name__ == "__main__":

    # SAM3DBody에서 받아온 체형 데이터 예시
    user = BodyMeasurement(
        height=172,
        shoulder=43,
        chest=91,
        waist=75,
        hip=97,
        arm_length=59,
        inseam=77,
    )

    print("\n[ 입력된 체형 치수 ]")
    print(f"  키: {user.height}cm  어깨: {user.shoulder}cm")
    print(f"  가슴: {user.chest}cm  허리: {user.waist}cm")
    print(f"  힙: {user.hip}cm  팔길이: {user.arm_length}cm  인심: {user.inseam}cm")

    # 상의 추천
    top_results = knn_size_match(user, clothes_type="top", k=3)
    print_results(top_results, "top")

    # 하의 추천
    bottom_results = knn_size_match(user, clothes_type="bottom", k=3)
    print_results(bottom_results, "bottom")
