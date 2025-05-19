from flask import render_template, request, redirect, session
from extensions import db
from models import Simptomas
from scripts.model_helpers import gauti_modelio_atsakyma, irasyti_uzklausa, gauti_teisinga_atsakyma_pagal_simptoma,gauti_pavyzdine_situacija_ir_vertinimas,ivertinti_atsakyma, suformuoti_situacija, irasyti_ivertinima_i_csv, ivertinti_atsakyma_automatiniskai

def setup_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        visi_simptomai = db.session.query(Simptomas.simptomas).filter_by(saltinis="excel").distinct().all()
        simptomu_sarasas = sorted(set(s[0].strip().lower() for s in visi_simptomai if s[0]))
        if request.method == "POST":
            simptomas = request.form.get("simptomas", "").strip()
            amzius = request.form.get("amzius", "").strip()
            lytis = request.form.get("lytis", "").strip().lower()

            klaidos = []

            if not simptomas:
                klaidos.append("Prašome pasirinkti simptomą.")

            try:
                amzius_int = int(amzius)
                if not 1 <= amzius_int <= 110:
                    klaidos.append("Amžius turi būti tarp 1 ir 110.")
            except ValueError:
                klaidos.append("Amžius turi būti skaičius.")

            if lytis not in ("vyras", "moteris"):
                klaidos.append("Pasirinkite tinkamą lytį.")

            if klaidos:
                return render_template("index.html", simptomai=simptomu_sarasas, klaidos=klaidos)

            ivestis = suformuoti_situacija(request.form)
            # AI atsakymas
            isvestis_ai = gauti_modelio_atsakyma(simptomas, ivestis)

            # Rankinis atsakymas iš DB
            teisingas_atsakymas = gauti_teisinga_atsakyma_pagal_simptoma(simptomas)

            # Situacijos pavyzdys iš DB pagal AI atsakymą
            situacija, patikimumas, _ = gauti_pavyzdine_situacija_ir_vertinimas(isvestis_ai)

            # Įrašas į DB
            irasyti_uzklausa(simptomas, ivestis, isvestis_ai)

            # Į sesiją
            session["simptomas"] = simptomas
            session["ai_atsakymas"] = isvestis_ai
            session["db_atsakymas"] = teisingas_atsakymas
            session["situacijos_pavyzdys"] = situacija
            session["atsakymo_patikimumas"] = patikimumas
            
            rouge_score, bleu_score = ivertinti_atsakyma_automatiniskai(isvestis_ai, teisingas_atsakymas)

            irasyti_ivertinima_i_csv(
                simptomas=simptomas,
                ivestis=ivestis,
                modelio_ats=isvestis_ai,
                tikras_ats=teisingas_atsakymas,
                rouge_score=rouge_score,
                bleu_score=bleu_score
            )

            return redirect("/aciu")

        return render_template("index.html", simptomai=simptomu_sarasas)

    @app.route("/aciu")
    def aciu():
        return render_template("aciu.html",
            atsakymas_ai=session.get("ai_atsakymas", ""),
            atsakymas_db=session.get("db_atsakymas", ""),
            situacija=session.get("situacijos_pavyzdys", ""),
            atsakymo_patikimumas=session.get("atsakymo_patikimumas", ""),
            simptomas=session.get("simptomas", "")
        )

    @app.route("/ivertinti", methods=["POST"])
    def ivertinti():
        simptomas = request.form.get("simptomas")
        ivertinimas = request.form.get("ivertinimas")

        if simptomas and ivertinimas:
            ivertinti_atsakyma(simptomas, ivertinimas)

        return redirect("/")