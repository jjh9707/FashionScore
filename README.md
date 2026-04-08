# 👕 FashionScore - Style Recommendation Server

## 📌 프로젝트 소개

사용자의 의류 정보를 기반으로 스타일을 분석하고
코디 점수 및 추천 결과를 제공하는 FastAPI 기반 서버입니다.

이 서버는 Rule 기반 + 일부 ML 로직을 활용하여
색상, 스타일, 사이즈를 종합적으로 평가합니다.

---

## 🛠 기술 스택

* Python 3.10+
* FastAPI
* Uvicorn

---

## 📂 프로젝트 구조

```text
RecommandServer/
 ├── algorithms/     # 스타일/색상/사이즈 추천 로직
 ├── routers/        # API 엔드포인트 정의
 ├── services/       # 추천 서비스 로직
 ├── models/         # Request/Response 모델
 ├── main.py         # FastAPI 실행
 ├── requirements.txt
 └── .gitignore
```

---

##  실행 방법

```bash
git clone https://github.com/jjh9707/FashionScore.git
cd FashionScore

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

uvicorn main:app --reload
```

👉 실행 후 Swagger UI:
http://127.0.0.1:8000/docs

---

## 📡 API 문서 (Swagger 기반)

FastAPI는 기본적으로 Swagger UI를 제공합니다.

👉 실행 후 아래에서 테스트 가능
http://127.0.0.1:8000/docs

---

##  핵심 API

###  1. 스타일 추천 API

#### ▶ Endpoint

```http
POST /recommend
```

#### ▶ Request Body (예시)

```json
{
  "top": "white shirt",
  "bottom": "black jeans",
  "style": "casual",
  "size": "M"
}
```

#### ▶ Response (예시)

```json
{
  "score": 87,
  "color_match": 90,
  "style_match": 85,
  "size_match": 88,
  "comment": "깔끔한 캐주얼 조합입니다."
}
```

---

## ⚙️ 내부 동작 구조

추천은 다음 단계로 수행됩니다:

1. 색상 조합 분석 (`color_harmony`)
2. 스타일 매칭 (`style_matching`)
3. 사이즈 매칭 (`size_matching`)
4. (선택) ML 기반 보정 (`style_ml`)
5. 최종 점수 계산

👉 `services/recommendation.py`에서 통합 처리

---

## 📊 Swagger 활용 방법

1. `/docs` 접속
2. `POST /recommend` 클릭
3. "Try it out"
4. JSON 입력 후 Execute

 바로 테스트 가능

---

##  협업 가이드

###  보안

* `.env`는 절대 업로드 금지

###  환경 세팅

```bash
pip install -r requirements.txt
```

###  작업 흐름

```bash
git pull
git add .
git commit -m "작업 내용"
git push
```

---

##  테스트

```bash
python test_recommandation.py
python test_style.py
```

---

##  향후 계획

* ML 기반 추천 정확도 향상
* 사용자 취향 학습 기능
* Unity / Android 앱 연동
* 실시간 추천 API 최적화

---

##  목표

패션 데이터를 기반으로
“자동 코디 추천 시스템” 구축
