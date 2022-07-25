from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify, send_from_directory, flash, Markup
from flask_mysqldb import MySQL
import hashlib, MySQLdb.cursors, datetime, os, glob
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

def reverse_date_string(dateStr):
	split_date = dateStr.split('-')
	return  '-'.join(split_date[::-1])

@app.route('/')
def default():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
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
			session['fullname'] = account['nama']

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
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			nomor_induk = session['nomor_induk']
			full_name = session['fullname']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
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
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			if request.method == 'GET':
				full_name = session['fullname']
				nomor_induk = session['nomor_induk']
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

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
						return "<script>alert('Harap Isi Semua Bagian Formulir dan Mata Kuliah Minimal 1!'); window.location.href='/mahasiswa/ajukan-mbkm'</script>"

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
						return "<script>alert('Harap Isi Semua Bagian Formulir dan Mata Kuliah Minimal 1!'); window.location.href='/mahasiswa/ajukan-mbkm'</script>"

				else:
					return "<script>alert('Harap Isi Semua Bagian Formulir dan Mata Kuliah Minimal 1!'); window.location.href='/mahasiswa/ajukan-mbkm'</script>"

		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/mahasiswa/status-mbkm-mhs', methods=['GET'])
def status_mbkm_mhs():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			if request.method == 'GET' :
				full_name = session['fullname']
				nomor_induk = session['nomor_induk']
				status_list = ''
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT id_pengajuan, nama_program, status_pengajuan FROM tbl_pengajuan_mbkm where nomor_induk_mahasiswa=%s", [nomor_induk])
				for item in cursor.fetchall():
					persetujuan = ""
					berkas = ""
					if item['status_pengajuan'] == 'Waiting' :
						persetujuan = "<td><p class='text text-warning'>🕐 Menunggu Persetujuan</p></td>"
						berkas = "<td><p class='text text-warning'>🕐 Menunggu Persetujuan</p></td>"
					elif item['status_pengajuan'] == 'Rejected' :
						persetujuan = "<td><p class='text text-danger'>✕ Pengajuan Ditolak</p></td>"
						berkas = "<td><p class='text text-danger'>✕ Pengajuan Ditolak</p></td>"
					else:
						persetujuan = "<td><p class='text-success'>✓ Pengajuan Disetujui</p></td>"
						berkas = "<td><button type='button' onclick=\"{click}\" class='btn btn-primary'><i class='fas fa-file'></i> Unggah Berkas</button></td>".format(click = f"window.location.href='/mahasiswa/unggah-berkas-mhs?id_pengajuan={item['id_pengajuan']}'")

					newcursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
					newcursor.execute("SELECT id_pengajuan from tbl_berkas_mbkm where id_pengajuan=%s", [item['id_pengajuan']])
					if newcursor.fetchone():
						berkas = """
								<td>
									<button type='button' onclick="window.location.href='/mahasiswa/lihat-berkas-mhs?id_pengajuan={id}'" class='btn btn-primary'><i class='fas fa-eye'></i></button>
									<button type='button' onclick="window.location.href='/mahasiswa/hapus-berkas-mhs?id_pengajuan={id}'"  class="btn btn-danger"><i class="fas fa-trash"></i></button>
								</td>
								""".format(id = item['id_pengajuan'])


					status_list += f"""
						<tr>
							<td>{item['id_pengajuan']}</td>
							<td>{item['nama_program']}</td>
							""" + persetujuan + berkas + """
							<td>
								<button type="button" onclick="window.location.href='/mahasiswa/status-mbkm-mhs-detail?id_pengajuan={id}'" class="btn btn-primary"><i class="fas fa-eye"></i></button>
								<button type="button" onclick="window.location.href='/mahasiswa/hapus-pengajuan-mhs?id_pengajuan={id}'" class="btn btn-danger"><i class="fas fa-trash"></i></button>
							</td>
						</tr>
						""".format(id = item['id_pengajuan'])

			return render_template('mahasiswa/status-mbkm-mhs.html', full_name=full_name, status_list=status_list)
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/mahasiswa/status-mbkm-mhs-detail', methods=['GET'])
def status_mbkm_mhs_detail():
	if 'id_pengajuan' in request.args and session['nomor_induk'] in request.args.get('id_pengajuan'):
		if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
			if session['role'] == 'Mahasiswa':
				idPengajuan = request.args.get('id_pengajuan')
				nama_lengkap = session['fullname']
				nomor_induk = session['nomor_induk']
				program_studi_kode = ""
				program_studi = ""
				tahun_angkatan = ""
				nama_mbkm = ""
				jenis_mbkm = ""
				tempat_mbkm = ""
				semester_mbkm = ""
				link_bukti =""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				sks_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_pengajuan_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				pengajuan_result = cursor.fetchone()
				if pengajuan_result:
					program_studi_kode = pengajuan_result['kode_prodi']
					tahun_angkatan = pengajuan_result['angkatan']
					nama_mbkm = pengajuan_result['nama_program']
					jenis_mbkm = pengajuan_result['jenis_program']
					tempat_mbkm = pengajuan_result['tempat_program']
					link_bukti = pengajuan_result['bukti_program']
					semester_mbkm = pengajuan_result['semester_klaim']

				cursor.execute("SELECT nama_prodi,jenjang from tbl_prodi_if where kode_prodi=%s", [program_studi_kode])
				prodi_result = cursor.fetchone()
				if prodi_result:
					program_studi = program_studi_kode + ' - ' + prodi_result['jenjang'] + ' ' + prodi_result['nama_prodi']

				cursor.execute("SELECT * from tbl_matkul_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				matkul_result = cursor.fetchone()
				if matkul_result:
					for i in range (1,9):
						kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
						nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']
						sks_matkul[j] = mat_result['jumlah_sks']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				return render_template('mahasiswa/status-mbkm-mhs-detail.html', nama_lengkap=nama_lengkap, id_pengajuan=idPengajuan, nomor_induk=nomor_induk, program_studi=program_studi, tahun_angkatan=tahun_angkatan, nama_mbkm=nama_mbkm, jenis_mbkm=jenis_mbkm, tempat_mbkm=tempat_mbkm, link_bukti=link_bukti, semester_mbkm=semester_mbkm, \
				nama_matkul1=nama_matkul[0], dosen_matkul1=dosen_matkul[0], sks_matkul1=sks_matkul[0], nama_matkul2=nama_matkul[1], dosen_matkul2=dosen_matkul[1], sks_matkul2=sks_matkul[1], nama_matkul3=nama_matkul[2], dosen_matkul3=dosen_matkul[2], sks_matkul3=sks_matkul[2], nama_matkul4=nama_matkul[3], dosen_matkul4=dosen_matkul[3], sks_matkul4=sks_matkul[3], \
				nama_matkul5=nama_matkul[4], dosen_matkul5=dosen_matkul[4], sks_matkul5=sks_matkul[4], nama_matkul6=nama_matkul[5], dosen_matkul6=dosen_matkul[5], sks_matkul6=sks_matkul[5], nama_matkul7=nama_matkul[6], dosen_matkul7=dosen_matkul[6], sks_matkul7=sks_matkul[6], nama_matkul8=nama_matkul[7], dosen_matkul8=dosen_matkul[7], sks_matkul8=sks_matkul[7])
			else:
				return redirect('/')
		else:
			return redirect('/login')
	else:
		return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

@app.route('/mahasiswa/lihat-berkas-mhs', methods=['GET'])
def lihat_berkas_mhs():
	if 'id_pengajuan' in request.args and session['nomor_induk'] in request.args.get('id_pengajuan'):
		if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
			if session['role'] == 'Mahasiswa':
				full_name = session['fullname']
				id_pengajuan = request.args.get('id_pengajuan')
				link_sertifikat = ""
				link_laporan = ""
				link_hasil = ""
				tanggal_mulai =""
				tanggal_selesai = ""
				link_dokumentasi = ""

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_berkas_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
				berkas_result = cursor.fetchone()
				if berkas_result:
					link_sertifikat = berkas_result['sertifikat_program']
					link_laporan = berkas_result['laporan_program']
					link_hasil = berkas_result['hasil_program']
					tanggal_mulai = berkas_result['tanggal_mulai_program'].strftime("%d-%m-%Y")
					tanggal_selesai = berkas_result['tanggal_selesai_program'].strftime("%d-%m-%Y")
					link_dokumentasi = berkas_result['dokumentasi_program']
				return render_template('mahasiswa/lihat-berkas-mhs.html', full_name=full_name, id_pengajuan=id_pengajuan, link_sertifikat=link_sertifikat, link_laporan=link_laporan, link_hasil=link_hasil, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai, link_dokumentasi=link_dokumentasi)
			else:
				return redirect('/')
		else:
			return redirect('/login')
	else:
		return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

@app.route('/mahasiswa/jadwal-asesmen-mhs', methods=['GET'])
def jadwal_asesmen_mhs():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			full_name = session['fullname']
			nomor_induk = session['nomor_induk']
			list_asesmen = ""
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * from tbl_kegiatan_assesmen WHERE id_assesmen LIKE %s", [f"{nomor_induk}%"])
			daftar_asesmen = cursor.fetchall()
			for item in daftar_asesmen:
				list_asesmen += f"""
							<tr>
								<td>{item['id_assesmen']}</td>
								<td>{item['id_pengajuan']}</td>
								<td>{item['waktu']}</td>
								<td>{item['tempat_link']}</td>
							"""
				if item['status_assesmen'] == "Belum Selesai":
					list_asesmen += """
								<td class="text text-warning">✕ Belum Selesai</td>
							</tr>
							"""
				else:
					list_asesmen += f"""
								<td><button type='button' onclick="window.location.href='/mahasiswa/hasil-asesmen-mhs?id_asesmen={item['id_assesmen']}'" class='btn btn-primary'><i class='fas fa-eye'></i></button></td>
							</tr>
							"""

			return render_template('/mahasiswa/jadwal-asesmen-mhs.html', full_name=full_name, list_asesmen=list_asesmen)

		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/mahasiswa/hasil-asesmen-mhs', methods=['GET'])
def hasil_asesmen_mhs():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			if 'id_asesmen' in request.args and session['nomor_induk'] in request.args.get('id_asesmen'):
				full_name = session['fullname']
				id_asesmen = request.args.get('id_asesmen')
				id_pengajuan = ""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nilai_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute ("SELECT tbl_kegiatan_assesmen.id_pengajuan, tbl_form_assesmen.* from tbl_kegiatan_assesmen INNER JOIN tbl_form_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_form_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [id_asesmen])
				hasil_detail = cursor.fetchone()
				if hasil_detail:
					id_pengajuan = hasil_detail['id_pengajuan']
					cursor.execute("SELECT * from tbl_matkul_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
					matkul_result = cursor.fetchone()
					if matkul_result:
						for i in range (1,9):
							kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
							nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				for l in range (len(kode_matkul)):
					cursor.execute("SELECT * from tbl_form_assesmen where id_assesmen=%s", [id_asesmen])
					nilai_result = cursor.fetchone()
					if nilai_result:
						if nilai_result['nilai_matkul_' + str(l+1)] is not None:
							nilai_matkul[l] = nilai_result['nilai_matkul_' + str(l+1)]

				return render_template('mahasiswa/hasil-asesmen-mhs.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, namaMatkul1=nama_matkul[0], dosenMatkul1=dosen_matkul[0], nilaiMatkul1=nilai_matkul[0], namaMatkul2=nama_matkul[1], dosenMatkul2=dosen_matkul[1], nilaiMatkul2=nilai_matkul[1], \
				namaMatkul3=nama_matkul[2], dosenMatkul3=dosen_matkul[2], nilaiMatkul3=nilai_matkul[2], namaMatkul4=nama_matkul[3], dosenMatkul4=dosen_matkul[3], nilaiMatkul4=nilai_matkul[3], namaMatkul5=nama_matkul[4], dosenMatkul5=dosen_matkul[4], nilaiMatkul5=nilai_matkul[4], \
				namaMatkul6=nama_matkul[5], dosenMatkul6=dosen_matkul[5], nilaiMatkul6=nilai_matkul[5], namaMatkul7=nama_matkul[6], dosenMatkul7=dosen_matkul[6], nilaiMatkul7=nilai_matkul[6], namaMatkul8=nama_matkul[7], dosenMatkul8=dosen_matkul[7], nilaiMatkul8=nilai_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/mahasiswa/jadwal-asesmen-mhs';</script>"
		else:
			return redirect('/login')
	else:
		return redirect('/')

@app.route('/mahasiswa/unggah-berkas-mhs', methods=['GET'])
def unggah_berkas_mhs():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			full_name = session['fullname']
			if request.method == 'GET' and 'id_pengajuan' in request.args and session['nomor_induk'] in request.args.get('id_pengajuan'):
				id_pengajuan = request.args.get('id_pengajuan')
				return render_template('mahasiswa/unggah-berkas-mhs.html', full_name=full_name, nomor_pengajuan=id_pengajuan)

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"
		else:
			return redirect ('/')
	else:
		return redirect ('/logout')

@app.route('/mahasiswa/tambah-berkas-pengajuan', methods=['POST'])
def tambah_berkas_mhs():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa':
			if request.method == 'POST' and all(i in request.form for i in ('idPengajuan','MBKMstart','MBKMfinish')) and all (j in request.files for j in ('sertifikatMBKM','laporanMBKM','hasilMBKM','dokumentasiMBKM')):
				id_pengajuan = request.form['idPengajuan']
				tanggal_mulai = request.form['MBKMstart']
				tanggal_selesai = request.form['MBKMfinish']
				sertifikat = request.files['sertifikatMBKM']
				link_sertifikat = ''
				laporan = request.files['laporanMBKM']
				link_laporan = ''
				hasil = request.files['hasilMBKM']
				link_hasil = ''
				dokumentasi = request.files['dokumentasiMBKM']
				link_dokumentasi = ''

				if sertifikat.filename == '' or laporan.filename == '' or hasil.filename == '' or dokumentasi.filename == '':
					return "<script>alert('Harap Isi Semua Bagian Formulir!'); window.location.href='/mahasiswa/unggah-berkas-mhs'</script>"

				if (sertifikat and allowed_file(sertifikat.filename)) and (laporan and allowed_file(laporan.filename)) and (hasil and allowed_file(hasil.filename)) and (dokumentasi and allowed_file(dokumentasi.filename)):
					try:
						sertifikat_newname = secure_filename(id_pengajuan + '-sertifikatMBKM.' + sertifikat.filename.rsplit('.', 1)[1].lower())
						laporan_newname = secure_filename(id_pengajuan + '-laporanMBKM.' + laporan.filename.rsplit('.', 1)[1].lower())
						hasil_newname = secure_filename(id_pengajuan + '-hasilMBKM.' + hasil.filename.rsplit('.', 1)[1].lower())
						dokumentasi_newname = secure_filename(id_pengajuan + '-dokumentasiMBKM.' + dokumentasi.filename.rsplit('.', 1)[1].lower())

						sertifikat.save(os.path.join(app.config['UPLOAD_FOLDER'], sertifikat_newname))
						laporan.save(os.path.join(app.config['UPLOAD_FOLDER'], laporan_newname))
						dokumentasi.save(os.path.join(app.config['UPLOAD_FOLDER'], dokumentasi_newname))
						hasil.save(os.path.join(app.config['UPLOAD_FOLDER'], hasil_newname))

						link_sertifikat = request.base_url.replace('/mahasiswa/tambah-berkas-pengajuan', '/uploads/' + sertifikat_newname)
						link_laporan = request.base_url.replace('/mahasiswa/tambah-berkas-pengajuan', '/uploads/' + laporan_newname)
						link_hasil = request.base_url.replace('/mahasiswa/tambah-berkas-pengajuan', '/uploads/' + hasil_newname)
						link_dokumentasi = request.base_url.replace('/mahasiswa/tambah-berkas-pengajuan', '/uploads/' + dokumentasi_newname)

						connection = mysql.connection
						cursor = connection.cursor()
						sql_command = "INSERT INTO tbl_berkas_mbkm (id_pengajuan, sertifikat_program, laporan_program, hasil_program, tanggal_mulai_program, tanggal_selesai_program, dokumentasi_program, status_berkas) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
						data_command =  (id_pengajuan, link_sertifikat, link_laporan, link_hasil, reverse_date_string(tanggal_mulai), reverse_date_string(tanggal_selesai), link_dokumentasi, 'Dikumpulkan')
						cursor.execute(sql_command, data_command)
						connection.commit()

						return "<script>alert('Unggah Berkas Berhasil!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

					except Exception:
							return "<script>alert('Unggah Berkas Gagal!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"
				else:
						return "<script>alert('Harap Isi Semua Bagian Formulir!'); window.location.href='/mahasiswa/unggah-berkas-mhs'</script>"
			else:
				return "<script>alert('Unggah Berkas Gagal!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"
		else:
			return redirect ('/')
	else:
		return redirect ('/logout')

@app.route('/sekjur/index-sekjur' , methods=['GET'])
def index_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			nomor_induk = session['nomor_induk']
			full_name = session['fullname']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
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

@app.route('/sekjur/daftar-pengajuan-mbkm', methods=['GET'])
def daftar_pengajuan_mbkm():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			full_name = session['fullname']
			list_pengajuan = ''
			cursor = cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT tbl_pengajuan_mbkm.id_pengajuan, tbl_pengajuan_mbkm.status_pengajuan, tbl_user.nama from tbl_pengajuan_mbkm INNER JOIN tbl_user ON tbl_pengajuan_mbkm.nomor_induk_mahasiswa=tbl_user.nomor_induk")
			bulk_pengajuan = cursor.fetchall()
			for item in bulk_pengajuan:
				status_pengajuan = ""
				if item['status_pengajuan'] == 'Waiting':
					status_pengajuan = f"""
								<td>
									<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/terima-pengajuan?id_pengajuan={item['id_pengajuan']}'"><i class="fas fa-check"></i> Setuju</button>
									<button type="button" class="btn btn-danger" onclick="window.location.href='/sekjur/tolak-pengajuan?id_pengajuan={item['id_pengajuan']}'"><i class="fas fa-times"></i> Tolak</button>
								</td>
								<td>
									<p class='text text-warning'>🕐 Menunggu Persetujuan</p>
								</td>
								"""
				elif item['status_pengajuan'] == 'Rejected':
					status_pengajuan = """
								<td>
									<p class='text text-danger'>✕ Pengajuan Ditolak</p>
								</td>
								<td>
									<p class='text text-danger'>✕ Pengajuan Ditolak</p>
								</td>
								"""
				else:
					cursor.execute("SELECT * from tbl_berkas_mbkm WHERE id_pengajuan=%s", [item['id_pengajuan']])
					data_berkas = cursor.fetchone()
					if data_berkas:
						status_pengajuan = f"""
								<td>
									<p class='text text-success'>✓ Pengajuan Disetujui</p>
								</td>
								<td>
									<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/lihat-berkas-sekjur?id_pengajuan={item['id_pengajuan']}'"><i class="fas fa-eye"></i></button>
									<button type="button" class="btn btn-danger" onclick="window.location.href='/sekjur/hapus-berkas-sekjur?id_pengajuan={item['id_pengajuan']}'"><i class="fas fa-trash"></i></button>
								</td>
								"""
					else:
						status_pengajuan = f"""
								<td>
									<p class='text text-success'>✓ Pengajuan Disetujui</p>
								</td>
								<td>
									<p class='text text-warning'>🕐 Menunggu Berkas</p>
								</td>
								"""

				list_pengajuan += f"""
							<tr>
								<td>{item['id_pengajuan']}</td>
								<td>{item['nama']}</td>
								{status_pengajuan}
								<td>
									<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/lihat-pengajuan-sekjur?id_pengajuan={item['id_pengajuan']}'"><i class="fas fa-eye"></i></button>
									<button type="button" class="btn btn-danger" onclick="window.location.href='/sekjur/hapus-pengajuan-sekjur?id_pengajuan={item['id_pengajuan']}'"><i class="fas fa-trash"></i></button>
								</td>
							</tr>
								"""
			return render_template ('sekjur/daftar-pengajuan-mbkm.html', full_name=full_name, list_pengajuan=list_pengajuan)
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/lihat-berkas-sekjur')
def lihat_berkas_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				full_name = session['fullname']
				id_pengajuan = request.args.get('id_pengajuan')
				link_sertifikat = ""
				link_laporan = ""
				link_hasil = ""
				tanggal_mulai =""
				tanggal_selesai = ""
				link_dokumentasi = ""

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_berkas_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
				berkas_result = cursor.fetchone()
				if berkas_result:
					link_sertifikat = berkas_result['sertifikat_program']
					link_laporan = berkas_result['laporan_program']
					link_hasil = berkas_result['hasil_program']
					tanggal_mulai = berkas_result['tanggal_mulai_program'].strftime("%d-%m-%Y")
					tanggal_selesai = berkas_result['tanggal_selesai_program'].strftime("%d-%m-%Y")
					link_dokumentasi = berkas_result['dokumentasi_program']
				return render_template('sekjur/lihat-berkas-sekjur.html', full_name=full_name, id_pengajuan=id_pengajuan, link_sertifikat=link_sertifikat, link_laporan=link_laporan, link_hasil=link_hasil, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai, link_dokumentasi=link_dokumentasi)
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/lihat-pengajuan-sekjur',methods=['GET'])
def lihat_pengajuan_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				idPengajuan = request.args.get('id_pengajuan')
				full_name = session['fullname']
				nama_lengkap_mhs = ""
				nomor_induk_mhs = ""
				program_studi_kode = ""
				program_studi = ""
				tahun_angkatan = ""
				nama_mbkm = ""
				jenis_mbkm = ""
				tempat_mbkm = ""
				semester_mbkm = ""
				link_bukti =""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				sks_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_pengajuan_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				pengajuan_result = cursor.fetchone()
				if pengajuan_result:
					nomor_induk_mhs = pengajuan_result['nomor_induk_mahasiswa']
					program_studi_kode = pengajuan_result['kode_prodi']
					tahun_angkatan = pengajuan_result['angkatan']
					nama_mbkm = pengajuan_result['nama_program']
					jenis_mbkm = pengajuan_result['jenis_program']
					tempat_mbkm = pengajuan_result['tempat_program']
					link_bukti = pengajuan_result['bukti_program']
					semester_mbkm = pengajuan_result['semester_klaim']

				cursor.execute("SELECT nama from tbl_user where nomor_induk=%s", [nomor_induk_mhs])
				user_result = cursor.fetchone()
				if user_result:
					nama_lengkap_mhs = user_result['nama']

				cursor.execute("SELECT nama_prodi,jenjang from tbl_prodi_if where kode_prodi=%s", [program_studi_kode])
				prodi_result = cursor.fetchone()
				if prodi_result:
					program_studi = program_studi_kode + ' - ' + prodi_result['jenjang'] + ' ' + prodi_result['nama_prodi']

				cursor.execute("SELECT * from tbl_matkul_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				matkul_result = cursor.fetchone()
				if matkul_result:
					for i in range (1,9):
						kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
						nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']
						sks_matkul[j] = mat_result['jumlah_sks']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				return render_template('sekjur/lihat-pengajuan-sekjur.html', full_name=full_name, id_pengajuan=idPengajuan, nama_lengkap_mhs=nama_lengkap_mhs, nomor_induk_mhs=nomor_induk_mhs, program_studi=program_studi, tahun_angkatan=tahun_angkatan, nama_mbkm=nama_mbkm, jenis_mbkm=jenis_mbkm, tempat_mbkm=tempat_mbkm, link_bukti=link_bukti, semester_mbkm=semester_mbkm, \
				nama_matkul1=nama_matkul[0], dosen_matkul1=dosen_matkul[0], sks_matkul1=sks_matkul[0], nama_matkul2=nama_matkul[1], dosen_matkul2=dosen_matkul[1], sks_matkul2=sks_matkul[1], nama_matkul3=nama_matkul[2], dosen_matkul3=dosen_matkul[2], sks_matkul3=sks_matkul[2], nama_matkul4=nama_matkul[3], dosen_matkul4=dosen_matkul[3], sks_matkul4=sks_matkul[3], \
				nama_matkul5=nama_matkul[4], dosen_matkul5=dosen_matkul[4], sks_matkul5=sks_matkul[4], nama_matkul6=nama_matkul[5], dosen_matkul6=dosen_matkul[5], sks_matkul6=sks_matkul[5], nama_matkul7=nama_matkul[6], dosen_matkul7=dosen_matkul[6], sks_matkul7=sks_matkul[6], nama_matkul8=nama_matkul[7], dosen_matkul8=dosen_matkul[7], sks_matkul8=sks_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/jadwal-asesmen-sekjur', methods=['GET'])
def jadwal_asesmen_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			full_name = session['fullname']
			list_asesmen = ""
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * from tbl_kegiatan_assesmen")
			bulk_asesmen = cursor.fetchall()
			for item in bulk_asesmen:
				status_asesmen = ""
				aksi = ""
				if item['status_assesmen'] == 'Belum Selesai':
					status_asesmen = f"""
								<td>
                      				<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/proses-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-calendar-check"></i> Proses</button>
                    			</td>
								"""
					aksi = f"""
						<td>
								<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/lihat-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-eye"></i></button>
                      			<button type="button" class="btn btn-warning" onclick="window.location.href='/sekjur/ubah-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-edit"></i></button>
                      			<button type="button" class="btn btn-danger" onclick="window.location.href='/sekjur/hapus-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-trash"></i></button>
						</td>
						"""

				else:
					status_asesmen = f"""
								<td>
                      				<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/hasil-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-eye"></i></button>
									<button type="button" class="btn btn-warning" onclick="window.location.href='/sekjur/ubah-hasil-asesmen?id_asesmen={item['id_assesmen']}'"><i class="fas fa-edit"></i></button>
									<button type="button" class="btn btn-danger" onclick="window.location.href='/sekjur/hapus-hasil-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-trash"></i></button>
                    			</td>
								"""
					aksi = f"""
						<td>
								<button type="button" class="btn btn-primary" onclick="window.location.href='/sekjur/lihat-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-eye"></i></button>
                      			<button type="button" class="btn btn-danger" onclick="window.location.href='/sekjur/hapus-asesmen-sekjur?id_asesmen={item['id_assesmen']}'"><i class="fas fa-trash"></i></button>
						</td>
						"""

				list_asesmen += f"""
						<tr>
							<td>{item['id_assesmen']}</td>
							<td>{item['id_pengajuan']}</td>
							<td>{item['waktu']}</td>
							<td>{item['tempat_link']}</td>
							{status_asesmen}
							{aksi}
						</tr>
						"""
			return render_template('sekjur/jadwal-asesmen-sekjur.html', full_name=full_name, list_asesmen=list_asesmen)
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/buat-asesmen-sekjur' ,methods=['GET','POST'])
def buat_asesmen_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' :
				full_name = session['fullname']
				list_pengajuan = ''
				list_mahasiswa = ''
				list_kajur = ''
				list_kaprodi = ''
				list_dosen = ''

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT id_pengajuan from tbl_pengajuan_mbkm")
				bulk_pengajuan = cursor.fetchall()
				for item in bulk_pengajuan :
					list_pengajuan += f"<option value='{item['id_pengajuan']}'>{item['id_pengajuan']}</option>"

				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE role=%s", ['Mahasiswa'])
				bulk_mhs = cursor.fetchall()
				for item in bulk_mhs :
					list_mahasiswa += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE role=%s", ['Ketua Jurusan'])
				bulk_kajur = cursor.fetchall()
				for item in bulk_kajur :
					list_kajur += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE role=%s", ['Kepala Prodi'])
				bulk_kaprodi = cursor.fetchall()
				for item in bulk_kaprodi :
					list_kaprodi += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE NOT role=%s", ['Mahasiswa'])
				bulk_dosen = cursor.fetchall()
				for item in bulk_dosen :
					list_dosen += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				return render_template('sekjur/buat-asesmen-sekjur.html', full_name=full_name, list_pengajuan=list_pengajuan, list_mahasiswa=list_mahasiswa, list_kajur=list_kajur, list_kaprodi=list_kaprodi, list_dosen=list_dosen)

			else:
				if all(i in request.form for i in ('idPengajuan','timeAsesmen', 'tempatLink', 'mahasiswa', 'dosen_wali', 'kajur', 'kaprodi', 'dosen1')) :
					lookup_cursor = cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
					lookup_cursor.execute("SELECT * from tbl_berkas_mbkm where id_pengajuan=%s", [request.form['idPengajuan']])
					berkas_status = lookup_cursor.fetchone()
					if berkas_status:
						try:
							full_name = session['fullname']
							id_pengajuan = request.form['idPengajuan']
							waktu_asesmen = request.form['timeAsesmen']
							tempat_link = request.form['tempatLink']
							mahasiswa = request.form['mahasiswa']
							dosen_wali = request.form['dosen_wali']
							kajur = request.form['kajur']
							kaprodi = request.form['kaprodi']
							dosen1 = request.form['dosen1']
							dosen2 = request.form['dosen2'] if 'dosen2' in request.form else None
							dosen3 = request.form['dosen2'] if 'dosen3' in request.form else None
							dosen4 = request.form['dosen2'] if 'dosen4' in request.form else None
							dosen5 = request.form['dosen2'] if 'dosen5' in request.form else None
							dosen6 = request.form['dosen2'] if 'dosen6' in request.form else None
							dosen7 = request.form['dosen2'] if 'dosen7' in request.form else None
							dosen8 = request.form['dosen2'] if 'dosen8' in request.form else None

							asesmen_time = waktu_asesmen.split(' ')
							new_asesmen_time = reverse_date_string(asesmen_time[0]) + ' ' + asesmen_time[1]

							joined_asesmen_date = ''.join((asesmen_time[0]).split('-'))
							id_asesmen = generate_asesmen_id(id_pengajuan, joined_asesmen_date)

							connection = mysql.connection
							cursor = connection.cursor()
							cursor.execute("INSERT INTO tbl_kegiatan_assesmen VALUES (%s, %s, %s, %s, %s)", (id_asesmen, id_pengajuan, new_asesmen_time, tempat_link, 'Belum Selesai'))
							cursor.execute("INSERT INTO tbl_peserta_assesmen VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_asesmen, mahasiswa, dosen_wali, kaprodi, kajur, dosen1, dosen2, dosen3, dosen4, dosen5, dosen6, dosen7, dosen8))
							connection.commit()

							return "<script>alert('Buat Jadwal Asesmen Berhasil!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"

						except Exception :
							return "<script>alert('Buat Jadwal Asesmen Gagal!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
					else:
						return "<script>alert('Buat Jadwal Asesmen Gagal! Berkas Pengajuan Belum Ada!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
				else:
					return "<script>alert('Harap Isi Semua Data Formulir dan Dosen Minimal 1!'); window.location.href='/sekjur/buat-asesmen-sekjur'</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/ubah-asesmen-sekjur', methods=['GET'])
def ubah_asesmen_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				id_asesmen = request.args.get('id_asesmen')
				full_name = session['fullname']
				list_kajur = ''
				list_kaprodi = ''
				list_dosen = ''

				idPengajuan = ''
				waktu_asesmen = ''
				tempat_link = ''

				nomor_mahasiswa = ''
				mahasiswa = ''
				nomor_dosen_wali = ''
				nomor_kajur = ''
				nomor_kaprodi = ''
				nomor_dosen = ['','','','','','','','']
				onload_script = ''

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE role=%s", ['Ketua Jurusan'])
				bulk_kajur = cursor.fetchall()
				for item in bulk_kajur :
					list_kajur += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE role=%s", ['Kepala Prodi'])
				bulk_kaprodi = cursor.fetchall()
				for item in bulk_kaprodi :
					list_kaprodi += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				cursor.execute("SELECT nomor_induk, nama from tbl_user WHERE NOT role=%s", ['Mahasiswa'])
				bulk_dosen = cursor.fetchall()
				for item in bulk_dosen :
					list_dosen += f"<option value='{item['nomor_induk']}'>{item['nomor_induk'] + ' - ' + item['nama']}</option>"

				cursor.execute("SELECT * from tbl_kegiatan_assesmen INNER JOIN tbl_peserta_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_peserta_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [request.args.get('id_asesmen')])
				asesmen_detail = cursor.fetchone()
				if asesmen_detail :
					idPengajuan = asesmen_detail['id_pengajuan']
					waktu_asesmen = asesmen_detail['waktu'].strftime('%d-%m-%Y %H:%M')
					tempat_link = asesmen_detail['tempat_link']
					nomor_mahasiswa = asesmen_detail['nomor_mahasiswa']
					nomor_dosen_wali = asesmen_detail['nomor_dosen_wali']
					nomor_kajur = asesmen_detail['nomor_ketua_jurusan']
					nomor_kaprodi = asesmen_detail['nomor_kepala_prodi']
					for i in range (1,9):
						if asesmen_detail[f'nomor_dosen_{i}'] :
							nomor_dosen[i-1] = asesmen_detail[f'nomor_dosen_{i}']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_mahasiswa])
					mhs_detail = cursor.fetchone()
					if mhs_detail:
						mahasiswa = nomor_mahasiswa + ' - ' + mhs_detail['nama']

					onload_script = f"""
							<script>
								selectElement('dosen_wali','{nomor_dosen_wali}');
								selectElement('kaprodi','{nomor_kaprodi}');
								selectElement('kajur','{nomor_kajur}');
								selectElement('dosen1','{nomor_dosen[0]}');
								selectElement('dosen2','{nomor_dosen[1]}');
								selectElement('dosen3','{nomor_dosen[2]}');
								selectElement('dosen4','{nomor_dosen[3]}');
								selectElement('dosen5','{nomor_dosen[4]}');
								selectElement('dosen6','{nomor_dosen[5]}');
								selectElement('dosen7','{nomor_dosen[6]}');
								selectElement('dosen8','{nomor_dosen[7]}');
							</script>
							"""

					return render_template('sekjur/ubah-asesmen-sekjur.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=idPengajuan, waktu_asesmen=waktu_asesmen, tempat_link=tempat_link, \
					mahasiswa=mahasiswa, list_kajur=list_kajur, list_kaprodi=list_kaprodi, list_dosen=list_dosen, onload_script=onload_script)
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/sekjur/jadwal-asesmen-sekjur';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/lihat-asesmen-sekjur', methods=['GET'])
def lihat_asesmen_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				full_name = session['fullname']
				idAsesmen = request.args.get('id_asesmen')
				idPengajuan = ''
				waktu_asesmen = ''
				tempat_link = ''

				nomor_mahasiswa = ''
				mahasiswa = ''
				nomor_dosen_wali = ''
				dosen_wali = ''
				nomor_kajur = ''
				kajur = ''
				nomor_kaprodi = ''
				kaprodi = ''
				nomor_dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']
				dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_kegiatan_assesmen INNER JOIN tbl_peserta_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_peserta_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [request.args.get('id_asesmen')])
				asesmen_detail = cursor.fetchone()
				if asesmen_detail :
					idPengajuan = asesmen_detail['id_pengajuan']
					waktu_asesmen = asesmen_detail['waktu'].strftime('%d-%m-%Y %H:%M')
					tempat_link = asesmen_detail['tempat_link']
					nomor_mahasiswa = asesmen_detail['nomor_mahasiswa']
					nomor_dosen_wali = asesmen_detail['nomor_dosen_wali']
					nomor_kajur = asesmen_detail['nomor_ketua_jurusan']
					nomor_kaprodi = asesmen_detail['nomor_kepala_prodi']
					for i in range (1,9):
						if asesmen_detail[f'nomor_dosen_{i}'] :
							nomor_dosen[i-1] = asesmen_detail[f'nomor_dosen_{i}']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_mahasiswa])
					mhs_detail = cursor.fetchone()
					if mhs_detail:
						mahasiswa = nomor_mahasiswa + ' - ' + mhs_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen_wali])
					wali_detail = cursor.fetchone()
					if wali_detail:
						dosen_wali = nomor_dosen_wali + ' - ' +  wali_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kajur])
					kajur_detail = cursor.fetchone()
					if kajur_detail:
						kajur = nomor_kajur + ' - ' +  kajur_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kaprodi])
					kaprodi_detail = cursor.fetchone()
					if kaprodi_detail:
						kaprodi = nomor_kaprodi + ' - ' +  kaprodi_detail['nama']

					for j in range (len(nomor_dosen)) :
						cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen[j]])
						dosen_detail = cursor.fetchone()
						if dosen_detail:
							dosen[j] = nomor_dosen[j] + ' - ' + dosen_detail['nama']

					return render_template('sekjur/lihat-asesmen-sekjur.html', full_name=full_name, id_asesmen=idAsesmen, id_pengajuan=idPengajuan, waktu_asesmen=waktu_asesmen, tempat_link=tempat_link, \
					mahasiswa=mahasiswa, dosen_wali=dosen_wali, kajur=kajur, kaprodi=kaprodi, dosen1=dosen[0], dosen2=dosen[1], dosen3=dosen[2], dosen4=dosen[3], dosen5=dosen[4], \
					dosen6=dosen[5], dosen7=dosen[6], dosen8=dosen[7])
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/sekjur/jadwal-asesmen-sekjur';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/proses-asesmen-sekjur')
def proses_asesmen_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				id_asesmen = request.args.get('id_asesmen')
				full_name = session['fullname']
				id_pengajuan = id_asesmen.split('-')[0] + '-' + id_asesmen.split('-')[1]
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_matkul_mbkm where id_pengajuan=%s", [id_pengajuan])
				matkul_result = cursor.fetchone()
				if matkul_result:
					for i in range (1,9):
						kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
						nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				return render_template('sekjur/proses-asesmen-sekjur.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, matkul1=nama_matkul[0], matkul2=nama_matkul[1], matkul3=nama_matkul[2], matkul4=nama_matkul[3], \
				matkul5=nama_matkul[4], matkul6=nama_matkul[5], matkul7=nama_matkul[6], matkul8=nama_matkul[7], dosen1=dosen_matkul[0], dosen2=dosen_matkul[1], dosen3=dosen_matkul[2], dosen4=dosen_matkul[3], dosen5=dosen_matkul[4], \
				dosen6=dosen_matkul[5], dosen7=dosen_matkul[6], dosen8=dosen_matkul[7])
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/sekjur/jadwal-asesmen-sekjur';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/dosen/index-dosen', methods=['GET'])
def index_dosen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Dosen':
			full_name = session['fullname']
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
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

