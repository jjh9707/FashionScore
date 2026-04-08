# style_ml.py

from sklearn.linear_model import LogisticRegression
from .style_matching import tags_to_vector

model = LogisticRegression()

# 예시 데이터 (나중에 교체)
X = []
y = []

def train():
    global model

    # TODO: 실제 데이터 넣기
    X.extend([
        tags_to_vector(["캐주얼"]) + tags_to_vector(["슬림핏"]),
        tags_to_vector(["포멀"]) + tags_to_vector(["스포티"]),
    ])

    y.extend([1, 0])

    model.fit(X, y)


def predict(tags1, tags2):
    vec = tags_to_vector(tags1) + tags_to_vector(tags2)
    return model.predict_proba([vec])[0][1]