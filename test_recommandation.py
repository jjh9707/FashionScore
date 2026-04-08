from services.recommendation import final_outfit_score, on_user_select

user = "user_1"

cloth1 = "top_001"
cloth2 = "pants_001"

tags1 = ["캐주얼", "오버핏"]
tags2 = ["캐주얼", "슬림핏"]

print("초기 점수:", final_outfit_score(user, cloth1, cloth2, tags1, tags2))

on_user_select(user, cloth1, cloth2, tags1, tags2)

print("학습 후 점수:", final_outfit_score(user, cloth1, cloth2, tags1, tags2))