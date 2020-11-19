import pymysql
from app import app
from urllib.parse import urlparse
from flask import jsonify, request, session
from werkzeug.security import check_password_hash
import loginAPI
import logoutAPI

@app.route('/',methods=['POST'])
def home():
	if 'username' in session:
		username = session['username']
		return jsonify({'message' : 'You are already logged in', 'username' : username})
	else:
		resp = jsonify({'message' : 'Unauthorized'})
		resp.status_code = 401
		return resp
       		
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)