@app.route('/dosen/jadwal-asesmen-dosen',methods=['GET'])
def jadwal_asesmen_dosen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Dosen':
			if request.method == 'GET':
				full_name = session['fullname']
				nomor_induk = session['nomor_induk']
				list_asesmen = ""
				
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT id_assesmen from tbl_peserta_assesmen WHERE nomor_dosen_wali=%s OR nomor_dosen_1=%s OR nomor_dosen_2=%s OR nomor_dosen_3=%s OR nomor_dosen_4=%s OR nomor_dosen_5=%s OR nomor_dosen_6=%s OR nomor_dosen_7=%s OR nomor_dosen_8=%s", (nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk))
				bulk_asesmen = cursor.fetchall()
				for item in bulk_asesmen:
					cursor.execute("SELECT * from tbl_kegiatan_assesmen WHERE id_assesmen=%s",[item['id_assesmen']])
					asesmen_detail = cursor.fetchone()
					if asesmen_detail:
						id_pengajuan = asesmen_detail['id_assesmen'].split('-')[0] + '-' + asesmen_detail['id_assesmen'].split('-')[1]
						status_asesmen = ""
						if asesmen_detail['status_assesmen'] == "Belum Selesai" :
							status_asesmen = """
								<td>
									<p class='text text-warning'>✕ Belum Selesai</p>
								</td>
								"""
						else :
							status_asesmen = f"""
								<td>
									<button type="button" onclick="window.location.href='/dosen/hasil-asesmen-dosen?id_asesmen={asesmen_detail['id_assesmen']}'" class='btn btn-primary'><i class='fas fa-eye'></i> Hasil</button>
								</td>
								"""
						
						list_asesmen += f"""
								<tr>
									<td>{asesmen_detail['id_assesmen']}</td>
									<td>{asesmen_detail['waktu']}</td>
									<td>{asesmen_detail['tempat_link']}</td>
									{status_asesmen}
									<td>
										<button type="button" class="btn btn-primary" onclick="window.location.href='/dosen/lihat-pengajuan-dosen?id_pengajuan={id_pengajuan}'"><i class="fas fa-eye"></i> Pengajuan</button>
                      					<button type="button" class="btn btn-primary" onclick="window.location.href='/dosen/lihat-berkas-dosen?id_pengajuan={id_pengajuan}'"><i class="fas fa-eye"></i> Berkas</button>
									</td>
									<td>
										<button type="button" class="btn btn-primary" onclick="window.location.href='/dosen/lihat-asesmen-dosen?id_asesmen={asesmen_detail['id_assesmen']}'"><i class="fas fa-eye"></i></button>
									</td>
								</tr>
								"""
				return render_template("dosen/jadwal-asesmen-dosen.html", full_name=full_name, list_asesmen=list_asesmen)
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/dosen/lihat-pengajuan-dosen')
def lihat_pengajuan_dosen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Dosen':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				idPengajuan = request.args.get('id_pengajuan')
				full_name = session['fullname']
				nama_lengkap_mhs = ""
				nomor_induk_mhs = ""
				program_studi_kode = ""
				program_studi = ""
				tahun_angkatan = ""
				nama_mbkm = ""
				jenis_mbkm = ""
				tempat_mbkm = ""
				semester_mbkm = ""
				link_bukti =""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				sks_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_pengajuan_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				pengajuan_result = cursor.fetchone()
				if pengajuan_result:
					nomor_induk_mhs = pengajuan_result['nomor_induk_mahasiswa']
					program_studi_kode = pengajuan_result['kode_prodi']
					tahun_angkatan = pengajuan_result['angkatan']
					nama_mbkm = pengajuan_result['nama_program']
					jenis_mbkm = pengajuan_result['jenis_program']
					tempat_mbkm = pengajuan_result['tempat_program']
					link_bukti = pengajuan_result['bukti_program']
					semester_mbkm = pengajuan_result['semester_klaim']

				cursor.execute("SELECT nama from tbl_user where nomor_induk=%s", [nomor_induk_mhs])
				user_result = cursor.fetchone()
				if user_result:
					nama_lengkap_mhs = user_result['nama']

				cursor.execute("SELECT nama_prodi,jenjang from tbl_prodi_if where kode_prodi=%s", [program_studi_kode])
				prodi_result = cursor.fetchone()
				if prodi_result:
					program_studi = program_studi_kode + ' - ' + prodi_result['jenjang'] + ' ' + prodi_result['nama_prodi']

				cursor.execute("SELECT * from tbl_matkul_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				matkul_result = cursor.fetchone()
				if matkul_result:
					for i in range (1,9):
						kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
						nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']
						sks_matkul[j] = mat_result['jumlah_sks']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				return render_template('dosen/lihat-pengajuan-dosen.html', full_name=full_name, id_pengajuan=idPengajuan, nama_lengkap_mhs=nama_lengkap_mhs, nomor_induk_mhs=nomor_induk_mhs, program_studi=program_studi, tahun_angkatan=tahun_angkatan, nama_mbkm=nama_mbkm, jenis_mbkm=jenis_mbkm, tempat_mbkm=tempat_mbkm, link_bukti=link_bukti, semester_mbkm=semester_mbkm, \
				nama_matkul1=nama_matkul[0], dosen_matkul1=dosen_matkul[0], sks_matkul1=sks_matkul[0], nama_matkul2=nama_matkul[1], dosen_matkul2=dosen_matkul[1], sks_matkul2=sks_matkul[1], nama_matkul3=nama_matkul[2], dosen_matkul3=dosen_matkul[2], sks_matkul3=sks_matkul[2], nama_matkul4=nama_matkul[3], dosen_matkul4=dosen_matkul[3], sks_matkul4=sks_matkul[3], \
				nama_matkul5=nama_matkul[4], dosen_matkul5=dosen_matkul[4], sks_matkul5=sks_matkul[4], nama_matkul6=nama_matkul[5], dosen_matkul6=dosen_matkul[5], sks_matkul6=sks_matkul[5], nama_matkul7=nama_matkul[6], dosen_matkul7=dosen_matkul[6], sks_matkul7=sks_matkul[6], nama_matkul8=nama_matkul[7], dosen_matkul8=dosen_matkul[7], sks_matkul8=sks_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/dosen/jadwal-asesmen-dosen';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/dosen/lihat-berkas-dosen')
def lihat_berkas_dosen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Dosen':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				full_name = session['fullname']
				id_pengajuan = request.args.get('id_pengajuan')
				link_sertifikat = ""
				link_laporan = ""
				link_hasil = ""
				tanggal_mulai =""
				tanggal_selesai = ""
				link_dokumentasi = ""

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_berkas_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
				berkas_result = cursor.fetchone()
				if berkas_result:
					link_sertifikat = berkas_result['sertifikat_program']
					link_laporan = berkas_result['laporan_program']
					link_hasil = berkas_result['hasil_program']
					tanggal_mulai = berkas_result['tanggal_mulai_program'].strftime("%d-%m-%Y")
					tanggal_selesai = berkas_result['tanggal_selesai_program'].strftime("%d-%m-%Y")
					link_dokumentasi = berkas_result['dokumentasi_program']
				return render_template('dosen/lihat-berkas-dosen.html', full_name=full_name, id_pengajuan=id_pengajuan, link_sertifikat=link_sertifikat, link_laporan=link_laporan, link_hasil=link_hasil, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai, link_dokumentasi=link_dokumentasi)
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/dosen/jadwal-asesmen-dosen';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/dosen/lihat-asesmen-dosen')
def lihat_asesmen_dosen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Dosen':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				full_name = session['fullname']
				idAsesmen = request.args.get('id_asesmen')
				idPengajuan = ''
				waktu_asesmen = ''
				tempat_link = ''

				nomor_mahasiswa = ''
				mahasiswa = ''
				nomor_dosen_wali = ''
				dosen_wali = ''
				nomor_kajur = ''
				kajur = ''
				nomor_kaprodi = ''
				kaprodi = ''
				nomor_dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']
				dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_kegiatan_assesmen INNER JOIN tbl_peserta_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_peserta_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [request.args.get('id_asesmen')])
				asesmen_detail = cursor.fetchone()
				if asesmen_detail :
					idPengajuan = asesmen_detail['id_pengajuan']
					waktu_asesmen = asesmen_detail['waktu'].strftime('%d-%m-%Y %H:%M')
					tempat_link = asesmen_detail['tempat_link']
					nomor_mahasiswa = asesmen_detail['nomor_mahasiswa']
					nomor_dosen_wali = asesmen_detail['nomor_dosen_wali']
					nomor_kajur = asesmen_detail['nomor_ketua_jurusan']
					nomor_kaprodi = asesmen_detail['nomor_kepala_prodi']
					for i in range (1,9):
						if asesmen_detail[f'nomor_dosen_{i}'] :
							nomor_dosen[i-1] = asesmen_detail[f'nomor_dosen_{i}']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_mahasiswa])
					mhs_detail = cursor.fetchone()
					if mhs_detail:
						mahasiswa = nomor_mahasiswa + ' - ' + mhs_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen_wali])
					wali_detail = cursor.fetchone()
					if wali_detail:
						dosen_wali = nomor_dosen_wali + ' - ' +  wali_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kajur])
					kajur_detail = cursor.fetchone()
					if kajur_detail:
						kajur = nomor_kajur + ' - ' +  kajur_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kaprodi])
					kaprodi_detail = cursor.fetchone()
					if kaprodi_detail:
						kaprodi = nomor_kaprodi + ' - ' +  kaprodi_detail['nama']

					for j in range (len(nomor_dosen)) :
						cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen[j]])
						dosen_detail = cursor.fetchone()
						if dosen_detail:
							dosen[j] = nomor_dosen[j] + ' - ' + dosen_detail['nama']

					return render_template('dosen/lihat-asesmen-dosen.html', full_name=full_name, id_asesmen=idAsesmen, id_pengajuan=idPengajuan, waktu_asesmen=waktu_asesmen, tempat_link=tempat_link, \
					mahasiswa=mahasiswa, dosen_wali=dosen_wali, kajur=kajur, kaprodi=kaprodi, dosen1=dosen[0], dosen2=dosen[1], dosen3=dosen[2], dosen4=dosen[3], dosen5=dosen[4], \
					dosen6=dosen[5], dosen7=dosen[6], dosen8=dosen[7])
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/dosen/jadwal-asesmen-dosen';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kaprodi/index-kaprodi',methods=['GET'])
def index_kaprodi():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Kepala Prodi':
			full_name = session['fullname']
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
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
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Kepala Prodi':
			if request.method == 'GET':
				full_name = session['fullname']
				nomor_induk = session['nomor_induk']
				list_asesmen = ""
				
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT id_assesmen from tbl_peserta_assesmen WHERE nomor_kepala_prodi=%s OR nomor_dosen_wali=%s OR nomor_dosen_1=%s OR nomor_dosen_2=%s OR nomor_dosen_3=%s OR nomor_dosen_4=%s OR nomor_dosen_5=%s OR nomor_dosen_6=%s OR nomor_dosen_7=%s OR nomor_dosen_8=%s", (nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk))
				bulk_asesmen = cursor.fetchall()
				for item in bulk_asesmen:
					cursor.execute("SELECT * from tbl_kegiatan_assesmen WHERE id_assesmen=%s",[item['id_assesmen']])
					asesmen_detail = cursor.fetchone()
					if asesmen_detail:
						id_pengajuan = asesmen_detail['id_assesmen'].split('-')[0] + '-' + asesmen_detail['id_assesmen'].split('-')[1]
						status_asesmen = ""
						if asesmen_detail['status_assesmen'] == "Belum Selesai" :
							status_asesmen = """
								<td>
									<p class='text text-warning'>✕ Belum Selesai</p>
								</td>
								"""
						else :
							status_asesmen = f"""
								<td>
									<button type="button" onclick="window.location.href='/kaprodi/hasil-asesmen-kaprodi?id_asesmen={asesmen_detail['id_assesmen']}'" class='btn btn-primary'><i class='fas fa-eye'></i> Hasil</button>
								</td>
								"""
						
						list_asesmen += f"""
								<tr>
									<td>{asesmen_detail['id_assesmen']}</td>
									<td>{asesmen_detail['waktu']}</td>
									<td>{asesmen_detail['tempat_link']}</td>
									{status_asesmen}
									<td>
										<button type="button" class="btn btn-primary" onclick="window.location.href='/kaprodi/lihat-pengajuan-kaprodi?id_pengajuan={id_pengajuan}'"><i class="fas fa-eye"></i> Pengajuan</button>
                      					<button type="button" class="btn btn-primary" onclick="window.location.href='/kaprodi/lihat-berkas-kaprodi?id_pengajuan={id_pengajuan}'"><i class="fas fa-eye"></i> Berkas</button>
									</td>
									<td>
										<button type="button" class="btn btn-primary" onclick="window.location.href='/kaprodi/lihat-asesmen-kaprodi?id_asesmen={asesmen_detail['id_assesmen']}'"><i class="fas fa-eye"></i></button>
									</td>
								</tr>
								"""
				return render_template("kaprodi/jadwal-asesmen-kaprodi.html", full_name=full_name, list_asesmen=list_asesmen)
		else:
			return redirect('/')
	else:
		return redirect('/login')
	

