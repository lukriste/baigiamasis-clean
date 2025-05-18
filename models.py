from extensions import db

class Simptomas(db.Model):
    __tablename__ = 'simptomai'

    id = db.Column(db.Integer, primary_key=True)
    simptomas = db.Column(db.String(255), nullable=False)
    ivestis = db.Column(db.Text)
    isvestis = db.Column(db.Text)
    saltinis = db.Column(db.Enum('excel', 'vartotojas'), default='vartotojas')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    ivertinimas = db.Column(db.Enum('teigiamas', 'neigiamas'), nullable=True)