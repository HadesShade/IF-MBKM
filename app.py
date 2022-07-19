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
	


