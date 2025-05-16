import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from duomenu_tvarkymas import normalizuoti_teksta
import re

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

engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm1")
df.to_sql(name='simptomai', con=engine, if_exists='replace', index=False)

print("✅ Duomenys įkelti į 'gnm1.simptomai'")








