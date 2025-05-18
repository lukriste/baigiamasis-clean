from transformers import TFAutoModelForSeq2SeqLM, T5Tokenizer
import tensorflow as tf
from models import Simptomas
from extensions import db
from rapidfuzz import fuzz
# Įkeliame išsaugotą modelį
model = TFAutoModelForSeq2SeqLM.from_pretrained("gnm-t5")
tokenizer = T5Tokenizer.from_pretrained("gnm-t5")

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