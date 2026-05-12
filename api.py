from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load model and feature list
bundle = joblib.load("model.joblib")
model = bundle["model"]
FEATURES = bundle["features"]

class CICInput(BaseModel):
    data: dict  # dynamic fields

@app.post("/predict")
def predict(payload: CICInput):
    # Ensure the input contains expected features
    row = {f: payload.data.get(f, None) for f in FEATURES}
    df = pd.DataFrame([row])

    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0][1]

    return {
        "label": "ATTACK" if pred == 1 else "BENIGN",
        "score": round(float(proba), 4)
    }