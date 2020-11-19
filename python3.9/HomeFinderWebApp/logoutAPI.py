import pymysql
from app import app
from __main__ import app
from flask import jsonify, request, session
from werkzeug.security import check_password_hash

@app.route('/logout' ,methods=['POST'])
def logout():
	if 'username' in session:
		session.pop('username', None)
	return jsonify({'message' : 'You successfully logged out'})
