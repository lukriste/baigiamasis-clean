import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  #uztikrina kad importas config veiks

from sqlalchemy import create_engine,text
from config import Config


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

with engine.connect() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS simptomai (
        id INT AUTO_INCREMENT PRIMARY KEY,
        simptomas VARCHAR(255),
        ivestis TEXT,
        isvestis TEXT,
        saltinis ENUM('excel', 'vartotojas') DEFAULT 'vartotojas',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""))
    print("✅ Lentelė 'simptomai' sukurta arba jau egzistuoja.")