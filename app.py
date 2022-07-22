from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify, send_from_directory, flash, Markup
from flask_mysqldb import MySQL
import hashlib, MySQLdb.cursors, datetime, os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'png', 'pdf', 'doc', 'docx', 'zip'}

app = Flask(__name__)
app.secret_key = "XiCgaXUiemeLaPgCPx5fvcYCMFeuEH1fULZmAmYkuy1HWkCgtVA9Qbvb4qpTGt1i"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'mbkm_sql'
app.config['MYSQL_PASSWORD'] = 'Pa$$worD'
app.config['MYSQL_DB'] = 'mbkm_db'
app.config['MYSQL_PORT'] = 3306
app.config['UPLOAD_FOLDER'] = '/home/sysop/project/jwp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_password(passText):
	return hashlib.sha512(passText.encode()).hexdigest()

def generate_mbkm_id(nomorInduk):
	currDate = datetime.datetime.now()
	return str(nomorInduk) + '-' + str('{:02d}'.format(currDate.day)) + str('{:02d}'.format(currDate.month)) + str(currDate.year)

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

@app.route('/mahasiswa/ajukan-mbkm', methods=['GET','POST'])
def ajukan_mbkm():
	if session.get('nomor_induk') and session.get('username') and session.get('role'):
		if session['role'] == 'Mahasiswa':
			if request.method == 'GET':
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
				if all(i in request.form for i in('namaLengkap','nomorInduk','programStudi','angkatan','namaMBKM','jenisMBKM','tempatMBKM','semesterKlaim','namaMatkul1','dosenMatkul1','jumlahSKS1')) and 'buktiMBKM' in request.files:
					nama_lengkap = request.form['namaLengkap']
					nomor_induk = request.form['nomorInduk']
					id_pengajuan = generate_mbkm_id(nomor_induk)
					program_studi = request.form['programStudi']
					angkatan = request.form['angkatan']
					nama_mbkm = request.form['namaMBKM']
					jenis_mbkm = request.form['jenisMBKM']
					tempat_mbkm = request.form['tempatMBKM']
					semester_klaim = request.form['semesterKlaim']
					bukti_mbkm = request.files['buktiMBKM']

					nama_matkul1 = request.form['namaMatkul1']
					dosen_matkul1 = request.form['dosenMatkul1']
					nama_matkul2 = request.form['namaMatkul2'] if 'namaMatkul2' in request.form else None
					dosen_matkul2 = request.form['dosenMatkul2'] if 'dosenMatkul2' in request.form else None
					nama_matkul3 = request.form['namaMatkul3'] if 'namaMatkul3' in request.form else None
					dosen_matkul3 = request.form['dosenMatkul3'] if 'dosenMatkul3' in request.form else None
					nama_matkul4 = request.form['namaMatkul4'] if 'namaMatkul4' in request.form else None
					dosen_matkul4 = request.form['dosenMatkul4'] if 'dosenMatkul4' in request.form else None
					nama_matkul5 = request.form['namaMatkul5'] if 'namaMatkul5' in request.form else None
					dosen_matkul5 = request.form['dosenMatkul5'] if 'dosenMatkul5' in request.form else None
					nama_matkul6 = request.form['namaMatkul6'] if 'namaMatkul6' in request.form else None
					dosen_matkul6 = request.form['dosenMatkul6'] if 'dosenMatkul6' in request.form else None
					nama_matkul7 = request.form['namaMatkul7'] if 'namaMatkul7' in request.form else None
					dosen_matkul7 = request.form['dosenMatkul7'] if 'dosenMatkul7' in request.form else None
					nama_matkul8 = request.form['namaMatkul8'] if 'namaMatkul8' in request.form else None
					dosen_matkul8 = request.form['dosenMatkul8'] if 'dosenMatkul8' in request.form else None

					if bukti_mbkm.filename == '' :
						message = "<p class='text text-danger'>Harap Isi Semua Bagian Formulir dan Mata Kuliah Minimal 1!</p>"
						return render_template('/mahasiswa/ajukan-mbkm', message=message)
					
					if bukti_mbkm and allowed_file(bukti_mbkm.filename) :
						try:
							new_filename = secure_filename(id_pengajuan + '-buktiMBKM.' + bukti_mbkm.filename.rsplit('.', 1)[1].lower())
							bukti_mbkm.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
							link_bukti = request.base_url.replace('/mahasiswa/ajukan-mbkm', '/uploads/' + new_filename)

							connection = mysql.connection
							cursor = connection.cursor()
							sql_command_1 = "INSERT INTO tbl_pengajuan_mbkm (id_pengajuan, nomor_induk_mahasiswa, kode_prodi, angkatan, nama_program, jenis_program, tempat_program, bukti_program, semester_klaim, status_pengajuan) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
							sql_command_2 = "INSERT INTO tbl_matkul_mbkm(id_pengajuan,kode_matkul_1,nomor_dosen_1,kode_matkul_2,nomor_dosen_2,kode_matkul_3,nomor_dosen_3,kode_matkul_4,nomor_dosen_4,kode_matkul_5,nomor_dosen_5, kode_matkul_6,nomor_dosen_6,kode_matkul_7,nomor_dosen_7,kode_matkul_8,nomor_dosen_8) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
							data_command_1 =  (id_pengajuan, nomor_induk, program_studi, angkatan, nama_mbkm, jenis_mbkm, tempat_mbkm, link_bukti, semester_klaim, 'Waiting')
							data_command_2 = (id_pengajuan, nama_matkul1, dosen_matkul1, nama_matkul2, dosen_matkul2, nama_matkul3, dosen_matkul3, nama_matkul4, dosen_matkul4, nama_matkul5, dosen_matkul5, nama_matkul6, dosen_matkul6, nama_matkul7, dosen_matkul7, nama_matkul8, dosen_matkul8)
							cursor.execute(sql_command_1, data_command_1)
							cursor.execute(sql_command_2, data_command_2)
							connection.commit()

							return "<script>alert('Pengajuan Berhasil!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"
						
						except Exception:
							return "<script>alert('Pengajuan Gagal!'); window.location.href='/mahasiswa/index-mhs';</script>"
					
					else:
						message = "<p class='text text-danger'>Harap Isi Semua Bagian Formulir dan Mata Kuliah Minimal 1!</p>"
						return render_template('/mahasiswa/ajukan-mbkm', message=message)

				else:
					message = "<p class='text text-danger'>Harap Isi Semua Bagian Formulir dan Mata Kuliah Minimal 1!</p>"
					return render_template('/mahasiswa/ajukan-mbkm', message=message)

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

@app.route('/get_sks', methods=['POST'])
def get_sks():
	if request.method == 'POST' and 'kode_matkul' in request.form:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM tbl_mata_kuliah WHERE kode_matkul=%s", [request.form['kode_matkul']])
		matkul_data = cursor.fetchone()
		if matkul_data:
			return jsonify(jumlah_sks=matkul_data['jumlah_sks'])
		else:
			return jsonify(jumlah_sks=None)
	else:
		return jsonify(jumlah_sks=None)

@app.route('/uploads/<name>')
def get_file(name):
	return send_from_directory(app.config["UPLOAD_FOLDER"], name)






