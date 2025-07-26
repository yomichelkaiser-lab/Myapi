from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Veritabanı ayarı (Render.com ile uyumlu SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hesaplar.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Kategori tablosu
class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False, unique=True)
    hesaplar = db.relationship('Hesap', backref='kategori', lazy=True)

# Hesap tablosu
class Hesap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    veri = db.Column(db.String(100), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    kullanildi = db.Column(db.Boolean, default=False)

# Veritabanını oluştur
def create_tables():
    with app.app_context():
        db.create_all()

# API: Belirli bir kategorideki kullanılmamış hesapları getir
@app.route("/api/<kategori_ad>", methods=["GET"])
def kategoriye_gore_hesaplar(kategori_ad):
    kategori = Kategori.query.filter_by(ad=kategori_ad).first()
    if not kategori:
        return jsonify({"error": "Kategori bulunamadı"}), 404
    hesap = Hesap.query.filter_by(kategori_id=kategori.id, kullanildi=False).first()
    if not hesap:
        return jsonify({"error": "Hesap kalmadı"}), 404
    hesap.kullanildi = True
    db.session.commit()
    return jsonify({"hesap": hesap.veri})

# API: Yeni kategori ekle (manuel kullanım)
@app.route("/api/kategori_ekle", methods=["POST"])
def kategori_ekle():
    data = request.json
    ad = data.get("ad")
    if not ad:
        return jsonify({"error": "Kategori adı gerekli"}), 400
    if Kategori.query.filter_by(ad=ad).first():
        return jsonify({"error": "Bu kategori zaten var"}), 400
    yeni = Kategori(ad=ad)
    db.session.add(yeni)
    db.session.commit()
    return jsonify({"message": "Kategori eklendi"})

# API: Kategoriye hesap ekle
@app.route("/api/hesap_ekle", methods=["POST"])
def hesap_ekle():
    data = request.json
    kategori_ad = data.get("kategori")
    veri = data.get("veri")
    if not kategori_ad or not veri:
        return jsonify({"error": "Veri eksik"}), 400
    kategori = Kategori.query.filter_by(ad=kategori_ad).first()
    if not kategori:
        return jsonify({"error": "Kategori bulunamadı"}), 404
    hesap = Hesap(veri=veri, kategori_id=kategori.id)
    db.session.add(hesap)
    db.session.commit()
    return jsonify({"message": "Hesap eklendi"})

# Render için: 0.0.0.0 ve port ayarı
if __name__ == "__main__":
    create_tables()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
