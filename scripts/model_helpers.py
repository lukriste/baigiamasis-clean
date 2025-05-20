import csv
import os
from datetime import datetime
from transformers import TFAutoModelForSeq2SeqLM, T5Tokenizer
import tensorflow as tf
from models import Simptomas
from extensions import db
from rapidfuzz import fuzz
import evaluate
# Įkeliame išsaugotą modelį
model = TFAutoModelForSeq2SeqLM.from_pretrained("trained_models/gnm-t5-liet-var2")
tokenizer = T5Tokenizer.from_pretrained("trained_models/gnm-t5-liet-var2")

def gauti_modelio_atsakyma(simptomas: str, ivestis: str) -> str:
    if not simptomas:
        return "Reikia nurodyti bent simptomą."

    tekstas = f"simptomas: {simptomas}."
    if ivestis:
        tekstas += f" situacija: {ivestis}"

    try:
        input_ids = tokenizer(tekstas, return_tensors="tf", truncation=True, padding=True).input_ids
        output_ids = model.generate(input_ids, max_length=128)
        atsakymas = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return atsakymas
    except Exception as e:
        return f"Klaida generuojant atsakymą: {str(e)}"
    
def irasyti_uzklausa(simptomas, ivestis, isvestis):
    naujas = Simptomas(
        simptomas=simptomas.lower(),
        ivestis=ivestis or None,
        isvestis=isvestis,
        saltinis="vartotojas"
    )
    db.session.add(naujas)
    db.session.commit()

def gauti_teisinga_atsakyma_pagal_simptoma(simptomas: str) -> str:
    atsakymas = Simptomas.query.filter(
        Simptomas.simptomas.ilike(f"%{simptomas.lower()}%"),
        Simptomas.saltinis == "excel"
    ).first()
    return atsakymas.isvestis if atsakymas else "🟡 Atsakymas bazėje nerastas."

def gauti_pavyzdine_situacija_ir_vertinimas(ai_atsakymas: str, riba: int = 60):
    visi_excel = Simptomas.query.filter_by(saltinis='excel').all()
    geriausias = None
    geriausias_sutapimas = 0

    for irasas in visi_excel:
        panašumas = fuzz.token_set_ratio(irasas.isvestis, ai_atsakymas)
        if panašumas > geriausias_sutapimas:
            geriausias_sutapimas = panašumas
            geriausias = irasas

    if geriausias and geriausias_sutapimas >= riba:
        return (
            geriausias.ivestis,
            "Atsakymas pagrįstas duomenų baze (patikimumas aukštas)",
            geriausias_sutapimas
        )
    else:
        return (
            "Situacija nerasta – AI atsakymas galimai netikslus.",
            "Modelio atsakymas neatitiko jokio žinomo duomenų bazės įrašo",
            geriausias_sutapimas
        )

def ivertinti_atsakyma(simptomas: str, ivertinimas: str):
    irasas = Simptomas.query.filter_by(simptomas=simptomas.lower(), saltinis='vartotojas').order_by(Simptomas.created_at.desc()).first()
    if irasas:
        irasas.ivertinimas = ivertinimas
        db.session.commit()


def suformuoti_situacija(form):
    return (
        f"{form.get('lytis', 'Asmuo')} ({form.get('amzius', '?')} m.) "
        f"pajuto simptomą. Prieš tai nutiko: {form.get('ivestis', '')}. "
        f"Emociškai įvykis įvertintas kaip {form.get('emocija', 'nežinoma')} patirtis."
    )

def irasyti_ivertinima_i_csv(simptomas, ivestis, modelio_ats, tikras_ats, rouge_score, bleu_score):
    laukai = ["timestamp", "simptomas", "ivestis", "modelio_ats", "tikras_ats", "rouge", "bleu"]
    eilute = {
        "timestamp": datetime.now().isoformat(),
        "simptomas": simptomas,
        "ivestis": ivestis,
        "modelio_ats": modelio_ats,
        "tikras_ats": tikras_ats,
        "rouge": round(rouge_score, 4) if rouge_score is not None else None,
        "bleu": round(bleu_score, 4) if bleu_score is not None else None
    }

    failo_pavadinimas = "data/vertinimo_metrikos.csv"  
    failas_egzistuoja = os.path.isfile(failo_pavadinimas)

    with open(failo_pavadinimas, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=laukai)
        if not failas_egzistuoja:
            writer.writeheader()
        writer.writerow(eilute)

rouge_metric = evaluate.load("rouge")
bleu_metric = evaluate.load("bleu")

def ivertinti_atsakyma_automatiniskai(modelio_ats: str, tikras_ats: str):
    try:
        # ROUGE (naudojam ROUGE-L)
        rouge = rouge_metric.compute(predictions=[modelio_ats], references=[tikras_ats])
        rouge_score = rouge["rougeL"]

        # BLEU (tekstų palyginimas, ne split'ai!)
        bleu = bleu_metric.compute(
            predictions=[modelio_ats],
            references=[tikras_ats]
        )
        bleu_score = bleu["bleu"]

        return rouge_score, bleu_score
    except Exception as e:
        print(f"Klaida skaičiuojant metrikas: {str(e)}")
        return None, None


def rasti_artimiausia_simptoma(ivestas_simptomas, riba=70):
    visi = Simptomas.query.filter_by(saltinis="excel").all()

    geriausias = None
    geriausias_sutapimas = 0

    for irasas in visi:
        panašumas = fuzz.token_set_ratio(ivestas_simptomas.lower(), irasas.simptomas.lower())
        if panašumas > geriausias_sutapimas:
            geriausias_sutapimas = panašumas
            geriausias = irasas

    if geriausias and geriausias_sutapimas >= riba:
        return geriausias.simptomas
    else:
        return ivestas_simptomas