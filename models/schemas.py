"""
API 요청 / 응답 데이터 구조 정의
Android 앱에서 보내는 JSON 형식과 서버가 돌려주는 JSON 형식
"""

from pydantic import BaseModel
from typing import Optional


# ──────────────────────────────────────────
# 요청 (Android → 서버)
# ──────────────────────────────────────────

class BodyData(BaseModel):
    """SAM3DBody에서 측정한 체형 데이터"""
    height: float           # 키 (cm)
    shoulder: float         # 어깨너비 (cm)
    chest: float            # 가슴둘레 (cm)
    waist: float            # 허리둘레 (cm)
    hip: float              # 힙둘레 (cm)
    arm_length: float       # 팔 길이 (cm)
    inseam: float           # 인심 (cm)


class ClothItem(BaseModel):
    """옷장에 등록된 옷 하나"""
    cloth_id: str           # 고유 ID
    name: str               # 옷 이름 (예: "흰 오버핏 티")
    category: str           # "top" | "bottom" | "outer"
    color_hex: str          # 대표 색상 (예: "#FFFFFF")
    style_tags: list[str]   # ["캐주얼", "루즈핏"]
    size_label: str         # "S" | "M" | "L" ...
    wear_count: int = 0     # 착용 횟수


class RecommendRequest(BaseModel):
    """추천 요청 전체"""
    user_id: str
    body: BodyData
    closet: list[ClothItem]         # 내 옷장 전체
    situation: Optional[str] = ""   # "캐주얼 외출", "비즈니스" 등
    top_k: int = 3                  # 추천 개수


class FeedbackRequest(BaseModel):
    """착용 피드백 요청 (개인화 학습용)"""
    user_id: str
    cloth_id: str
    worn: bool              # True: 착용함, False: 거절


# ──────────────────────────────────────────
# 응답 (서버 → Android)
# ──────────────────────────────────────────

class SizeMatchResult(BaseModel):
    """사이즈 매칭 결과"""
    recommended_size: str   # "M"
    fit_score: float        # 89.1
    fit_comment: str        # "어깨 딱 맞음"
    alternatives: list[str] # ["L", "S"] - 차선택


class OutfitRecommendation(BaseModel):
    """코디 하나"""
    outfit_id: str
    top: Optional[ClothItem]
    bottom: Optional[ClothItem]
    outer: Optional[ClothItem]
    total_score: float          # 최종 점수
    size_score: float           # 사이즈 점수
    color_score: float          # 색상 조화 점수
    style_score: float          # 스타일 점수
    frequency_score: float      # 착용 빈도 점수
    description: str            # 추천 이유 설명


class RecommendResponse(BaseModel):
    """추천 응답 전체"""
    user_id: str
    outfits: list[OutfitRecommendation]
    message: str = "추천 완료"
