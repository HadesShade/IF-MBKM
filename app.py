from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_mysqldb import MySQL
import hashlib, MySQLdb.cursors, datetime

app = Flask(__name__)
app.secret_key = "XiCgaXUiemeLaPgCPx5fvcYCMFeuEH1fULZmAmYkuy1HWkCgtVA9Qbvb4qpTGt1i"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'mbkm_sql'
app.config['MYSQL_PASSWORD'] = 'Pa$$worD'
app.config['MYSQL_DB'] = 'mbkm_db'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

def encrypt_password(passText):
	return hashlib.sha512(passText.encode()).hexdigest()

def generate_mbkm_id(nomorInduk):
	currDate = datetime.datetime.now()
	return nomorInduk + '-' + currDate.day + currDate.month + currDate.year

def generate_asesmen_id(mbkmID, asesmenDate):
	return mbkmID + '-' + asesmenDate

@app.route('/')
def default():
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Mahasiswa':
			return redirect('/mahasiswa/index-mhs')
		elif session['role'] == 'Sekretaris Jurusan':
			return redirect('/sekjur/index-sekjur')
		elif session['role'] == 'Ketua Jurusan':
			return redirect('/kajur/index-kajur')
		elif session['role'] == 'Kepala Prodi':
			return redirect('/kaprodi/index-kaprodi')
		elif session['role'] == 'Dosen':
			return redirect('/dosen/index-dosen')
	
	return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login():
	invalid = ""
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM tbl_user where username=%s AND password=%s", (username, encrypt_password(password)))
		account = cursor.fetchone()
		if account:
			session['nomor_induk'] = account['nomor_induk']
			session['username'] = account['username']
			session['role'] = account['role']

			if session['role'] == 'Mahasiswa':
				return redirect('/mahasiswa/index-mhs')
			elif session['role'] == 'Sekretaris Jurusan':
				return redirect('/sekjur/index-sekjur')
			elif session['role'] == 'Ketua Jurusan':
				return redirect('/kajur/index-kajur')
			elif session['role'] == 'Kepala Prodi':
				return redirect('/kaprodi/index-kaprodi')
			elif session['role'] == 'Dosen':
				return redirect('/dosen/index-dosen')
		else:
			invalid = "Login Salah! Silahkan Periksa Kredensial Anda!"
		
	return render_template('login.html', invalid=invalid)
		

@app.route('/mahasiswa/index-mhs', methods=['GET'])
def index_mhs():
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Mahasiswa':
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
				full_name = account_detail['nama']
				user_role = account_detail['role']
				user_email = account_detail['email']
				telp_number = account_detail['telp']
				user_address = account_detail['alamat']
				return render_template('mahasiswa/index-mhs.html', nomor_induk=nomor_induk, full_name=full_name, user_role=user_role, user_email=user_email, telp_number=telp_number, user_address=user_address)
			else:
				return redirect('/logout')
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/mahasiswa/ajukan-mbkm')
def ajukan_mbkm():
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Mahasiswa':
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
				full_name = account_detail['nama']
				program_studi = ""
				cursor.execute("SELECT * from tbl_prodi_if")
				for item in cursor.fetchall():
					program_studi += f"<option value='{item['kode_prodi']}'>{item['kode_prodi']  + ' - ' + item['jenjang'] + ' ' + item['nama_prodi']}</option>"
				
				mata_kuliah=""
				cursor.execute("SELECT * from tbl_mata_kuliah")
				for item in cursor.fetchall():
					mata_kuliah += f"<option value='{item['kode_matkul']}'>{item['kode_matkul']  + ' - ' + item['nama_matkul']}</option>"
				
				dosen_list = ""
				cursor.execute("SELECT * from tbl_user where NOT role='Mahasiswa'")
				for item in cursor.fetchall():
					dosen_list += f"<option value='{item['nomor_induk']}'>{item['nomor_induk']  + ' - ' + item['nama']}</option>"

				return render_template('mahasiswa/ajukan-mbkm.html', nomor_induk=nomor_induk, full_name=full_name, program_studi=program_studi, mata_kuliah=mata_kuliah, dosen_list=dosen_list)
			else:
				return redirect('/logout')
		else:
			return redirect('/')
	else:
		return redirect('/login')

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
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Sekretaris Jurusan':
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
				full_name = account_detail['nama']
				user_role = account_detail['role']
				user_email = account_detail['email']
				telp_number = account_detail['telp']
				user_address = account_detail['alamat']
				return render_template('sekjur/index-sekjur.html', nomor_induk=nomor_induk, full_name=full_name, user_role=user_role, user_email=user_email, telp_number=telp_number, user_address=user_address)
			else:
				return redirect('/logout')
		else:
			return redirect('/')
	else:
		return redirect('/login')
	
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
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Dosen':
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
				full_name = account_detail['nama']
				user_role = account_detail['role']
				user_email = account_detail['email']
				telp_number = account_detail['telp']
				user_address = account_detail['alamat']
				return render_template('dosen/index-dosen.html', nomor_induk=nomor_induk, full_name=full_name, user_role=user_role,user_email=user_email, telp_number=telp_number, user_address=user_address)
			else:
				return redirect('/logout')
		else:
			return redirect('/')
	else:
		return redirect('/login')

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
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Kepala Prodi':
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
				full_name = account_detail['nama']
				user_role = account_detail['role']
				user_email = account_detail['email']
				telp_number = account_detail['telp']
				user_address = account_detail['alamat']
				return render_template('kaprodi/index-kaprodi.html', nomor_induk=nomor_induk, full_name=full_name, user_role=user_role,user_email=user_email, telp_number=telp_number, user_address=user_address)
			else:
				return redirect('/logout')
		else:
			return redirect('/')
	else:
		return redirect('/login')

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

@app.route('/kajur/index-kajur')
def index_kajur():
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Ketua Jurusan':
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
				full_name = account_detail['nama']
				user_role = account_detail['role']
				user_email = account_detail['email']
				telp_number = account_detail['telp']
				user_address = account_detail['alamat']
				return render_template('kajur/index-kajur.html', nomor_induk=nomor_induk, full_name=full_name, user_role=user_role,user_email=user_email, telp_number=telp_number, user_address=user_address)
			else:
				return redirect('/logout')
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kajur/jadwal-asesmen-kajur')
def jadwal_asesmen_kajur():
	return render_template('kajur/jadwal-asesmen-kajur.html')

@app.route('/kajur/lihat-pengajuan-kajur')
def lihat_pengajuan_kajur():
	return render_template('kajur/lihat-pengajuan-kajur.html')

@app.route('/kajur/lihat-berkas-kajur')
def lihat_berkas_kajur():
	return render_template('kajur/lihat-berkas-kajur.html')

@app.route('/kajur/lihat-asesmen-kajur')
def lihat_asesmen_kajur():
	return render_template('kajur/lihat-asesmen-kajur.html')

@app.route('/logout')
def logout():
	session.pop('nomor_induk', None)
	session.pop('username', None)
	session.pop('role', None)
	return redirect('/')

