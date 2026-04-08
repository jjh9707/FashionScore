"""
추천 관련 API 엔드포인트
"""

from fastapi import APIRouter
from models.schemas import (
    RecommendRequest, RecommendResponse,
    FeedbackRequest, OutfitRecommendation, SizeMatchResult
)

from algorithms.size_matching import knn_size_match, BodyMeasurement
from algorithms.color_harmony import color_harmony_score
from algorithms.style_matching import style_score
from algorithms.frequency_learning import get_frequency_score

from services.recommendation import on_user_select, on_user_reject

router = APIRouter(prefix="/recommend", tags=["추천"])


# ──────────────────────────────────────────
# 점수 가중치
# ──────────────────────────────────────────
W_SIZE      = 0.40
W_COLOR     = 0.25
W_STYLE     = 0.25
W_FREQUENCY = 0.10


@router.post("", response_model=RecommendResponse)
def get_recommendation(req: RecommendRequest):

    # 1️⃣ 체형 → 사이즈 매칭
    body = BodyMeasurement(
        height=req.body.height,
        shoulder=req.body.shoulder,
        chest=req.body.chest,
        waist=req.body.waist,
        hip=req.body.hip,
        arm_length=req.body.arm_length,
        inseam=req.body.inseam,
    )

    top_size_results    = knn_size_match(body, "top", k=1)
    bottom_size_results = knn_size_match(body, "bottom", k=1)

    size_score = (
        top_size_results[0].fit_score +
        bottom_size_results[0].fit_score
    ) / 2


    # 2️⃣ 카테고리 분리
    tops    = [c for c in req.closet if c.category == "top"]
    bottoms = [c for c in req.closet if c.category == "bottom"]

    print("tops:", tops)
    print("bottoms:", bottoms)


    # 3️⃣ 조합 점수 계산
    candidates = []

    for i, top in enumerate(tops):
        for j, bottom in enumerate(bottoms):

            # 스타일 점수
            style = style_score(top.style_tags, bottom.style_tags)

            # 색상 점수
            color = color_harmony_score(top.color_hex, bottom.color_hex)

            # 사이즈 점수
            size = size_score

            # 빈도 점수
            freq1 = get_frequency_score(req.user_id, top.cloth_id)
            freq2 = get_frequency_score(req.user_id, bottom.cloth_id)
            freq = (freq1 + freq2) / 2

            # 최종 점수
            total = (
                size * W_SIZE +
                color * W_COLOR +
                style * W_STYLE +
                freq * W_FREQUENCY
            )

            print("==== DEBUG ====")
            print("top:", top.cloth_id, top.style_tags)
            print("bottom:", bottom.cloth_id, bottom.style_tags)
            print("style:", style)
            print("color:", color)
            print("size:", size)
            print("freq:", freq)
            print("total:", total)

            candidates.append(OutfitRecommendation(
                outfit_id=f"outfit_{i}_{j}",
                top=top,
                bottom=bottom,
                outer=None,
                description="추천 코디",
                total_score=round(total, 1),
                size_score=round(size, 1),
                color_score=round(color, 1),
                style_score=round(style, 1),
                frequency_score=round(freq, 1),
            ))


    # 4️⃣ 정렬 후 top_k 반환
    candidates.sort(key=lambda x: x.total_score, reverse=True)
    top_outfits = candidates[:req.top_k]

    print("outfits:", top_outfits)

    return RecommendResponse(
        user_id=req.user_id,
        outfits=top_outfits,
    )


# ──────────────────────────────────────────
# 피드백 (학습)
# ──────────────────────────────────────────
@router.post("/feedback")
def receive_feedback(req: FeedbackRequest):

    if req.worn:
        on_user_select(
            req.user_id,
            req.cloth_id[0],
            req.cloth_id[1],
            req.tags[0],
            req.tags[1]
        )
    else:
        on_user_reject(
            req.user_id,
            req.cloth_id[0],
            req.cloth_id[1],
            req.tags[0],
            req.tags[1]
        )

    return {"message": "학습 완료"}


# ──────────────────────────────────────────
# 사이즈 추천
# ──────────────────────────────────────────
@router.post("/size", response_model=SizeMatchResult)
def get_size_only(body: BodyMeasurement, clothes_type: str = "top"):

    results = knn_size_match(body, clothes_type, k=3)
    best = results[0]

    return SizeMatchResult(
        recommended_size=best.size_label,
        fit_score=best.fit_score,
        fit_comment=best.fit_comment,
        alternatives=[r.size_label for r in results[1:]],
    )