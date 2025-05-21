from flask import Flask
from config import Config
from extensions import db, migrate
from models import Simptomas
from routes import setup_routes  # ← importuoji maršrutus


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

setup_routes(app)  # ← prijungi visus maršrutus

if __name__ == "__main__":
    app.run(debug=True)