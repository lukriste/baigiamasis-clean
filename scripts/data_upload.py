import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
import pandas as pd
from sqlalchemy import create_engine
import re


def normalizuoti_teksta(tekstas):
    if pd.isna(tekstas): return ""
    tekstas = str(tekstas).strip()
    tekstas = tekstas.strip('"“”„‘’–—')
    tekstas = tekstas.replace("\\", "/")
    tekstas = re.sub(r"[\r\n\t]", " ", tekstas)
    tekstas = re.sub(r"\s{2,}", " ", tekstas)
    tekstas = re.sub(r"\s+([.,;!?()])", r"\1", tekstas)
    return tekstas

failo_kelias = "data/naujas_gnm.xlsx"
df = pd.read_excel(failo_kelias)

df = df.rename(columns={
    "Siptomas": "simptomas",
    "Input/situacija": "ivestis",
    "Output/GNM_interpretacija": "isvestis"
})

df["simptomas"] = df["simptomas"].apply(lambda x: normalizuoti_teksta(x).lower())
df["ivestis"] = df["ivestis"].apply(lambda x: normalizuoti_teksta(x).lower())
df["isvestis"] = df["isvestis"].apply(normalizuoti_teksta)
df["saltinis"] = "excel"  # pažymim, kad tai ne iš vartotojo


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


df.to_sql(name='simptomai', con=engine, if_exists='append', index=False)

print("Įrašai įkelti į Railway DB")

def paziureti_kiek_irasu():
    df = pd.read_sql("SELECT COUNT(*) FROM simptomai", engine)
    print("Iš viso įrašų:", df.iloc[0, 0])

# paziureti_kiek_irasu()