@app.route('/kaprodi/lihat-pengajuan-kaprodi')
def lihat_pengajuan_kaprodi():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Kepala Prodi':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				idPengajuan = request.args.get('id_pengajuan')
				full_name = session['fullname']
				nama_lengkap_mhs = ""
				nomor_induk_mhs = ""
				program_studi_kode = ""
				program_studi = ""
				tahun_angkatan = ""
				nama_mbkm = ""
				jenis_mbkm = ""
				tempat_mbkm = ""
				semester_mbkm = ""
				link_bukti =""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				sks_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_pengajuan_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				pengajuan_result = cursor.fetchone()
				if pengajuan_result:
					nomor_induk_mhs = pengajuan_result['nomor_induk_mahasiswa']
					program_studi_kode = pengajuan_result['kode_prodi']
					tahun_angkatan = pengajuan_result['angkatan']
					nama_mbkm = pengajuan_result['nama_program']
					jenis_mbkm = pengajuan_result['jenis_program']
					tempat_mbkm = pengajuan_result['tempat_program']
					link_bukti = pengajuan_result['bukti_program']
					semester_mbkm = pengajuan_result['semester_klaim']

				cursor.execute("SELECT nama from tbl_user where nomor_induk=%s", [nomor_induk_mhs])
				user_result = cursor.fetchone()
				if user_result:
					nama_lengkap_mhs = user_result['nama']

				cursor.execute("SELECT nama_prodi,jenjang from tbl_prodi_if where kode_prodi=%s", [program_studi_kode])
				prodi_result = cursor.fetchone()
				if prodi_result:
					program_studi = program_studi_kode + ' - ' + prodi_result['jenjang'] + ' ' + prodi_result['nama_prodi']

				cursor.execute("SELECT * from tbl_matkul_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				matkul_result = cursor.fetchone()
				if matkul_result:
					for i in range (1,9):
						kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
						nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']
						sks_matkul[j] = mat_result['jumlah_sks']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				return render_template('kaprodi/lihat-pengajuan-kaprodi.html', full_name=full_name, id_pengajuan=idPengajuan, nama_lengkap_mhs=nama_lengkap_mhs, nomor_induk_mhs=nomor_induk_mhs, program_studi=program_studi, tahun_angkatan=tahun_angkatan, nama_mbkm=nama_mbkm, jenis_mbkm=jenis_mbkm, tempat_mbkm=tempat_mbkm, link_bukti=link_bukti, semester_mbkm=semester_mbkm, \
				nama_matkul1=nama_matkul[0], dosen_matkul1=dosen_matkul[0], sks_matkul1=sks_matkul[0], nama_matkul2=nama_matkul[1], dosen_matkul2=dosen_matkul[1], sks_matkul2=sks_matkul[1], nama_matkul3=nama_matkul[2], dosen_matkul3=dosen_matkul[2], sks_matkul3=sks_matkul[2], nama_matkul4=nama_matkul[3], dosen_matkul4=dosen_matkul[3], sks_matkul4=sks_matkul[3], \
				nama_matkul5=nama_matkul[4], dosen_matkul5=dosen_matkul[4], sks_matkul5=sks_matkul[4], nama_matkul6=nama_matkul[5], dosen_matkul6=dosen_matkul[5], sks_matkul6=sks_matkul[5], nama_matkul7=nama_matkul[6], dosen_matkul7=dosen_matkul[6], sks_matkul7=sks_matkul[6], nama_matkul8=nama_matkul[7], dosen_matkul8=dosen_matkul[7], sks_matkul8=sks_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/kaprodi/jadwal-asesmen-kaprodi';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kaprodi/lihat-berkas-kaprodi')
def lihat_berkas_kaprodi():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Kepala Prodi':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				full_name = session['fullname']
				id_pengajuan = request.args.get('id_pengajuan')
				link_sertifikat = ""
				link_laporan = ""
				link_hasil = ""
				tanggal_mulai =""
				tanggal_selesai = ""
				link_dokumentasi = ""

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_berkas_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
				berkas_result = cursor.fetchone()
				if berkas_result:
					link_sertifikat = berkas_result['sertifikat_program']
					link_laporan = berkas_result['laporan_program']
					link_hasil = berkas_result['hasil_program']
					tanggal_mulai = berkas_result['tanggal_mulai_program'].strftime("%d-%m-%Y")
					tanggal_selesai = berkas_result['tanggal_selesai_program'].strftime("%d-%m-%Y")
					link_dokumentasi = berkas_result['dokumentasi_program']
				return render_template('kaprodi/lihat-berkas-kaprodi.html', full_name=full_name, id_pengajuan=id_pengajuan, link_sertifikat=link_sertifikat, link_laporan=link_laporan, link_hasil=link_hasil, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai, link_dokumentasi=link_dokumentasi)
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/kaprodi/jadwal-asesmen-kaprodi';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kaprodi/lihat-asesmen-kaprodi')
def lihat_asesmen_kaprodi():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Kepala Prodi':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				full_name = session['fullname']
				idAsesmen = request.args.get('id_asesmen')
				idPengajuan = ''
				waktu_asesmen = ''
				tempat_link = ''

				nomor_mahasiswa = ''
				mahasiswa = ''
				nomor_dosen_wali = ''
				dosen_wali = ''
				nomor_kajur = ''
				kajur = ''
				nomor_kaprodi = ''
				kaprodi = ''
				nomor_dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']
				dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_kegiatan_assesmen INNER JOIN tbl_peserta_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_peserta_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [request.args.get('id_asesmen')])
				asesmen_detail = cursor.fetchone()
				if asesmen_detail :
					idPengajuan = asesmen_detail['id_pengajuan']
					waktu_asesmen = asesmen_detail['waktu'].strftime('%d-%m-%Y %H:%M')
					tempat_link = asesmen_detail['tempat_link']
					nomor_mahasiswa = asesmen_detail['nomor_mahasiswa']
					nomor_dosen_wali = asesmen_detail['nomor_dosen_wali']
					nomor_kajur = asesmen_detail['nomor_ketua_jurusan']
					nomor_kaprodi = asesmen_detail['nomor_kepala_prodi']
					for i in range (1,9):
						if asesmen_detail[f'nomor_dosen_{i}'] :
							nomor_dosen[i-1] = asesmen_detail[f'nomor_dosen_{i}']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_mahasiswa])
					mhs_detail = cursor.fetchone()
					if mhs_detail:
						mahasiswa = nomor_mahasiswa + ' - ' + mhs_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen_wali])
					wali_detail = cursor.fetchone()
					if wali_detail:
						dosen_wali = nomor_dosen_wali + ' - ' +  wali_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kajur])
					kajur_detail = cursor.fetchone()
					if kajur_detail:
						kajur = nomor_kajur + ' - ' +  kajur_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kaprodi])
					kaprodi_detail = cursor.fetchone()
					if kaprodi_detail:
						kaprodi = nomor_kaprodi + ' - ' +  kaprodi_detail['nama']

					for j in range (len(nomor_dosen)) :
						cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen[j]])
						dosen_detail = cursor.fetchone()
						if dosen_detail:
							dosen[j] = nomor_dosen[j] + ' - ' + dosen_detail['nama']

					return render_template('kaprodi/lihat-asesmen-kaprodi.html', full_name=full_name, id_asesmen=idAsesmen, id_pengajuan=idPengajuan, waktu_asesmen=waktu_asesmen, tempat_link=tempat_link, \
					mahasiswa=mahasiswa, dosen_wali=dosen_wali, kajur=kajur, kaprodi=kaprodi, dosen1=dosen[0], dosen2=dosen[1], dosen3=dosen[2], dosen4=dosen[3], dosen5=dosen[4], \
					dosen6=dosen[5], dosen7=dosen[6], dosen8=dosen[7])
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/kaprodi/jadwal-asesmen-kaprodi';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kajur/index-kajur',methods=['GET'])
def index_kajur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Ketua Jurusan':
			full_name = session['fullname']
			nomor_induk = session['nomor_induk']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("SELECT * FROM tbl_user where nomor_induk=%s", [nomor_induk])
			account_detail = cursor.fetchone()

			if account_detail:
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
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Ketua Jurusan':
			if request.method == 'GET':
				full_name = session['fullname']
				nomor_induk = session['nomor_induk']
				list_asesmen = ""
				
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT id_assesmen from tbl_peserta_assesmen WHERE nomor_ketua_jurusan=%s OR nomor_dosen_wali=%s OR nomor_dosen_1=%s OR nomor_dosen_2=%s OR nomor_dosen_3=%s OR nomor_dosen_4=%s OR nomor_dosen_5=%s OR nomor_dosen_6=%s OR nomor_dosen_7=%s OR nomor_dosen_8=%s", (nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk, nomor_induk))
				bulk_asesmen = cursor.fetchall()
				for item in bulk_asesmen:
					cursor.execute("SELECT * from tbl_kegiatan_assesmen WHERE id_assesmen=%s",[item['id_assesmen']])
					asesmen_detail = cursor.fetchone()
					if asesmen_detail:
						id_pengajuan = asesmen_detail['id_assesmen'].split('-')[0] + '-' + asesmen_detail['id_assesmen'].split('-')[1]
						status_asesmen = ""
						if asesmen_detail['status_assesmen'] == "Belum Selesai" :
							status_asesmen = """
								<td>
									<p class='text text-warning'>✕ Belum Selesai</p>
								</td>
								"""
						else :
							status_asesmen = f"""
								<td>
									<button type="button" onclick="window.location.href='/kajur/hasil-asesmen-kajur?id_asesmen={asesmen_detail['id_assesmen']}'" class='btn btn-primary'><i class='fas fa-eye'></i> Hasil</button>
								</td>
								"""
						
						list_asesmen += f"""
								<tr>
									<td>{asesmen_detail['id_assesmen']}</td>
									<td>{asesmen_detail['waktu']}</td>
									<td>{asesmen_detail['tempat_link']}</td>
									{status_asesmen}
									<td>
										<button type="button" class="btn btn-primary" onclick="window.location.href='/kajur/lihat-pengajuan-kajur?id_pengajuan={id_pengajuan}'"><i class="fas fa-eye"></i> Pengajuan</button>
                      					<button type="button" class="btn btn-primary" onclick="window.location.href='/kajur/lihat-berkas-kajur?id_pengajuan={id_pengajuan}'"><i class="fas fa-eye"></i> Berkas</button>
									</td>
									<td>
										<button type="button" class="btn btn-primary" onclick="window.location.href='/kajur/lihat-asesmen-kajur?id_asesmen={asesmen_detail['id_assesmen']}'"><i class="fas fa-eye"></i></button>
									</td>
								</tr>
								"""
				return render_template("kajur/jadwal-asesmen-kajur.html", full_name=full_name, list_asesmen=list_asesmen)
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kajur/lihat-pengajuan-kajur')
def lihat_pengajuan_kajur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Ketua Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				idPengajuan = request.args.get('id_pengajuan')
				full_name = session['fullname']
				nama_lengkap_mhs = ""
				nomor_induk_mhs = ""
				program_studi_kode = ""
				program_studi = ""
				tahun_angkatan = ""
				nama_mbkm = ""
				jenis_mbkm = ""
				tempat_mbkm = ""
				semester_mbkm = ""
				link_bukti =""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				sks_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_pengajuan_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				pengajuan_result = cursor.fetchone()
				if pengajuan_result:
					nomor_induk_mhs = pengajuan_result['nomor_induk_mahasiswa']
					program_studi_kode = pengajuan_result['kode_prodi']
					tahun_angkatan = pengajuan_result['angkatan']
					nama_mbkm = pengajuan_result['nama_program']
					jenis_mbkm = pengajuan_result['jenis_program']
					tempat_mbkm = pengajuan_result['tempat_program']
					link_bukti = pengajuan_result['bukti_program']
					semester_mbkm = pengajuan_result['semester_klaim']

				cursor.execute("SELECT nama from tbl_user where nomor_induk=%s", [nomor_induk_mhs])
				user_result = cursor.fetchone()
				if user_result:
					nama_lengkap_mhs = user_result['nama']

				cursor.execute("SELECT nama_prodi,jenjang from tbl_prodi_if where kode_prodi=%s", [program_studi_kode])
				prodi_result = cursor.fetchone()
				if prodi_result:
					program_studi = program_studi_kode + ' - ' + prodi_result['jenjang'] + ' ' + prodi_result['nama_prodi']

				cursor.execute("SELECT * from tbl_matkul_mbkm where id_pengajuan=%s", [request.args.get('id_pengajuan')])
				matkul_result = cursor.fetchone()
				if matkul_result:
					for i in range (1,9):
						kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
						nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']
						sks_matkul[j] = mat_result['jumlah_sks']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				return render_template('kajur/lihat-pengajuan-kajur.html', full_name=full_name, id_pengajuan=idPengajuan, nama_lengkap_mhs=nama_lengkap_mhs, nomor_induk_mhs=nomor_induk_mhs, program_studi=program_studi, tahun_angkatan=tahun_angkatan, nama_mbkm=nama_mbkm, jenis_mbkm=jenis_mbkm, tempat_mbkm=tempat_mbkm, link_bukti=link_bukti, semester_mbkm=semester_mbkm, \
				nama_matkul1=nama_matkul[0], dosen_matkul1=dosen_matkul[0], sks_matkul1=sks_matkul[0], nama_matkul2=nama_matkul[1], dosen_matkul2=dosen_matkul[1], sks_matkul2=sks_matkul[1], nama_matkul3=nama_matkul[2], dosen_matkul3=dosen_matkul[2], sks_matkul3=sks_matkul[2], nama_matkul4=nama_matkul[3], dosen_matkul4=dosen_matkul[3], sks_matkul4=sks_matkul[3], \
				nama_matkul5=nama_matkul[4], dosen_matkul5=dosen_matkul[4], sks_matkul5=sks_matkul[4], nama_matkul6=nama_matkul[5], dosen_matkul6=dosen_matkul[5], sks_matkul6=sks_matkul[5], nama_matkul7=nama_matkul[6], dosen_matkul7=dosen_matkul[6], sks_matkul7=sks_matkul[6], nama_matkul8=nama_matkul[7], dosen_matkul8=dosen_matkul[7], sks_matkul8=sks_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/jadwal-asesmen-kajur';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kajur/lihat-berkas-kajur')
