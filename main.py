"""
패션 추천 서버 - 메인 진입점
실행: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from routers import recommend

app = FastAPI(
    title="Virtual Fitting 추천 서버",
    description="체형 기반 패션 추천 API (졸업작품)",
    version="1.0.0",
)

# 라우터 등록
app.include_router(recommend.router)


@app.get("/")
def root():
    return {"status": "서버 정상 동작 중", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
