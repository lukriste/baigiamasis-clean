import pandas as pd
from sqlalchemy import create_engine
import re


def normalizuoti_teksta(tekstas):
    if pd.isna(tekstas):
        return ""
    tekstas = str(tekstas).strip()
    if tekstas.startswith('"') and tekstas.endswith('"'):
        tekstas = tekstas[1:-1]
    tekstas = tekstas.replace("“", '"').replace("”", '"').replace("„", '"')
    tekstas = tekstas.replace("‘", "'").replace("’", "'")
    tekstas = tekstas.replace("–", "-").replace("—", "-")
    tekstas = tekstas.replace("\\", "/")

    if tekstas.startswith('"'):
        tekstas = tekstas[1:]
    if tekstas.endswith('"'):
        tekstas = tekstas[:-1]
        
    tekstas = re.sub(r"[\r\n\t]", " ", tekstas)
    tekstas = re.sub(r"\s{2,}", " ", tekstas)
    tekstas = re.sub(r"\s+([.,;!?()])", r"\1", tekstas)
    return tekstas

# def sutvarkyti_sinonimus(tekstas):
#     if pd.isna(tekstas):
#         return tekstas
#     tekstas = "; ".join([s.strip() for s in tekstas.split(",")])
#     return normalizuoti_teksta(tekstas)

# def grupuoti_konflikta(tekstas):
#     if pd.isna(tekstas):
#         return "Nežinomas"

#     tekstas = tekstas.lower()

#     # Kūno „kąsnio“ konfliktas
#     if re.search(r"(kąsni|neviršk|praryt|saldum|nuoding|atsikrat|apdoroj|nepavyk|kūn|apsinuodij|maist|skon)", tekstas):
#         return "Kūno 'kąsnio' konfliktas"

#     # Savigarbos sumažėjimo konfliktas
#     if re.search(r"(savigarb|savivert|nuvertin|nepakankam|nevert|nesugeb|nepajėg|bevert|vert|išnykim|nematom|neverting)", tekstas):
#         return "Savigarbos sumažėjimo konfliktas"
    
#     if re.search(r"(savigarb|savivert|nuvertin|nepakankam|nevert|nesugeb|nepajėg|bevert)", tekstas):
#         return "Savigarbos sumažėjimo konfliktas"
    


#     # Streso konfliktas
#     if re.search(r"(laiko trūk|spaudimas|stres|ekstrem|suspėt|greitis)", tekstas):
#         return "Streso / greičio / spaudimo konfliktas"

#     # Išsiskyrimo konfliktas
#     if re.search(r"(išsiskyr|atskyr|netekt|palik|atstūm|išėj|prarad|vieniš|atsiskyr|izoliacij)", tekstas):
#         return "Išsiskyrimo konfliktas"

#     # Mirties baimės konfliktas
#     if re.search(r"(mirt|uždus|kvėpav|gyvyb|baim|dūst|deguon)", tekstas):
#         return "Mirties baimės konfliktas"

#     # Seksualinis konfliktas
#     if re.search(r"(seksual|intym|pažemin|lytin|santyk|žindym|geidul|genit)", tekstas):
#         return "Seksualinis konfliktas"

#     # Estetinis konfliktas
#     if re.search(r"(išvaizd|estet|žaves|grož|nepatrauk)", tekstas):
#         return "Estetinis konfliktas"

#     # Bėglio konfliktas
#     if re.search(r"(bėgl|bėg|pabėg|negalėjim.*pabėg|bėgau|nepabėg|egzistenc)", tekstas):
#         return "Bėglio konfliktas"
    
#     # Užsitęsę gijimo procesai / recidyvai
#     if re.search(r"(gijimo faz|gijim|gyjimo|gijimas|gyjim|gijimo rezultatas)", tekstas):
#         return "Gijimo fazės / gijimo procesai"

#     # Motorinis konfliktas
#     if re.search(r"(motorin|judėjim|negalėjim.*jud|negalėjim.*veik|nepajėg.*vaikšč|negalėjim.*ženg)", tekstas):
#         return "Motorinis konfliktas"
    
#     #Šeimos /santykių konfliktas
#     if re.search(r"(motin|tėv|šeim|vaik|partner|sutuoktin|močiut|protėvi|gimin)", tekstas):
#         return "Šeimos / santykių konfliktas"

#     # Sensorinis konfliktas
#     if re.search(r"(gird|nejautr|jutim|pojūt|klausy|svaig|neišgirst|nebegal.*gird|matyt|žiūr|nematyt|švies|vaizd|regėj|konjungty|reg|klausym|triukš|negird|vizual)", tekstas):
#         return "Sensorinis / regos / klausos konfliktas"
    
#     if re.search(r"(kvap|užuost|pojūtis|nemalonaus pojūčio)", tekstas):
#         return "Kvapo / jutiminis konfliktas"
    
#     if re.search(r"(atak|smūg|apsaug|smūgi|invazij|smurt)", tekstas):
#         return "Atakos / apsaugos konfliktas"


#     if re.search(r"(kontrol|priverstin|nurodym|paklusim|spaust|tvark|rūpesč|glob|pasirūp|priežiūr|atsakomyb|pareig)", tekstas):
#         return "Kontrolės / rūpesčio konfliktas"

#     # Kombinuotas konfliktas
#     if re.search(r"(dvigub|kombinuot|konsteliacij|derin|mišr|tarp dviej)", tekstas):
#         return "Kombinuotas konfliktas"

#     return "Kiti"