def lihat_berkas_kajur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Ketua Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				full_name = session['fullname']
				id_pengajuan = request.args.get('id_pengajuan')
				link_sertifikat = ""
				link_laporan = ""
				link_hasil = ""
				tanggal_mulai =""
				tanggal_selesai = ""
				link_dokumentasi = ""

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_berkas_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
				berkas_result = cursor.fetchone()
				if berkas_result:
					link_sertifikat = berkas_result['sertifikat_program']
					link_laporan = berkas_result['laporan_program']
					link_hasil = berkas_result['hasil_program']
					tanggal_mulai = berkas_result['tanggal_mulai_program'].strftime("%d-%m-%Y")
					tanggal_selesai = berkas_result['tanggal_selesai_program'].strftime("%d-%m-%Y")
					link_dokumentasi = berkas_result['dokumentasi_program']
				return render_template('kajur/lihat-berkas-kajur.html', full_name=full_name, id_pengajuan=id_pengajuan, link_sertifikat=link_sertifikat, link_laporan=link_laporan, link_hasil=link_hasil, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai, link_dokumentasi=link_dokumentasi)
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/kajur/jadwal-asesmen-kajur';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/kajur/lihat-asesmen-kajur')
def lihat_asesmen_kajur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Ketua Jurusan':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				full_name = session['fullname']
				idAsesmen = request.args.get('id_asesmen')
				idPengajuan = ''
				waktu_asesmen = ''
				tempat_link = ''

				nomor_mahasiswa = ''
				mahasiswa = ''
				nomor_dosen_wali = ''
				dosen_wali = ''
				nomor_kajur = ''
				kajur = ''
				nomor_kaprodi = ''
				kaprodi = ''
				nomor_dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']
				dosen = ['Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada','Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute("SELECT * from tbl_kegiatan_assesmen INNER JOIN tbl_peserta_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_peserta_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [request.args.get('id_asesmen')])
				asesmen_detail = cursor.fetchone()
				if asesmen_detail :
					idPengajuan = asesmen_detail['id_pengajuan']
					waktu_asesmen = asesmen_detail['waktu'].strftime('%d-%m-%Y %H:%M')
					tempat_link = asesmen_detail['tempat_link']
					nomor_mahasiswa = asesmen_detail['nomor_mahasiswa']
					nomor_dosen_wali = asesmen_detail['nomor_dosen_wali']
					nomor_kajur = asesmen_detail['nomor_ketua_jurusan']
					nomor_kaprodi = asesmen_detail['nomor_kepala_prodi']
					for i in range (1,9):
						if asesmen_detail[f'nomor_dosen_{i}'] :
							nomor_dosen[i-1] = asesmen_detail[f'nomor_dosen_{i}']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_mahasiswa])
					mhs_detail = cursor.fetchone()
					if mhs_detail:
						mahasiswa = nomor_mahasiswa + ' - ' + mhs_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen_wali])
					wali_detail = cursor.fetchone()
					if wali_detail:
						dosen_wali = nomor_dosen_wali + ' - ' +  wali_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kajur])
					kajur_detail = cursor.fetchone()
					if kajur_detail:
						kajur = nomor_kajur + ' - ' +  kajur_detail['nama']

					cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_kaprodi])
					kaprodi_detail = cursor.fetchone()
					if kaprodi_detail:
						kaprodi = nomor_kaprodi + ' - ' +  kaprodi_detail['nama']

					for j in range (len(nomor_dosen)) :
						cursor.execute("SELECT nama from tbl_user WHERE nomor_induk=%s", [nomor_dosen[j]])
						dosen_detail = cursor.fetchone()
						if dosen_detail:
							dosen[j] = nomor_dosen[j] + ' - ' + dosen_detail['nama']

					return render_template('kajur/lihat-asesmen-kajur.html', full_name=full_name, id_asesmen=idAsesmen, id_pengajuan=idPengajuan, waktu_asesmen=waktu_asesmen, tempat_link=tempat_link, \
					mahasiswa=mahasiswa, dosen_wali=dosen_wali, kajur=kajur, kaprodi=kaprodi, dosen1=dosen[0], dosen2=dosen[1], dosen3=dosen[2], dosen4=dosen[3], dosen5=dosen[4], \
					dosen6=dosen[5], dosen7=dosen[6], dosen8=dosen[7])
			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/kajur/jadwal-asesmen-kajur';</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/dosen/hasil-asesmen-dosen')
