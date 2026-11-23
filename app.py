from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

print("CEK URL:", os.environ.get('DATABASE_URL'))

app = Flask(__name__)

# --- PENGATURAN DATABASE NEON ---
db_url = os.environ.get('DATABASE_URL')

# Memperbaiki format URL agar sesuai dengan SQLAlchemy dan psycopg3
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# --------------------------------

# Model Tabel Database
class Surat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_surat = db.Column(db.String(100), nullable=False)
    alamat_surat = db.Column(db.String(255), nullable=False)
    tgl_dibuat = db.Column(db.String(50), nullable=False)
    tgl_dikirim = db.Column(db.String(50), nullable=False)
    perihal = db.Column(db.String(255), nullable=False)

# Membuat tabel di database Neon secara otomatis saat aplikasi pertama kali dijalankan
with app.app_context():
    db.create_all()

# Fungsi generate nomor surat otomatis
def generate_no_surat():
    total = Surat.query.count() + 1
    bulan_romawi = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    sekarang = datetime.now()
    bulan = bulan_romawi[sekarang.month - 1]
    tahun = sekarang.year
    
    # Format: 001/HMPS-PAI/01/A-0/XI/2025
    return f"{total:03d}/HMPS-PAI/01/A-0/{bulan}/{tahun}"

@app.route('/')
def index():
    data_surat = Surat.query.order_by(Surat.id.desc()).all()
    no_otomatis = generate_no_surat() 
    return render_template('index.html', surat=data_surat, no_otomatis=no_otomatis)

@app.route('/tambah', methods=['POST'])
def tambah():
    alamat = request.form['alamat_surat']
    tgl_dibuat = request.form['tgl_dibuat']
    tgl_dikirim = request.form['tgl_dikirim']
    perihal = request.form['perihal']
    
    # Cek apakah user mengedit nomor surat di form
    no_surat_input = request.form.get('no_surat', '').strip()
    no_surat = no_surat_input if no_surat_input else generate_no_surat()

    surat_baru = Surat(no_surat=no_surat, alamat_surat=alamat, tgl_dibuat=tgl_dibuat, tgl_dikirim=tgl_dikirim, perihal=perihal)
    db.session.add(surat_baru)
    db.session.commit()
    return redirect('/')

@app.route('/hapus/<int:id>')
def hapus(id):
    surat = Surat.query.get_or_404(id)
    db.session.delete(surat)
    db.session.commit()
    return redirect('/')

@app.route('/hapus_semua')
def hapus_semua():
    db.session.query(Surat).delete()
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    # Tambahkan host 0.0.0.0 agar bisa diakses via jaringan lokal jika diperlukan
    app.run(host='0.0.0.0', port=5000, debug=True)