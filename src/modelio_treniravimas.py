# 📘 GNM Konfliktų Klasifikavimas su TF-IDF + Naive Bayes

import pandas as pd
from sqlalchemy import create_engine
from duomenu_tvarkymas import grupuoti_konflikta
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer

engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm")

df = pd.read_sql("SELECT * FROM simptomai", con=engine)
df = df[df["GNM_konfliktas"].notna()]
df["input_text"] = df["simptomas"].fillna("") + " " + df["sinonimai"].fillna("")
df["konflikto_grupe"] = df["GNM_konfliktas"].apply(grupuoti_konflikta)

liet_stop_zodziai = [
    "ir", "ar", "kad", "bet", "o", "nes", "jog", "bei", "taip", "tada", 
    "kai", "kur", "kas", "koks", "tokiu", "toks", "jis", "ji", "jų", "jo",
    "tuo", "todėl", "tačiau", "čia", "ten", "dar", "jau", "tik", "vis", "dėl",
    "man", "tau", "jam", "jos", "mums", "jums", "jų", "aš", "tu", "mes", "jie", "jos",
    "esu", "yra", "buvo", "būti", "bus", "buvau"
]
vectorizer = TfidfVectorizer(stop_words=liet_stop_zodziai)

def pasalinti_stop_zodzius(tekstas, stop_zodziai):
    zodziai = tekstas.split()
    grynas = [z for z in zodziai if z.lower() not in stop_zodziai]
    return " ".join(grynas)

df["input_text"] = df["input_text"].apply(lambda t: pasalinti_stop_zodzius(t, liet_stop_zodziai))

X = df["input_text"].values
y = df["konflikto_grupe"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelis = make_pipeline(TfidfVectorizer(stop_words=liet_stop_zodziai), MultinomialNB())
modelis.fit(X_train, y_train)

print("\nModelio tikslumas:", modelis.score(X_test, y_test))
y_pred = modelis.predict(X_test)

print("\nKlasifikacijos ataskaita:\n")

print(classification_report(y_test, y_pred))
plt.figure(figsize=(12, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap="Blues",
            xticklabels=modelis.classes_, yticklabels=modelis.classes_)
plt.xlabel("Prognozuota")
plt.ylabel("Tikroji")
plt.title("Confusion Matrix")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 8. Testavimas su nauju tekstu
tekstas = "skausmas gerklėje, sunku kalbėti"
prognoze = modelis.predict([tekstas])[0]
print(f"\nPrognozuojamas konfliktas: {prognoze}")