def hasil_asesmen_dosen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Dosen':
			if 'id_asesmen' in request.args:
				full_name = session['fullname']
				id_asesmen = request.args.get('id_asesmen')
				id_pengajuan = ""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nilai_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute ("SELECT tbl_kegiatan_assesmen.id_pengajuan, tbl_form_assesmen.* from tbl_kegiatan_assesmen INNER JOIN tbl_form_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_form_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [id_asesmen])
				hasil_detail = cursor.fetchone()
				if hasil_detail:
					id_pengajuan = hasil_detail['id_pengajuan']
					cursor.execute("SELECT * from tbl_matkul_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
					matkul_result = cursor.fetchone()
					if matkul_result:
						for i in range (1,9):
							kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
							nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				for l in range (len(kode_matkul)):
					cursor.execute("SELECT * from tbl_form_assesmen where id_assesmen=%s", [id_asesmen])
					nilai_result = cursor.fetchone()
					if nilai_result:
						if nilai_result['nilai_matkul_' + str(l+1)] is not None:
							nilai_matkul[l] = nilai_result['nilai_matkul_' + str(l+1)]

				return render_template('dosen/hasil-asesmen-dosen.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, namaMatkul1=nama_matkul[0], dosenMatkul1=dosen_matkul[0], nilaiMatkul1=nilai_matkul[0], namaMatkul2=nama_matkul[1], dosenMatkul2=dosen_matkul[1], nilaiMatkul2=nilai_matkul[1], \
				namaMatkul3=nama_matkul[2], dosenMatkul3=dosen_matkul[2], nilaiMatkul3=nilai_matkul[2], namaMatkul4=nama_matkul[3], dosenMatkul4=dosen_matkul[3], nilaiMatkul4=nilai_matkul[3], namaMatkul5=nama_matkul[4], dosenMatkul5=dosen_matkul[4], nilaiMatkul5=nilai_matkul[4], \
				namaMatkul6=nama_matkul[5], dosenMatkul6=dosen_matkul[5], nilaiMatkul6=nilai_matkul[5], namaMatkul7=nama_matkul[6], dosenMatkul7=dosen_matkul[6], nilaiMatkul7=nilai_matkul[6], namaMatkul8=nama_matkul[7], dosenMatkul8=dosen_matkul[7], nilaiMatkul8=nilai_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/dosen/jadwal-asesmen-dosen';</script>"
		else:
			return redirect('/login')
	else:
		return redirect('/')

@app.route('/kajur/hasil-asesmen-kajur')
def hasil_asesmen_kajur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Ketua Jurusan':
			if 'id_asesmen' in request.args:
				full_name = session['fullname']
				id_asesmen = request.args.get('id_asesmen')
				id_pengajuan = ""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nilai_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute ("SELECT tbl_kegiatan_assesmen.id_pengajuan, tbl_form_assesmen.* from tbl_kegiatan_assesmen INNER JOIN tbl_form_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_form_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [id_asesmen])
				hasil_detail = cursor.fetchone()
				if hasil_detail:
					id_pengajuan = hasil_detail['id_pengajuan']
					cursor.execute("SELECT * from tbl_matkul_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
					matkul_result = cursor.fetchone()
					if matkul_result:
						for i in range (1,9):
							kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
							nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				for l in range (len(kode_matkul)):
					cursor.execute("SELECT * from tbl_form_assesmen where id_assesmen=%s", [id_asesmen])
					nilai_result = cursor.fetchone()
					if nilai_result:
						if nilai_result['nilai_matkul_' + str(l+1)] is not None:
							nilai_matkul[l] = nilai_result['nilai_matkul_' + str(l+1)]

				return render_template('kajur/hasil-asesmen-kajur.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, namaMatkul1=nama_matkul[0], dosenMatkul1=dosen_matkul[0], nilaiMatkul1=nilai_matkul[0], namaMatkul2=nama_matkul[1], dosenMatkul2=dosen_matkul[1], nilaiMatkul2=nilai_matkul[1], \
				namaMatkul3=nama_matkul[2], dosenMatkul3=dosen_matkul[2], nilaiMatkul3=nilai_matkul[2], namaMatkul4=nama_matkul[3], dosenMatkul4=dosen_matkul[3], nilaiMatkul4=nilai_matkul[3], namaMatkul5=nama_matkul[4], dosenMatkul5=dosen_matkul[4], nilaiMatkul5=nilai_matkul[4], \
				namaMatkul6=nama_matkul[5], dosenMatkul6=dosen_matkul[5], nilaiMatkul6=nilai_matkul[5], namaMatkul7=nama_matkul[6], dosenMatkul7=dosen_matkul[6], nilaiMatkul7=nilai_matkul[6], namaMatkul8=nama_matkul[7], dosenMatkul8=dosen_matkul[7], nilaiMatkul8=nilai_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/kajur/jadwal-asesmen-kajur';</script>"
		else:
			return redirect('/login')
	else:
		return redirect('/')

@app.route('/kaprodi/hasil-asesmen-kaprodi')
def hasil_asesmen_kaprodi():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Kepala Prodi':
			if 'id_asesmen' in request.args:
				full_name = session['fullname']
				id_asesmen = request.args.get('id_asesmen')
				id_pengajuan = ""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nilai_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute ("SELECT tbl_kegiatan_assesmen.id_pengajuan, tbl_form_assesmen.* from tbl_kegiatan_assesmen INNER JOIN tbl_form_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_form_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [id_asesmen])
				hasil_detail = cursor.fetchone()
				if hasil_detail:
					id_pengajuan = hasil_detail['id_pengajuan']
					cursor.execute("SELECT * from tbl_matkul_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
					matkul_result = cursor.fetchone()
					if matkul_result:
						for i in range (1,9):
							kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
							nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				for l in range (len(kode_matkul)):
					cursor.execute("SELECT * from tbl_form_assesmen where id_assesmen=%s", [id_asesmen])
					nilai_result = cursor.fetchone()
					if nilai_result:
						if nilai_result['nilai_matkul_' + str(l+1)] is not None:
							nilai_matkul[l] = nilai_result['nilai_matkul_' + str(l+1)]

				return render_template('kaprodi/hasil-asesmen-kaprodi.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, namaMatkul1=nama_matkul[0], dosenMatkul1=dosen_matkul[0], nilaiMatkul1=nilai_matkul[0], namaMatkul2=nama_matkul[1], dosenMatkul2=dosen_matkul[1], nilaiMatkul2=nilai_matkul[1], \
				namaMatkul3=nama_matkul[2], dosenMatkul3=dosen_matkul[2], nilaiMatkul3=nilai_matkul[2], namaMatkul4=nama_matkul[3], dosenMatkul4=dosen_matkul[3], nilaiMatkul4=nilai_matkul[3], namaMatkul5=nama_matkul[4], dosenMatkul5=dosen_matkul[4], nilaiMatkul5=nilai_matkul[4], \
				namaMatkul6=nama_matkul[5], dosenMatkul6=dosen_matkul[5], nilaiMatkul6=nilai_matkul[5], namaMatkul7=nama_matkul[6], dosenMatkul7=dosen_matkul[6], nilaiMatkul7=nilai_matkul[6], namaMatkul8=nama_matkul[7], dosenMatkul8=dosen_matkul[7], nilaiMatkul8=nilai_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/kaprodi/jadwal-asesmen-kaprodi';</script>"
		else:
			return redirect('/login')
	else:
		return redirect('/')

@app.route('/sekjur/hasil-asesmen-sekjur', methods=['GET'])
def hasil_asesmen_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if 'id_asesmen' in request.args:
				full_name = session['fullname']
				id_asesmen = request.args.get('id_asesmen')
				id_pengajuan = ""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nilai_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute ("SELECT tbl_kegiatan_assesmen.id_pengajuan, tbl_form_assesmen.* from tbl_kegiatan_assesmen INNER JOIN tbl_form_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_form_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [id_asesmen])
				hasil_detail = cursor.fetchone()
				if hasil_detail:
					id_pengajuan = hasil_detail['id_pengajuan']
					cursor.execute("SELECT * from tbl_matkul_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
					matkul_result = cursor.fetchone()
					if matkul_result:
						for i in range (1,9):
							kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
							nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				for l in range (len(kode_matkul)):
					cursor.execute("SELECT * from tbl_form_assesmen where id_assesmen=%s", [id_asesmen])
					nilai_result = cursor.fetchone()
					if nilai_result:
						if nilai_result['nilai_matkul_' + str(l+1)] is not None:
							nilai_matkul[l] = nilai_result['nilai_matkul_' + str(l+1)]

				return render_template('sekjur/hasil-asesmen-sekjur.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, namaMatkul1=nama_matkul[0], dosenMatkul1=dosen_matkul[0], nilaiMatkul1=nilai_matkul[0], namaMatkul2=nama_matkul[1], dosenMatkul2=dosen_matkul[1], nilaiMatkul2=nilai_matkul[1], \
				namaMatkul3=nama_matkul[2], dosenMatkul3=dosen_matkul[2], nilaiMatkul3=nilai_matkul[2], namaMatkul4=nama_matkul[3], dosenMatkul4=dosen_matkul[3], nilaiMatkul4=nilai_matkul[3], namaMatkul5=nama_matkul[4], dosenMatkul5=dosen_matkul[4], nilaiMatkul5=nilai_matkul[4], \
				namaMatkul6=nama_matkul[5], dosenMatkul6=dosen_matkul[5], nilaiMatkul6=nilai_matkul[5], namaMatkul7=nama_matkul[6], dosenMatkul7=dosen_matkul[6], nilaiMatkul7=nilai_matkul[6], namaMatkul8=nama_matkul[7], dosenMatkul8=dosen_matkul[7], nilaiMatkul8=nilai_matkul[7])

			else:
				return "<script>alert('Operasi Gagal! Tidak ada Nomor Asesmen!'); window.location.href='/sekjur/jadwal-asesmen-sekjur';</script>"
		else:
			return redirect('/login')
	else:
		return redirect('/')


@app.route('/sekjur/ubah-hasil-asesmen',methods=['GET','POST'])
def ubah_hasil_asesmen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if 'id_asesmen' in request.args:
				full_name = session['fullname']
				id_asesmen = request.args.get('id_asesmen')
				id_pengajuan = ""
				kode_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nomor_dosen = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nama_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				dosen_matkul = ['Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada', 'Tidak Ada']
				nilai_matkul = ['', '', '', '', '', '', '', '']
				onload_script = ""

				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute ("SELECT tbl_kegiatan_assesmen.id_pengajuan, tbl_form_assesmen.* from tbl_kegiatan_assesmen INNER JOIN tbl_form_assesmen ON tbl_kegiatan_assesmen.id_assesmen=tbl_form_assesmen.id_assesmen WHERE tbl_kegiatan_assesmen.id_assesmen=%s", [id_asesmen])
				hasil_detail = cursor.fetchone()
				if hasil_detail:
					id_pengajuan = hasil_detail['id_pengajuan']
					cursor.execute("SELECT * from tbl_matkul_mbkm WHERE id_pengajuan=%s", [id_pengajuan])
					matkul_result = cursor.fetchone()
					if matkul_result:
						for i in range (1,9):
							kode_matkul[i-1] = matkul_result['kode_matkul_' + str(i)]
							nomor_dosen[i-1] = matkul_result['nomor_dosen_' + str(i)]

				for j in range (len(kode_matkul)):
					cursor.execute("SELECT nama_matkul, jumlah_sks from tbl_mata_kuliah where kode_matkul=%s",[kode_matkul[j]])
					mat_result = cursor.fetchone()
					if mat_result:
						nama_matkul[j] = kode_matkul[j] + ' - ' + mat_result['nama_matkul']

				for k in range (len(nomor_dosen)):
					cursor.execute('SELECT nama from tbl_user where nomor_induk=%s', [nomor_dosen[k]])
					dosen_result = cursor.fetchone()
					if dosen_result:
						dosen_matkul[k] = nomor_dosen[k] + ' - ' + dosen_result['nama']

				for l in range (len(kode_matkul)):
					cursor.execute("SELECT * from tbl_form_assesmen where id_assesmen=%s", [id_asesmen])
					nilai_result = cursor.fetchone()
					if nilai_result:
						if nilai_result['nilai_matkul_' + str(l+1)] is not None:
							nilai_matkul[l] = nilai_result['nilai_matkul_' + str(l+1)]

				onload_script= f"""
						<script>
								selectElement('nilaiMatkul1','{nilai_matkul[0]}');
								selectElement('nilaiMatkul2','{nilai_matkul[1]}');
								selectElement('nilaiMatkul3','{nilai_matkul[2]}');
								selectElement('nilaiMatkul4','{nilai_matkul[3]}');
								selectElement('nilaiMatkul5','{nilai_matkul[4]}');
								selectElement('nilaiMatkul6','{nilai_matkul[5]}');
								selectElement('nilaiMatkul7','{nilai_matkul[6]}');
								selectElement('nilaiMatkul8','{nilai_matkul[7]}');
							</script>
							"""


				return render_template('sekjur/ubah-hasil-asesmen.html', full_name=full_name, id_asesmen=id_asesmen, id_pengajuan=id_pengajuan, matkul1=nama_matkul[0], dosen1=dosen_matkul[0], nilai1=nilai_matkul[0], matkul2=nama_matkul[1], dosen2=dosen_matkul[1], nilai2=nilai_matkul[1], \
				matkul3=nama_matkul[2], dosen3=dosen_matkul[2], nilai3=nilai_matkul[2], matkul4=nama_matkul[3], dosen4=dosen_matkul[3], nilai4=nilai_matkul[3], matkul5=nama_matkul[4], dosen5=dosen_matkul[4], nilai5=nilai_matkul[4], \
				matkul6=nama_matkul[5], dosen6=dosen_matkul[5], nilai6=nilai_matkul[5], matkul7=nama_matkul[6], dosen7=dosen_matkul[6], nilai7=nilai_matkul[6], matkul8=nama_matkul[7], dosen8=dosen_matkul[7], nilai8=nilai_matkul[7], onload_script=onload_script)


@app.route('/logout')
def logout():
	session.pop('nomor_induk', None)
	session.pop('username', None)
	session.pop('role', None)
	session.pop('fullname', None)
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
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Mahasiswa' and session['nomor_induk'] not in name:
			return redirect('/')
		return send_from_directory(app.config["UPLOAD_FOLDER"], name)
	else:
		return redirect('/login')

@app.route('/mahasiswa/hapus-pengajuan-mhs', methods=['GET'])
def hapus_pengajuan_mhs():
	if 'id_pengajuan' in request.args and session['nomor_induk'] in request.args.get('id_pengajuan'):
		if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
			if session['role'] == 'Mahasiswa':
				try:
					cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
					cursor.execute('SELECT id_assesmen from tbl_kegiatan_assesmen WHERE id_pengajuan=%s', [request.args.get('id_pengajuan')])
					if not cursor.fetchone():
						file_list = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + request.args.get('id_pengajuan') + '*')
						for file in file_list:
							os.remove(file)
						connection = mysql.connection
						delete_cursor = connection.cursor()
						delete_cursor.execute('DELETE FROM tbl_berkas_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						delete_cursor.execute('DELETE FROM tbl_matkul_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						delete_cursor.execute('DELETE FROM tbl_pengajuan_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						connection.commit()

						return "<script>alert('Pengajuan Berhasil Dihapus!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

					else:
						return "<script>alert('Pengajuan Tidak Bisa Dihapus! Jadwal Asesmen Sudah Ada!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

				except Exception:
					return "<script>alert('Pengajuan Gagal Dihapus!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"
			else:
				return redirect('/')
		else:
			return redirect('/login')
	else:
		return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

@app.route('/mahasiswa/hapus-berkas-mhs', methods=['GET'])
def hapus_berkas_mhs():
	if 'id_pengajuan' in request.args and session['nomor_induk'] in request.args.get('id_pengajuan'):
		if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
			if session['role'] == 'Mahasiswa':
				try:
					cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
					cursor.execute('SELECT id_assesmen from tbl_kegiatan_assesmen WHERE id_pengajuan=%s', [request.args.get('id_pengajuan')])
					if not cursor.fetchone():
						file_list = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + request.args.get('id_pengajuan') + '*')
						for file in file_list:
							if 'buktiMBKM' not in file:
								os.remove(file)

						connection = mysql.connection
						delete_cursor = connection.cursor()
						delete_cursor.execute('DELETE FROM tbl_berkas_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						connection.commit()

						return "<script>alert('Berkas Berhasil Dihapus!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

					else:
						return "<script>alert('Berkas Tidak Bisa Dihapus! Jadwal Asesmen Sudah Ada!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

				except Exception:
					return "<script>alert('Berkas Gagal Dihapus!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"
			else:
				return redirect('/')
		else:
			return redirect('/login')
	else:
		return "<script>alert('Operasi Gagal! Tidak ada Nomor Pengajuan!'); window.location.href='/mahasiswa/status-mbkm-mhs';</script>"

@app.route('/sekjur/terima-pengajuan', methods=['GET'])
def sekjur_terima_pengajuan():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				try:
					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute("UPDATE tbl_pengajuan_mbkm SET status_pengajuan='Accepted' WHERE id_pengajuan=%s", [request.args.get('id_pengajuan')])
					connection.commit()

					return "<script>alert('Pengajuan Berhasil Disetujui!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"

				except Exception:
					return "<script>alert('Pengajuan Gagal Disetujui!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
			else:
				return "<script>alert('Operasi Gagal! Tidak Ada Nomor Pengajuan!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
		else:
				return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/tolak-pengajuan', methods=['GET'])
def sekjur_tolak_pengajuan():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				try:
					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute("UPDATE tbl_pengajuan_mbkm SET status_pengajuan='Rejected' WHERE id_pengajuan=%s", [request.args.get('id_pengajuan')])
					connection.commit()

					return "<script>alert('Pengajuan Berhasil Ditolak!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"

				except Exception:
					return "<script>alert('Pengajuan Gagal Ditolak!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
			else:
				return "<script>alert('Operasi Gagal! Tidak Ada Nomor Pengajuan!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
		else:
				return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/hapus-pengajuan-sekjur', methods=['GET'])
def sekjur_hapus_pengajuan():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				try:
					cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
					cursor.execute('SELECT id_assesmen from tbl_kegiatan_assesmen WHERE id_pengajuan=%s', [request.args.get('id_pengajuan')])
					if not cursor.fetchone():
						file_list = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + request.args.get('id_pengajuan') + '*')
						for file in file_list:
							os.remove(file)
						connection = mysql.connection
						delete_cursor = connection.cursor()
						delete_cursor.execute('DELETE FROM tbl_berkas_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						delete_cursor.execute('DELETE FROM tbl_matkul_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						delete_cursor.execute('DELETE FROM tbl_pengajuan_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						connection.commit()

						return "<script>alert('Pengajuan Berhasil Dihapus!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"

					else:
						return "<script>alert('Pengajuan Gagal Dihapus! Jadwal Asesmen Sudah Ada!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
				except Exception:
					return "<script>alert('Pengajuan Gagal Dihapus!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
			else:
				return "<script>alert('Operasi Gagal! Tidak Ada Nomor Pengajuan!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
		else:
				return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/hapus-berkas-sekjur', methods=['GET'])
def sekjur_hapus_berkas():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_pengajuan' in request.args:
				try:
					cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
					cursor.execute('SELECT id_assesmen from tbl_kegiatan_assesmen WHERE id_pengajuan=%s', [request.args.get('id_pengajuan')])
					if not cursor.fetchone():
						file_list = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + request.args.get('id_pengajuan') + '*')
						for file in file_list:
							if 'buktiMBKM' not in file:
								os.remove(file)

						connection = mysql.connection
						delete_cursor = connection.cursor()
						delete_cursor.execute('DELETE FROM tbl_berkas_mbkm where id_pengajuan=%s', [request.args.get('id_pengajuan')])
						connection.commit()

						return "<script>alert('Berkas Berhasil Dihapus!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"

					else:
						return "<script>alert('Berkas Gagal Dihapus! Jadwal Asesmen Sudah Ada!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
				except Exception:
					return "<script>alert('Berkas Gagal Dihapus!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
			else:
				return "<script>alert('Operasi Gagal! Tidak Ada Nomor Pengajuan!');window.location.href='/sekjur/daftar-pengajuan-mbkm';</script>"
		else:
				return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/proses-ubah-asesmen',methods=['POST'])
def proses_ubah_asesmen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'POST' and all(i in request.form for i in ('idAsesmen', 'idPengajuan','timeAsesmen', 'tempatLink', 'mahasiswa', 'dosen_wali', 'kajur', 'kaprodi', 'dosen1')) :
				try:
					full_name = session['fullname']
					id_asesmen = request.form['idAsesmen']
					id_pengajuan = request.form['idPengajuan']
					waktu_asesmen = request.form['timeAsesmen']
					tempat_link = request.form['tempatLink']
					mahasiswa = request.form['mahasiswa']
					dosen_wali = request.form['dosen_wali']
					kajur = request.form['kajur']
					kaprodi = request.form['kaprodi']
					dosen1 = request.form['dosen1']
					dosen2 = request.form['dosen2'] if 'dosen2' in request.form else None
					dosen3 = request.form['dosen2'] if 'dosen3' in request.form else None
					dosen4 = request.form['dosen2'] if 'dosen4' in request.form else None
					dosen5 = request.form['dosen2'] if 'dosen5' in request.form else None
					dosen6 = request.form['dosen2'] if 'dosen6' in request.form else None
					dosen7 = request.form['dosen2'] if 'dosen7' in request.form else None
					dosen8 = request.form['dosen2'] if 'dosen8' in request.form else None

					asesmen_time = waktu_asesmen.split(' ')
					new_asesmen_time = reverse_date_string(asesmen_time[0]) + ' ' + asesmen_time[1]

					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute("UPDATE tbl_kegiatan_assesmen SET waktu=%s, tempat_link=%s WHERE id_assesmen=%s", (new_asesmen_time, tempat_link, id_asesmen))
					cursor.execute("UPDATE tbl_peserta_assesmen SET nomor_dosen_wali=%s, nomor_kepala_prodi=%s, nomor_ketua_jurusan=%s, nomor_dosen_1=%s, nomor_dosen_2=%s, nomor_dosen_3=%s, nomor_dosen_4=%s, nomor_dosen_5=%s, nomor_dosen_6=%s, nomor_dosen_7=%s, nomor_dosen_8=%s WHERE id_assesmen=%s",(dosen_wali, kaprodi, kajur, dosen1, dosen2, dosen3, dosen4, dosen5, dosen6, dosen7, dosen8, id_asesmen))
					connection.commit()

					return "<script>alert('Ubah Jadwal Asesmen Berhasil!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"

				except Exception :
					return "<script>alert('Ubah Jadwal Asesmen Gagal!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
			else:
				return "<script>alert('Harap Isi Semua Data Formulir dan Dosen Minimal 1!'); window.location.href='/sekjur/buat-asesmen-sekjur'</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/tambah-hasil-asesmen',methods=['POST'])
def tambah_hasil_asesmen():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'POST' and all (i in request.form for i in ('idAsesmen', 'idPengajuan', 'nilaiMatkul1')) :
				try:
					full_name = session['fullname']
					id_asesmen = request.form['idAsesmen']
					nilai1 = request.form['nilaiMatkul1']
					nilai2 = request.form['nilaiMatkul2'] if 'nilaiMatkul2' in request.form else None
					nilai3 = request.form['nilaiMatkul3'] if 'nilaiMatkul3' in request.form else None
					nilai4 = request.form['nilaiMatkul4'] if 'nilaiMatkul4' in request.form else None
					nilai5 = request.form['nilaiMatkul5'] if 'nilaiMatkul5' in request.form else None
					nilai6 = request.form['nilaiMatkul6'] if 'nilaiMatkul6' in request.form else None
					nilai7 = request.form['nilaiMatkul7'] if 'nilaiMatkul7' in request.form else None
					nilai8 = request.form['nilaiMatkul8'] if 'nilaiMatkul8' in request.form else None

					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute ("INSERT INTO tbl_form_assesmen VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_asesmen, nilai1, nilai2, nilai3, nilai4, nilai5, nilai6, nilai7, nilai8))
					cursor.execute ("UPDATE tbl_kegiatan_assesmen SET status_assesmen=%s WHERE id_assesmen=%s", ('Selesai',id_asesmen))
					connection.commit()

					return "<script>alert('Proses Asesmen Berhasil!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"

				except Exception :
					return "<script>alert('Proses Asesmen Gagal!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"

			else:
				return "<script>alert('Harap Isi Nilai Mata Kuliah Minimal 1!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/proses-ubah-hasil',methods=['POST'])
def proses_ubah_hasil_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'POST' and all (i in request.form for i in ('idAsesmen', 'idPengajuan', 'nilaiMatkul1')) :
				try:
					full_name = session['fullname']
					id_asesmen = request.form['idAsesmen']
					nilai1 = request.form['nilaiMatkul1']
					nilai2 = request.form['nilaiMatkul2'] if 'nilaiMatkul2' in request.form else None
					nilai3 = request.form['nilaiMatkul3'] if 'nilaiMatkul3' in request.form else None
					nilai4 = request.form['nilaiMatkul4'] if 'nilaiMatkul4' in request.form else None
					nilai5 = request.form['nilaiMatkul5'] if 'nilaiMatkul5' in request.form else None
					nilai6 = request.form['nilaiMatkul6'] if 'nilaiMatkul6' in request.form else None
					nilai7 = request.form['nilaiMatkul7'] if 'nilaiMatkul7' in request.form else None
					nilai8 = request.form['nilaiMatkul8'] if 'nilaiMatkul8' in request.form else None

					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute ("UPDATE tbl_form_assesmen set nilai_matkul_1=%s, nilai_matkul_2=%s, nilai_matkul_3=%s, nilai_matkul_4=%s, nilai_matkul_5=%s, nilai_matkul_6=%s, nilai_matkul_7=%s, nilai_matkul_8=%s WHERE id_assesmen=%s", (nilai1, nilai2, nilai3, nilai4, nilai5, nilai6, nilai7, nilai8, id_asesmen))
					connection.commit()

					return "<script>alert('Ubah Hasil Asesmen Berhasil!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"

				except Exception :
					return "<script>alert('Ubah Hasil Asesmen Gagal!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"

			else:
				return "<script>alert('Harap Isi Nilai Mata Kuliah Minimal 1!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/hapus-hasil-sekjur',methods=['GET'])
def hapus_hasil_sekjur():
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				try:
					full_name = session['fullname']
					id_asesmen = request.args.get('id_asesmen')

					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute("DELETE FROM tbl_form_assesmen WHERE id_assesmen=%s", [id_asesmen])
					cursor.execute("UPDATE tbl_kegiatan_assesmen set status_assesmen='Belum Selesai' WHERE id_assesmen=%s", [id_asesmen])
					connection.commit()

					return "<script>alert('Hasil Asesmen Berhasil Dihapus!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
				
				except Exception :
					return "<script>alert('Hasil Asesmen Gagal Dihapus!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
			else :
				return "<script>alert('Operasi Gagal! Tidak Ada Nomor Asesmen!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')

@app.route('/sekjur/hapus-asesmen-sekjur',methods=['GET'])
def hapus_asesmen_sekjur() :
	if session.get('nomor_induk') and session.get('username') and session.get('role') and session.get('fullname'):
		if session['role'] == 'Sekretaris Jurusan':
			if request.method == 'GET' and 'id_asesmen' in request.args :
				try:
					full_name = session['fullname']
					id_asesmen = request.args.get('id_asesmen')

					connection = mysql.connection
					cursor = connection.cursor()
					cursor.execute("DELETE FROM tbl_form_assesmen WHERE id_assesmen=%s", [id_asesmen])
					cursor.execute("DELETE FROM tbl_peserta_assesmen WHERE id_assesmen=%s", [id_asesmen])
					cursor.execute("DELETE FROM tbl_kegiatan_assesmen WHERE id_assesmen=%s", [id_asesmen])
					connection.commit()

					return "<script>alert('Asesmen Berhasil Dihapus!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
				
				except Exception :
					return "<script>alert('Asesmen Gagal Dihapus!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
			else :
				return "<script>alert('Operasi Gagal! Tidak Ada Nomor Asesmen!'); window.location.href='/sekjur/jadwal-asesmen-sekjur'</script>"
		else:
			return redirect('/')
	else:
		return redirect('/login')