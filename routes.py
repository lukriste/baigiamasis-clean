from flask import render_template, request, redirect, session
from extensions import db
from models import Simptomas
from scripts.model_answers import gauti_modelio_atsakyma

def setup_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            simptomas = request.form.get("simptomas", "").strip()
            ivestis = request.form.get("ivestis", "").strip()
            isvestis = gauti_modelio_atsakyma(simptomas, ivestis)

            naujas = Simptomas(
                simptomas=simptomas.strip().lower(),
                ivestis=ivestis.strip(),
                isvestis=isvestis.strip(),
                saltinis="vartotojas"
            )
            session["Atsakymas Jums: "] = isvestis
            db.session.add(naujas)
            db.session.commit()
            return redirect("/aciu")

        return render_template("index.html")

    @app.route("/aciu")
    def aciu():
        atsakymas = session.get("Atsakymas Jums", "Ačiū už pateiktą informaciją!")
        return render_template("aciu.html", atsakymas=atsakymas)