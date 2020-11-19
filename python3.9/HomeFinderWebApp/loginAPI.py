import pymysql
from app import app
from __main__ import app
from flask import jsonify, request, session
from werkzeug.security import check_password_hash

@app.route('/login', methods=['POST'])
def login():
	conn = None
	cursor = None

	_json = request.get_json()
	print(_json)
	_username = _json['username']
	_password = _json['password']

		# validate the received values
	if _username and _password:
		print ("test3")
		#check user exists			
		conn = conn = pymysql.connect( 
        host='homedatabase-1.csisk2h2fjry.us-west-1.rds.amazonaws.com', 
        user='root',  
        password = "homefinderdb95", 
        db='homefinder', 
        ) 
		cursor = conn.cursor()
			
		sql = "SELECT * FROM users WHERE username=%s"
		sql_where = (_username,)
			
		cursor.execute(sql, sql_where)
		row = cursor.fetchone()
			
	if row:
		if 	(row[7]== _password):
			session['username'] = row[1]
			#cursor.close()
			#conn.close()
			return jsonify({'message' : 'You are logged in successfully'})
		else:
			resp = jsonify({'message' : 'Bad Request - invalid password'})
			resp.status_code = 400
			return resp
	else:
		resp = jsonify({'message' : 'Bad Request - invalid credendtials'})
		resp.status_code = 400
		return resp
