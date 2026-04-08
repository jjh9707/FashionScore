"""
색상 조화 알고리즘
- RGB → HSV 변환 직접 구현
- HSV 색상환 기반 조화 규칙으로 점수 계산
- 유사색 / 보색 / 삼각배색 / 무채색 규칙 적용
"""


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


def rgb_to_hsv(r: int, g: int, b: int) -> tuple:
    """
    RGB → HSV 직접 구현
    H: 색상 0~360°  S: 채도 0~1  V: 명도 0~1
    HSV를 쓰는 이유: H 값 차이만으로 색상환에서
    두 색이 얼마나 떨어졌는지 바로 계산 가능
    """
    r_f, g_f, b_f = r / 255.0, g / 255.0, b / 255.0
    c_max, c_min = max(r_f, g_f, b_f), min(r_f, g_f, b_f)
    delta = c_max - c_min

    if delta == 0:      h = 0.0
    elif c_max == r_f:  h = 60.0 * (((g_f - b_f) / delta) % 6)
    elif c_max == g_f:  h = 60.0 * (((b_f - r_f) / delta) + 2)
    else:               h = 60.0 * (((r_f - g_f) / delta) + 4)

    s = 0.0 if c_max == 0 else delta / c_max
    return h, s, c_max


def hue_distance(h1: float, h2: float) -> float:
    """색상환에서 두 색의 최단 각도 차이 (0~180°)"""
    diff = abs(h1 - h2)
    return min(diff, 360.0 - diff)


def is_achromatic(s: float) -> bool:
    """무채색 판별 — 채도 0.15 미만이면 흰/검/회색"""
    return s < 0.15


def get_harmony_rule(h_dist: float) -> tuple:
    """
    Hue 각도 차이 → 색채학 조화 규칙 + 기본 점수
      유사색   (0~30°)   : 자연스럽고 안정적      → 90점
      보색     (150~210°): 강렬한 대비, 포인트     → 85점
      삼각배색 (115~125°): 균형 잡힌 배색          → 75점
      근접유사 (30~60°)  : 무난한 조합             → 65점
      중간대비 (60~115°) : 다소 어색               → 40점
      부조화   (나머지)  : 안 어울림               → 25점
    """
    if h_dist <= 30:                              return "유사색",      90.0
    elif 150 <= h_dist <= 210:                    return "보색",        85.0
    elif 115 <= h_dist <= 125 or 235 <= h_dist <= 245: return "삼각배색", 75.0
    elif h_dist <= 60:                            return "근접 유사색", 65.0
    elif h_dist < 115:                            return "중간 대비",   40.0
    else:                                         return "부조화",      25.0


def color_harmony_score(hex1: str, hex2: str) -> float:
    """
    두 색상의 조화 점수 (0~100)
    무채색(흰/검/회)은 어떤 색과도 잘 어울려 고정 보너스
    유채색끼리는 Hue 차이 기반 색채학 규칙 적용
    + 명도 차이가 클수록 시각 대비 보너스 최대 +10점
    """
    h1, s1, v1 = rgb_to_hsv(*hex_to_rgb(hex1))
    h2, s2, v2 = rgb_to_hsv(*hex_to_rgb(hex2))

    if is_achromatic(s1) and is_achromatic(s2): return 80.0
    if is_achromatic(s1) or  is_achromatic(s2): return 85.0

    _, base = get_harmony_rule(hue_distance(h1, h2))
    v_bonus = abs(v1 - v2) * 10.0
    return round(min(100.0, base + v_bonus), 1)


def get_color_comment(hex1: str, hex2: str) -> str:
    h1, s1, v1 = rgb_to_hsv(*hex_to_rgb(hex1))
    h2, s2, v2 = rgb_to_hsv(*hex_to_rgb(hex2))
    if is_achromatic(s1) or is_achromatic(s2):
        return "무채색 포함 — 무난하게 어울려요"
    rule, _ = get_harmony_rule(hue_distance(h1, h2))
    return {
        "유사색":      "비슷한 색 계열 — 안정적인 코디예요",
        "보색":        "반대 색 조합 — 강렬한 포인트 코디예요",
        "삼각배색":    "균형 잡힌 배색이에요",
        "근접 유사색": "자연스러운 색 조합이에요",
        "중간 대비":   "색 대비가 있는 조합이에요",
        "부조화":      "색 조합이 다소 어색할 수 있어요",
    }.get(rule, "")


if __name__ == "__main__":
    tests = [
        ("흰 티 + 검정 팬츠 (무채색)",  "#FFFFFF", "#1A1A1A"),
        ("네이비 + 흰색 (무채색 포함)", "#1F3A6E", "#FFFFFF"),
        ("하늘색 + 연청 (유사색)",      "#87CEEB", "#6BA3BE"),
        ("빨강 + 초록 (보색)",          "#E63946", "#2D6A4F"),
        ("파랑 + 주황 (보색)",          "#2196F3", "#FF9800"),
        ("노랑 + 보라 (보색)",          "#FFC107", "#9C27B0"),
        ("빨강 + 파랑 (부조화)",        "#E63946", "#2196F3"),
    ]
    print("\n" + "=" * 58)
    print("  색상 조화 점수 테스트")
    print("=" * 58)
    for desc, h1, h2 in tests:
        score = color_harmony_score(h1, h2)
        comment = get_color_comment(h1, h2)
        bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        print(f"\n  {desc}")
        print(f"  [{bar}] {score:>5.1f}점  →  {comment}")
    print("\n" + "=" * 58)
