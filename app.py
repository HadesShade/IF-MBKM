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

@app.route('/sekjur/index-sekjur')
def index_sekjur():
	return render_template('sekjur/index-sekjur.html')
	
@app.route('/sekjur/daftar-pengajuan-mbkm')
def daftar_pengajuan_mbkm():
	return render_template('sekjur/daftar-pengajuan-mbkm.html')

@app.route('/sekjur/lihat-berkas-sekjur')
def lihat_berkas_sekjur():
	return render_template('sekjur/lihat-berkas-sekjur.html')

@app.route('/sekjur/lihat-pengajuan-sekjur')
def lihat_pengajuan_sekjur():
	return render_template('sekjur/lihat-pengajuan-sekjur.html')

@app.route('/sekjur/jadwal-asesmen-sekjur')
def jadwal_asesmen_sekjur():
	return render_template('sekjur/jadwal-asesmen-sekjur.html')

@app.route('/sekjur/buat-asesmen-sekjur')
def buat_asesmen_sekjur():
	return render_template('sekjur/buat-asesmen-sekjur.html')

@app.route('/sekjur/ubah-asesmen-sekjur')
def ubah_asesmen_sekjur():
	return render_template('sekjur/ubah-asesmen-sekjur.html')

@app.route('/sekjur/lihat-asesmen-sekjur')
def lihat_asesmen_sekjur():
	return render_template('sekjur/lihat-asesmen-sekjur.html')

@app.route('/sekjur/proses-asesmen-sekjur')
def proses_asesmen_sekjur():
	return render_template('sekjur/proses-asesmen-sekjur.html')

@app.route('/dosen/index-dosen')
def index_dosen():
	return render_template('dosen/index-dosen.html')

@app.route('/dosen/jadwal-asesmen-dosen')
def jadwal_asesmen_dosen():
	return render_template('dosen/jadwal-asesmen-dosen.html')

@app.route('/dosen/lihat-pengajuan-dosen')
def lihat_pengajuan_dosen():
	return render_template('dosen/lihat-pengajuan-dosen.html')

@app.route('/dosen/lihat-berkas-dosen')
def lihat_berkas_dosen():
	return render_template('dosen/lihat-berkas-dosen.html')

@app.route('/dosen/lihat-asesmen-dosen')
def lihat_asesmen_dosen():
	return render_template('dosen/lihat-asesmen-dosen.html')

@app.route('/kaprodi/index-kaprodi')
def index_kaprodi():
	return render_template('kaprodi/index-kaprodi.html')

@app.route('/kaprodi/jadwal-asesmen-kaprodi')
def jadwal_asesmen_kaprodi():
	return render_template('kaprodi/jadwal-asesmen-kaprodi.html')

@app.route('/kaprodi/lihat-pengajuan-kaprodi')
def lihat_pengajuan_kaprodi():
	return render_template('kaprodi/lihat-pengajuan-kaprodi.html')

@app.route('/kaprodi/lihat-berkas-kaprodi')
def lihat_berkas_kaprodi():
	return render_template('kaprodi/lihat-berkas-kaprodi.html')

@app.route('/kaprodi/lihat-asesmen-kaprodi')
def lihat_asesmen_kaprodi():
	return render_template('kaprodi/lihat-asesmen-kaprodi.html')

