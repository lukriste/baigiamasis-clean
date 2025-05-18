from rapidfuzz import fuzz
from flask import render_template, request, redirect, session
from extensions import db
from models import Simptomas
from scripts.model_helpers import gauti_modelio_atsakyma


def setup_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            simptomas = request.form.get("simptomas", "").strip()
            ivestis = request.form.get("ivestis", "").strip()

            if not simptomas:
                return "Prašome įvesti bent simptomą!", 400

            # AI modelio atsakymas
            isvestis_ai = gauti_modelio_atsakyma(simptomas, ivestis)

            # Paieška duomenų bazėje – rankinis atsakymas, jei yra
            # Gauti visus „rankinius“ įrašus
            visi_excel_simptomai = Simptomas.query.filter_by(saltinis='excel').all()

            geriausias = None
            geriausias_sutapimas = 0

            for irasas in visi_excel_simptomai:
                sutapimas = fuzz.token_set_ratio(irasas.simptomas, simptomas.lower())
                
                if sutapimas > geriausias_sutapimas:
                    geriausias_sutapimas = sutapimas
                    geriausias = irasas

                if geriausias and geriausias_sutapimas >= 60:
                    teisingas_atsakymas = geriausias.isvestis
                else:
                    teisingas_atsakymas = "🟡 Atsakymas bazėje nerastas."

            # Įrašyti į DB vartotojo įrašą
            naujas = Simptomas(
                simptomas=simptomas.lower(),
                ivestis=ivestis or None,
                isvestis=isvestis_ai,
                saltinis="vartotojas"
            )
            db.session.add(naujas)
            db.session.commit()

            # Siunčiam info į 'aciu.html'
            session["ai_atsakymas"] = isvestis_ai
            session["db_atsakymas"] = teisingas_atsakymas
            return redirect("/aciu")
    
        return render_template("index.html")

    @app.route("/aciu")
    def aciu():
        ai = session.get("ai_atsakymas", "Nepavyko gauti AI atsakymo.")
        db = session.get("db_atsakymas", "Nepavyko gauti teisingo atsakymo iš duomenų bazės.")
        return render_template("aciu.html", atsakymas_ai=ai, atsakymas_db=db)