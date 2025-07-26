from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hesaplar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), unique=True, nullable=False)
    hesaplar = db.relationship('Hesap', backref='kategori', lazy=True)

class Hesap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hesap = db.Column(db.String(100), unique=True, nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)

def create_tables():
    db.create_all()

@app.route('/')
def index():
    kategoriler = Kategori.query.all()
    return render_template('index.html', kategoriler=kategoriler)

@app.route('/kategori-ekle', methods=['GET', 'POST'])
def kategori_ekle():
    if request.method == 'POST':
        isim = request.form.get('isim')
        if isim and not Kategori.query.filter_by(isim=isim).first():
            yeni = Kategori(isim=isim)
            db.session.add(yeni)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('kategori-ekle.html')

@app.route('/ekle', methods=['GET', 'POST'])
def hesap_ekle():
    kategoriler = Kategori.query.all()
    if request.method == 'POST':
        hesap = request.form.get('hesap')
        kategori_id = request.form.get('kategori_id')
        if hesap and kategori_id and not Hesap.query.filter_by(hesap=hesap).first():
            yeni = Hesap(hesap=hesap, kategori_id=int(kategori_id))
            db.session.add(yeni)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('hesap-ekle.html', kategoriler=kategoriler)

@app.route('/api/kategori/<int:kategori_id>/hesaplar')
def api_hesaplar(kategori_id):
    hesaplar = Hesap.query.filter_by(kategori_id=kategori_id).all()
    hesap_listesi = [h.hesap for h in hesaplar]
    return jsonify(hesap_listesi)

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)
