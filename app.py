import os
from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Memuat variabel dari file .env (untuk testing lokal)
load_dotenv()

app = Flask(__name__)

# --- PENGATURAN DATABASE ---
db_url = os.environ.get('DATABASE_URL')

if db_url:
    # 1. Perbaiki skema jika dari Render/Neon menggunakan 'postgres://'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # 2. Paksa SQLAlchemy menggunakan driver psycopg (v3)
    # Ini mencegah error ModuleNotFoundError: No module named 'psycopg'
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Konfigurasi Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kunci-rahasia-default')

# Inisialisasi Database
db = SQLAlchemy(app)

# --- CONTOH MODEL (Bisa Anda sesuaikan) ---
# Model ini hanya contoh untuk memastikan database terhubung.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

# --- ROUTES ---
@app.route('/')
def home():
    # Mengecek koneksi ke database (opsional, untuk memastikan tidak error)
    try:
        db.session.execute(db.text('SELECT 1'))
        status_db = "Berhasil terhubung ke Database!"
    except Exception as e:
        status_db = f"Gagal terhubung ke Database. Error: {str(e)}"
        
    return f"<h1>Aplikasi Berjalan!</h1><p>Status Database: {status_db}</p>"

if __name__ == '__main__':
    # Untuk testing di laptop lokal
    app.run(debug=True, port=5000)