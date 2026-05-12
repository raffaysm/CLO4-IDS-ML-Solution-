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

# 2) Target column
if "Label" not in df.columns:
    raise ValueError("Label column not found in dataset.csv")

# 3) Binary label: BENIGN = 0, Attack = 1
df["label"] = df["Label"].apply(lambda x: 0 if str(x).upper() == "BENIGN" else 1)

# 4) Keep only numeric features (drop Label + non-numeric)
X = df.drop(columns=["Label", "label"], errors="ignore")
X = X.select_dtypes(include=[np.number])

y = df["label"]

# 5) Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 6) Pipeline: impute missing + scale + RF
pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("clf", RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ))
])

# 7) Train
pipeline.fit(X_train, y_train)

# 8) Evaluate
y_pred = pipeline.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 9) Save model + feature list
joblib.dump({
    "model": pipeline,
    "features": list(X.columns)
}, "model.joblib")

print("\nSaved model.joblib")