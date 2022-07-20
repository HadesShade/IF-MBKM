from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'mbkm_sql'
app.config['MYSQL_PASSWORD'] = 'Pa$$worD'
app.config['MYSQL_DB'] = 'mbkm_db'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

@app.route('/')
def login():
	return render_template('login.html')

@app.route('/mahasiswa/index-mhs')
def index_mhs():
	return render_template('mahasiswa/index-mhs.html')

@app.route('/mahasiswa/ajukan-mbkm')
def ajukan_mbkm():
	return render_template('mahasiswa/ajukan-mbkm.html')

@app.route('/mahasiswa/status-mbkm-mhs')
def status_mbkm_mhs():
	return render_template('mahasiswa/status-mbkm-mhs.html')

@app.route('/mahasiswa/status-mbkm-mhs-detail')
def status_mbkm_mhs_detail():
	return render_template('mahasiswa/status-mbkm-mhs-detail.html')

@app.route('/mahasiswa/jadwal-asesmen-mhs')
def jadwal_asesmen_mhs():
	return render_template('mahasiswa/jadwal-asesmen-mhs.html')

@app.route('/mahasiswa/unggah-berkas-mhs')
def unggah_berkas_mhs():
	return render_template('mahasiswa/unggah-berkas-mhs.html')

@app.route('/mahasiswa/lihat-berkas-mhs')
def lihat_berkas_mhs():
	return render_template('mahasiswa/lihat-berkas-mhs.html')
	


