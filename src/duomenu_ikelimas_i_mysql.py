import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from duomenu_tvarkymas import normalizuoti_teksta, sutvarkyti_sinonimus
import re

failo_kelias = "data/gnm_simptomai.xlsx"

df = pd.read_excel(failo_kelias)

df = df[['simptomas', 'sinonimai', 'GNM_konfliktas', 'GNM_pavyzdys', 'GNM_papildomapastaba']]
df["sinonimai"] = df["sinonimai"].apply(sutvarkyti_sinonimus)

for s in ["GNM_konfliktas", "GNM_pavyzdys", "GNM_papildomapastaba"]:
    df[s] = df[s].apply(normalizuoti_teksta)

engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm")
df.to_sql(name='simptomai', con=engine, if_exists='replace', index=False)







