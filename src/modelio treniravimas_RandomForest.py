
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix,  precision_score, recall_score, f1_score, balanced_accuracy_score,accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt
from duomenu_tvarkymas import grupuoti_konflikta,  normalizuoti_teksta, sutvarkyti_sinonimus
from sqlalchemy import create_engine


engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm")

df = pd.read_sql("SELECT * FROM simptomai", con=engine)

df["simptomas"] = df["simptomas"].apply(normalizuoti_teksta)
df["sinonimai"] = df["sinonimai"].apply(sutvarkyti_sinonimus)
df["GNM_konfliktas"] = df["GNM_konfliktas"].apply(normalizuoti_teksta)

df = df[df["GNM_konfliktas"].notna()]  
df["input_text"] = df["simptomas"].fillna("") + " " + df["sinonimai"].fillna("")
df["konflikto_grupe"] = df["GNM_konfliktas"].apply(grupuoti_konflikta)


X = df["input_text"].values
y = df["konflikto_grupe"].values

# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Modelio sukūrimas (TF-IDF + Random Forest)
modelis = make_pipeline(TfidfVectorizer(), RandomForestClassifier(n_estimators=100, random_state=42))
modelis.fit(X_train, y_train)

# 5. Tikslumo patikrinimas
print("\nModelio tikslumas:", modelis.score(X_test, y_test))

# 6. Klasifikacijos ataskaita
y_pred = modelis.predict(X_test)
print("\nKlasifikacijos ataskaita:\n")
print(classification_report(y_test, y_pred))

# 7. Confusion matrix
plt.figure(figsize=(12, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap="Blues",
            xticklabels=modelis.classes_, yticklabels=modelis.classes_)
plt.xlabel("Prognozuota")
plt.ylabel("Tikroji")
plt.title("Confusion Matrix")
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# 8. Testavimas su nauju tekstu
tekstas = "skausmas gerklėje, sunku kalbėti"
prognoze = modelis.predict([tekstas])[0]
print(f"\nPrognozuojamas konfliktas: {prognoze}")

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Balanced Accuracy:", balanced_accuracy_score(y_test, y_pred))
print("Precision (svertinis):", precision_score(y_test, y_pred, average='weighted'))
print("Recall (svertinis):", recall_score(y_test, y_pred, average='weighted'))
print("F1-score (svertinis):", f1_score(y_test, y_pred, average='weighted'))