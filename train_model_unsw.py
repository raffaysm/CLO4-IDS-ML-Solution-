import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib

# 1) Load data
df = pd.read_csv("dataset.csv", low_memory=False)

# 2) Use existing binary label column
if "label" not in df.columns:
    raise ValueError("label column not found in dataset.csv")

y = df["label"]

# 3) Keep only numeric features (drop non-numeric + label)
X = df.drop(columns=["label", "attack_cat"], errors="ignore")
X = X.select_dtypes(include=[np.number])

# 4) Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5) Pipeline
pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("clf", RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ))
])

# 6) Train
pipeline.fit(X_train, y_train)

# 7) Evaluate
y_pred = pipeline.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 8) Save model + features
joblib.dump({
    "model": pipeline,
    "features": list(X.columns)
}, "model.joblib")

print("\nSaved model.joblib")