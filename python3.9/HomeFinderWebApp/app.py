from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from urllib.parse import urlparse
from flask import jsonify, request, session
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import pymysql
import json,os,io
from base64 import encodebytes
from PIL import Image
import base64
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

UPLOAD_FOLDER = os.getcwd()+'/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = "secret key"
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
CORS(app)

#Connect To MySQLDatabase hosted on AWS RDS
conn = None
conn = pymysql.connect( 
        host='homedatabase-1.csisk2h2fjry.us-west-1.rds.amazonaws.com', 
        user='root',  
        password = "homefinderdb95", 
        db='homefinder', 
        )  

#API THAT RETURNS ALL USERS 
@app.route('/returnAllUsers', methods=['GET', 'POST'])
def allUsersApi():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            # get waitlist users
            sql="SELECT * FROM users"
            cursor.execute(sql)
            #print (cursor.execute(sql))
            records = cursor.fetchall()
            jsonuser=[]
            jsonuser.append({'message' : 'You are already logged in', 'Admin id' : _adminid})

            for row in records:
                _userid=row[0]
                _firstname=row[1]
                _lastname=row[2]
                _address=row[3]
                _phone=row[4]
                _email=row[5]
                _username=row[6]
                _password=row[7]
                _usertype=row[8]

                jsonuser.append({'userid' : _userid,
                                'firstname' : _firstname, 
                                'lastname' : _lastname, 
                                'address' : _address, 
                                'phone' : _phone, 
                                'email' : _email, 
                                'usertype' : _usertype, 
                                'Option' : 'Approve / Reject'})
        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp
        
        return jsonify(jsonuser)


# GENERAL HOME FOR ALL WITH ALL LISTINGS BOTH SALES AND RENTAL
@app.route('/main' ,methods=['GET', 'POST'])
def generallHome():
    if request.method=='POST':
            return homeForAll()

    if request.method== 'GET':
        return 'general home page frontend'


######################################################## R E G I S T E R  A P I ##########################################################

# REGISTER
@app.route('/register' ,methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cursor = None

        _json = request.get_json()
        _firstname = _json['firstname']
        _lastname = _json['lastname']
        _address = _json['address']
        _phone = _json['phone']
        _email = _json['email']
        _username = _json['username']
        _password = _json['password']
        _usertype = _json['usertype']

        cursor = conn.cursor()
        sql = "INSERT INTO waitlist (firstname,lastname,address,phone,email,username,password,usertype) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
        sql_insert=(_firstname, _lastname , _address , _phone , _email , _username , _password,_usertype, )

        cursor.execute(sql,sql_insert)
        conn.commit()
        cursor.close()
        return jsonify({_firstname : 'You are redistered successfully'})
    if request.method== 'GET':
        return 'register frontend'

######################################################## A D M I N  A P I s ##########################################################

# ADMIN
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        cursor = None
        cursor = conn.cursor()

        _json = request.get_json()
        _code = _json['code']

        # validate the received values
        if _code:			
            sql = "SELECT * FROM admin WHERE code=%s"
            sql_where = (_code,)

            cursor.execute(sql, sql_where)
            row = cursor.fetchone()
            adminid=row[0]

        if row:
            if 	(row[1]== _code):
                print(_code)
                #session['adminid'] = row[0]
                updatesql = "UPDATE admin SET isactive=true WHERE id=%s"
                updatesql_where = (adminid,)
                cursor.execute(updatesql, updatesql_where)
                conn.commit()

                #cursor.close()
                #conn.close()
                return jsonify({'message' : 'You are logged in as admin successfully. you Admin ID:'+str(row[0])})
            else:
                resp = jsonify({'message' : 'Bad Request - invalid admin code'})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({'message' : 'Bad Request - invalid credendtials'})
            resp.status_code = 400
            return resp

    if request.method == 'GET':
        return 'admin login frontend'



#Admin Home
@app.route('/adminlogin/adminHome', methods=['GET', 'POST'])
def adminHome():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            # get waitlist users
            sql="SELECT * FROM waitlist"
            cursor.execute(sql)
            #print (cursor.execute(sql))
            records = cursor.fetchall()
            jsonuser=[]
            jsonuser.append({'message' : 'You are already logged in', 'Admin id' : _adminid})

            for row in records:
                _userid=row[0]
                _firstname=row[1]
                _lastname=row[2]
                _address=row[3]
                _phone=row[4]
                _email=row[5]
                _username=row[6]
                _password=row[7]
                _usertype=row[8]

                jsonuser.append({'userid' : _userid,
                                'firstname' : _firstname, 
                                'lastname' : _lastname, 
                                'address' : _address, 
                                'phone' : _phone, 
                                'email' : _email, 
                                'usertype' : _usertype, 
                                'Option' : 'Approve / Reject'})
            
            return jsonify(jsonuser)
        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp


#Admin Approve User
@app.route('/adminlogin/adminHome/approveUser', methods=['GET', 'POST'])
def approveUser():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            #get the waitlisted user id
            _json = request.get_json()
            _userid=_json['userid']

            cursor.execute("SELECT * FROM waitlist WHERE userid=%s",[_userid])
            row=cursor.fetchone()

            _firstname=row[1]
            _lastname=row[2]
            _address=row[3]
            _phone=row[4]
            _email=row[5]
            _username=row[6]
            _password=row[7]
            _usertype=row[8]

            approvesql="INSERT INTO users (firstname,lastname,address,phone,email,username,password,usertype,isactive) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,false);"
            sql_insert=(_firstname, _lastname , _address , _phone , _email , _username , _password,_usertype, )

            cursor.execute(approvesql,sql_insert)
            conn.commit()

            cursor.execute("DELETE FROM waitlist WHERE userid=%s",[_userid])
            conn.commit()
            cursor.close()

            return jsonify({'approveduser' : str(row[1])+' is approved successfully'})

        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'approve user page'


#Admin Reject User
@app.route('/adminlogin/adminHome/rejectUser', methods=['GET', 'POST'])
def rejectUser():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            #get the waitlisted user id
            _json = request.get_json()
            _userid=_json['userid']

            cursor.execute("DELETE FROM waitlist WHERE userid=%s",[_userid])
            conn.commit()
            cursor.close()

            return jsonify({'rejecteduser' :' user is rejected successfully and cannot log in to the applicaiton'})

        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'reject user page'


#ADMIN VIEWS ALL REPORTED LISTINGS 
@app.route('/adminlogin/adminHome/reportedListings', methods=['GET', 'POST'])
def reportedListings():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        listingdetails ={}
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            jsonuser1=[]
            jsonuser=[]
            rentlistingdetails={}
            jsonuser.append({'message' : 'You are already logged in', 'Admin id' : _adminid})

            cursor=None
            cursor=conn.cursor()

            # get rent reported listings
            rentsql="SELECT * FROM reportedlistings WHERE listingtype='rentlisting'"
            cursor.execute(rentsql)

            rentrecords = cursor.fetchall()

            for rentrow in rentrecords:
                _rentreportedid=rentrow[0]
                _rentlistingid=rentrow[1]
                _rentlistingcomments=rentrow[3]

                sql_select="SELECT * FROM rentlisting WHERE rentlistingid=%s"
                sql_select_where= (_rentlistingid,)
                cursor.execute(sql_select, sql_select_where)
                
                rec = cursor.fetchone()
                rec =list(rec)

                sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
                cursor.execute(sql_column)
                columns=(cursor.fetchall())
                
                cols =[i[0] for i in columns]   
                for col,val in zip(cols,rec):
                    image=""
                    image_path=""
                    listingdetails[col]=val
                if (listingdetails['filename']):    
                    image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
                    image = get_image(image_path)
                listingdetails['image']= image
                print(jsonuser)
                jsonuser.append({'reportid':_rentreportedid,
                                'rentlistingid':_rentlistingid,
                                'reportedcomments': _rentlistingcomments,
                                'rent listing details':listingdetails,
                                'options':'Keep Listing / Remove Rental Listing / Remove User '})
                rentlistingdetails.clear()


            # get sale reported listings
            salelistingdetails={}
            salesql="SELECT * FROM reportedlistings WHERE listingtype='salelisting'"
            cursor.execute(salesql)

            salerecords = cursor.fetchall()

            for salerow in salerecords:
                _salereportedid=salerow[0]
                _salelistingid=salerow[1]
                _salelistingcomments=salerow[3]

                cursor.execute("SELECT * FROM salelisting WHERE salelistingid=%s",[_salelistingid])
                rec = cursor.fetchone()
                rec =list(rec)

                sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
                cursor.execute(sql_column)
                columns=(cursor.fetchall())
                
                cols =[i[0] for i in columns]   
                for col,val in zip(cols,rec):
                    image=""
                    image_path=""
                    salelistingdetails[col]=val 
                if (listingdetails['filename']):     
                    image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
                    image = get_image(image_path)
                listingdetails['image']= image
                
                jsonuser.append(salelistingdetails)

                jsonuser.append({'reportid':_salereportedid,
                                'salelistingid':_salelistingid,
                                'reportedcomments': _salelistingcomments,
                                'options':'Keep Listing / Remove Rental Listing / Remove User '})
            
            #print (jsonuser)
            return jsonify(jsonuser)
        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'admin view reported listing page'


#ADMIN REMOVES REPORTED LISTING
@app.route('/adminlogin/adminHome/reportedListings/removeListing', methods=['GET', 'POST'])
def removeReportedListing():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            #get the reportedlisting id
            _json = request.get_json()
            _reportedlistingid=_json['reportid']

            cursor = None
            cursor = conn.cursor()

            sql = "SELECT * FROM reportedlistings WHERE reportedid=%s"
            sql_where = (_reportedlistingid,)

            cursor.execute(sql, sql_where)
            row = cursor.fetchone()

            #delete listing from database
            _listingid=row[1]
            _listingtype=row[2]

            if(_listingtype=='rentlisting'):
                cursor.execute("DELETE FROM rentlisting WHERE rentlistingid=%s",[_listingid])
                conn.commit()
            else:
                cursor.execute("DELETE FROM salelisting WHERE salelistingid=%s",[_listingid])
                conn.commit()

            cursor.execute("DELETE FROM reportedlistings WHERE reportedid=%s",[_reportedlistingid])
            conn.commit()

            return jsonify({'Notification' :' Following listing is removed from the application'})

        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'admin removes reported listing page'


#ADMIN KEEPS REPORTED LISTING
@app.route('/adminlogin/adminHome/reportedListings/keepListing', methods=['GET', 'POST'])
def keepReportedListing():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            #get the reportedlisting id
            _json = request.get_json()
            _reportedlistingid=_json['reportid']

            cursor = None
            cursor = conn.cursor()

            cursor.execute("DELETE FROM reportedlistings WHERE reportedid=%s",[_reportedlistingid])
            conn.commit()

            return jsonify({'Notification' :' Following listing is still in the application. No issues with the listing'})

        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'admin keeps reported listing page'


#ADMIN REMOVES USER AND ALL HIS POSTINGS
@app.route('/adminlogin/adminHome/reportedListings/removeuser', methods=['GET', 'POST'])
def removeUser():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            #get the reportedlisting id
            _json = request.get_json()
            _reportedlistingid=_json['reportid']

            cursor = None
            cursor = conn.cursor()

            sql = "SELECT * FROM reportedlistings WHERE reportedid=%s"
            sql_where = (_reportedlistingid,)

            cursor.execute(sql, sql_where)
            row = cursor.fetchone()

            #delete listing and the user from database
            _listingid=row[1]
            _listingtype=row[2]

            if(_listingtype=='rentlisting'):
                cursor.execute("SELECT * FROM rentlisting WHERE rentlistingid=%s",[_listingid])
                row = cursor.fetchone()
                if(row[14]!=0):
                    userid=row[14]
                    cursor.execute("DELETE FROM rentlisting WHERE landlordid=%s",[userid])
                    conn.commit()
            
                else:
                    userid=row[15]
                    cursor.execute("DELETE FROM rentlisting WHERE relatorid=%s",[userid])
                    conn.commit()

                
                cursor.execute("DELETE FROM rentapplication WHERE landlordid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM rentapplication WHERE realtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                if cursor.execute:
                    conn.commit()
 
            else:
                cursor.execute("SELECT * FROM salelisting WHERE salelistingid=%s",[_listingid])
                row = cursor.fetchone()
                if(row[11]!=0):
                    userid=row[11]
                    cursor.execute("DELETE FROM salelisting WHERE sellerid=%s",[userid])
                    conn.commit()
                else:
                    userid=row[12]
                    cursor.execute("DELETE FROM salelisting WHERE relatorid=%s",[userid])
                    conn.commit()

                cursor.execute("DELETE FROM saleapplication WHERE sellerid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM saleapplication WHERE sellerrealtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                if cursor.execute:
                    conn.commit()

            cursor.execute("DELETE FROM reportedlistings WHERE reportedid=%s",[_reportedlistingid])
            conn.commit()

            return jsonify({'Notification' :' Following listing and the user is removed from the application'})

        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'admin removes user page'



#ADMIN REMOVES USER AND ALL HIS POSTINGS WITHOUT REPORTING FUNC
@app.route('/adminlogin/adminHome/allUsers/removeuser', methods=['GET', 'POST'])
def kickUser():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        sql = "SELECT * FROM admin WHERE isactive=true"
        cursor.execute(sql)
        print(cursor.execute(sql))
        row = cursor.fetchone()

        #if 'adminid' in session:
        if cursor.execute(sql)==1:
            #_adminid=session['adminid']
            row = cursor.fetchone()
            _adminid=row[0]

            #get the reportedlisting id
            _json = request.get_json()
            userid=_json['userid']

            cursor = None
            cursor = conn.cursor()

            sql = "SELECT * FROM users WHERE userid=%s"
            sql_where = (userid,)

            cursor.execute(sql, sql_where)
            row = cursor.fetchone()
            usertype=row[8]

            if usertype=='renter':
                cursor.execute("DELETE FROM rentapplication WHERE renterid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM favorites WHERE userid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                conn.commit()

            if usertype=='buyer':
                cursor.execute("DELETE FROM saleapplication WHERE buyerid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM favorites WHERE userid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                conn.commit()

            if usertype=='landlord':
                cursor.execute("DELETE FROM rentapplication WHERE landlordid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM rentlisting WHERE landlordid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                conn.commit()

            if usertype=='seller':
                cursor.execute("DELETE FROM saleapplication WHERE sellerid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM salelisting WHERE sellerid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                conn.commit()

            if usertype=='realtor':
                cursor.execute("DELETE FROM saleapplication WHERE buyerrealtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM saleapplication WHERE sellerrealtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM rentapplication WHERE realtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM favorites WHERE userid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM salelisting WHERE realtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM rentlisting WHERE realtorid=%s",[userid])
                if cursor.execute:
                    conn.commit()

                cursor.execute("DELETE FROM users WHERE userid=%s",[userid])
                conn.commit()
                 
            return jsonify({'Notification' :' Following user and his data is removed from the application'})

        else:
            resp = jsonify({'message' : 'Unauthorized access. Admins only'})
            resp.status_code = 401
            return resp

    if request.method == 'GET':
        return 'admin removes user page'



#RENTER REPORT LISTING
@app.route('/renter/renterHome/dispolaylisting/reportListing', methods=['GET', 'POST'])
def reportLandlordListing():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()

        #get the listing id
        _json = request.get_json()
        _listingid=_json['listingid']
        _listingcomment=_json['listingcomment']

        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

            sql = "INSERT INTO reportedlistings (listingid,listingtype,comments) VALUES (%s,%s,%s);"
            sql_insert=(_listingid,'rentlisting',_listingcomment,)
            cursor.execute(sql,sql_insert)
            conn.commit()
            cursor.close()
            return jsonify({'Notification' :' Following listing is reported'})

    if request.method == 'GET':
        return 'renter report listing page'

#BUYER REPORT LISTING
@app.route('/buyer/reportListing', methods=['GET', 'POST'])
def reportSellerListing():
    if request.method == 'POST':

        cursor=None
        cursor=conn.cursor()

        #get the listing id
        _json = request.get_json()
        _listingid=_json['listingid']
        _listingcomment=_json['listingcomment']

        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

            sql = "INSERT INTO reportedlistings (listingid,listingtype,comments) VALUES (%s,%s,%s);"
            sql_insert=(_listingid,'salelisting',_listingcomment,)
            cursor.execute(sql,sql_insert)
            conn.commit()
            cursor.close()
            return jsonify({'Notification' :' Following listing is reported'})

    if request.method == 'GET':
        return 'buyer report listing page'

######################################################## L O G I N  A P I ##########################################################

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cursor = None
        jsonuser=[]

        _json = request.get_json()
        _username = _json['username']
        _password = _json['password']

        # validate the received values
        if _username and _password:			
            cursor = conn.cursor()

            sql = "SELECT * FROM users WHERE username=%s"
            sql_where = (_username,)
            cursor.execute(sql, sql_where)
            row = cursor.fetchone()
            _userid=row[0]
            _usertype=row[8]
            _name=row[1]
            global loggedinid
            loggedinid=_userid
            print(loggedinid)

        if row:
            if 	(row[7]== _password):
                #session['username'] = row[1]
                #session['id'] = str(row[0])

                updatesql = "UPDATE users SET isactive=true WHERE userid=%s"
                updatesql_where = (_userid,)
                cursor.execute(updatesql, updatesql_where)
                conn.commit()
                
                #cursor.close()
                #conn.close()
                jsonuser.append({'id':_userid,'usertype':_usertype,'name':_name})
                jsonuser.append({'message' : 'You are logged in successfully'})

            else:
                resp = jsonify({'message' : 'Bad Request - invalid password'})
                resp.status_code = 400
                return jsonuser.append(resp)
        else:
            resp = jsonify({'message' : 'Bad Request - invalid credendtials'})
            resp.status_code = 400
            return jsonuser.append(resp)

        return jsonify(jsonuser)


    if request.method == 'GET':
        return 'login frontend'


######################################################## R E N T E R , B U Y E R , B U Y E R - R E A L T O R  A P I s ##########################################################



# HOME PAGE WITH ALL LISTINGS FOR : RENTER , BUYER , BUYER REALTOR
@app.route('/login/home' ,methods=['GET', 'POST'])
def Home():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()

        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

            if (usertype=='renter'):
                renterid = id
                _renterfirstname=row[1]
                return renterHomePage(renterid)

            if (usertype=='buyer'):
                buyerid = id
                _buyerfirstname=row[1]
                return buyerHomePage(buyerid)

            if (usertype=='realtor'):
                realtorid = id
                _realtorfirstname=row[1]
                return buyerHomePage(realtorid)

        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or Realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'home page frontend'


#RENTER BUYER OR BUYER REALTOR SELECTS ONE LISTING TO VIEW INFORMATION ABOUT IT - AND CAN SUBMIT AN APPLICATION IF NEEDED
@app.route('/login/home/reviewListing' ,methods=['GET', 'POST'])
def reviewListing():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='renter':
            renterid = id
            return renterReviewListing(renterid)
        if usertype=='buyer':
            buyerid = id
            return buyerReviewListing(buyerid)
        if usertype=='realtor':
            realtorid = id
            return buyerReviewListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'review listing and submit application  page frontend'



#RENTER BUYER OR BUYER REALTOR VIEWS THEIR INBOX
@app.route('/login/home/inbox' ,methods=['GET', 'POST'])
def inbox():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
        if usertype=='renter':
            renterid = id
            return renterInbox(renterid)
        if usertype=='buyer':
            buyerid = id
            return buyerInbox(buyerid)
        if usertype=='realtor':
            realtorid = id
            return buyerInbox(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'inbox page frontend'

#RENTER BUYER OR BUYER REALTOR VIEWS PENDING APPLICATIONS
@app.route('/login/home/pending' ,methods=['GET', 'POST'])
def pending():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
        if usertype=='renter':
            renterid = id
            return renterPending(renterid)
        if usertype=='buyer':
            buyerid = id
            return buyerPending(buyerid)
        if usertype=='realtor':
            realtorid = id
            return buyerPending(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'pending page frontend'

#RENTER BUYER OR BUYER REALTOR ADDS A LISTINGS TO FAVORITES
@app.route('/login/home/reviewListing/favorite' ,methods=['GET', 'POST'])
def myFavorites():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
        if usertype=='renter':
            renterid = id
            return addToFavorites(renterid)
        if usertype=='buyer':
            buyerid = id
            return addToFavorites(buyerid)
        if usertype=='realtor':
            realtorid = id
            return addToFavorites(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'add to fav frontend'

#RENTER BUYER OR BUYER REALTOR REMOVES A LISTING FROM FAVORITES
@app.route('/login/home/myFavorites/remove' ,methods=['GET', 'POST'])
def removeFavorite():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
        if usertype=='renter':
            renterid = id
            return removeFromFav(renterid)
        if usertype=='buyer':
            buyerid = id
            return removeFromFav(buyerid)
        if usertype=='realtor':
            realtorid = id
            return removeFromFav(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'remove from fav frontend'


#RENTER BUYER OR BUYER REALTOR VIEWS FAVORITES
@app.route('/login/home/myFavorites' ,methods=['GET', 'POST'])
def viewmyFavorite():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
        if usertype=='renter':
            renterid = id
            return viewFav(renterid)
        if usertype=='buyer':
            buyerid = id
            return viewFav(buyerid)
        if usertype=='realtor':
            realtorid = id
            return viewFav(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'remove from fav frontend'

######################################################## S E A R C H   A P I s ##########################################################

#SEARCH API FOR ALL ROLES
@app.route('/login/search' ,methods=['GET', 'POST'])
def searchAPI():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
            return searchItAll()
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as buyer, renter or realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'search frontend'

######################################################## L A N D L O R D ,  L A N D L O R D - R E A L T O R  A P I s ##########################################################

# LANDLORD OR LANDLORD REALTOR CREATE LISTING
@app.route('/login/createRentalListing' ,methods=['GET', 'POST'])
def landlord():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

            if (usertype=='landlord'):
                landlordid = id
                _landlordfirstname=row[1]
                return createRentalListing(landlordid)

            if (usertype=='realtor'):
                realtorid = id
                _realtorfirstname=row[1]
                return createRentalListing(realtorid)

        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord Realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord page frontend'

#LANDLORD OR LANDLORD REALTOR VIEWS THEIR LISTINGS
@app.route('/login/myRentalListings' ,methods=['GET', 'POST'])
def landlordViewListings():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        #sql = "SELECT * FROM users WHERE isactive=true AND userid=%s"
        #cursor.execute(sql,int(loggedinid))

        if count==1:
            row = cursor.fetchone()
            print(row[0])
            id=row[0]
            usertype=row[8]

            if (usertype=='landlord'):
                landlordid = id
                _landlordfirstname=row[1]
                return ViewMyRentalListings(landlordid)

            if (usertype=='realtor'):
                realtorid = id
                _realtorfirstname=row[1]
                return ViewMyRentalListings(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord views his listings page frontend'


#LANDLORD OR LANDLORD REALTOR SELECTS ONE LISTING TO VIEW INFORMATION ABOUT IT
@app.route('/login/myRentalListings/selectListing' ,methods=['GET', 'POST'])
def landlordSelectListings():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]
        
        if usertype=='landlord':
            landlordid = id
            return displaySelectedRentListing(landlordid)
        if usertype=='realtor':
            realtorid = id
            return displaySelectedRentListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord views his listings page frontend'


#LANDLORD OR LANDLORD REALTOR UPDATES THEIR LISTING
@app.route('/login/myRentalListings/selectListing/updateListing' ,methods=['GET', 'POST'])
def landlordUpdatesListing():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='landlord':
            landlordid = id
            return updateRentalListing(landlordid)
        if usertype=='realtor':
            realtorid = id
            return updateRentalListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord updates listing page frontend'


#LANDLORD OR LANDLORD REALTOR DELETES THEIR LISTING
@app.route('/login/myRentalListings/selectListing/deleteListing' ,methods=['GET', 'POST'])
def landlorddeletesListing():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='landlord':
            landlordid = id
            return deleteRentListing(landlordid)
        if usertype=='realtor':
            realtorid = id
            return deleteRentListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord deletes listing page frontend'


#LANDLORD OR LANDLORD REALTOR VIEWS RENTERS APPLICATIONS FOR THAT LISTING
@app.route('/login/myRentalListings/viewApplications' ,methods=['GET', 'POST'])
def landlordViewApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='landlord':
            landlordid = id
            return ViewRentalApplications(landlordid)
        if usertype=='realtor':
            realtorid = id
            return ViewRentalApplications(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord view application page frontend'

#LANDLORD OR LANDLORD REALTOR SELECTS A RENTAL APPLICATION 
@app.route('/login/myRentalListings/viewApplications/selectApplication' ,methods=['GET', 'POST'])
def landlordSelectApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='landlord':
            landlordid = id
            return selectRentalApplication(landlordid)
        if usertype=='realtor':
            realtorid = session['realtorid']
            return selectRentalApplication(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord select application page frontend'



#LANDLORD OR LANDLORD REALTOR APPROVES RENTERS APPLICATION
@app.route('/login/myRentalListings/viewApplications/selectApplication/approve' ,methods=['GET', 'POST'])
def landlordApproveApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='landlord':
            landlordid = id
            return approveRentalApplication(landlordid)
        if usertype=='realtor':
            realtorid = id
            return approveRentalApplication(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord approves renters application page frontend'


#LANDLORD OR LANDLORD REALTOR REJECTS RENTERS APPLICATION
@app.route('/login/myRentalListings/viewApplications/selectApplication/reject' ,methods=['GET', 'POST'])
def landlordRejectApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        #sql = "SELECT * FROM users WHERE isactive=true"
        #cursor.execute(sql)
        #print(cursor.execute(sql))
        #row = cursor.fetchone()

        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]
            usertype=row[8]

        if usertype=='landlord':
            landlordid = id
            return rejectRentalApplication(landlordid)
        if usertype=='realtor':
            realtorid = id
            return rejectRentalApplication(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as landlord or landlord realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'landlord rejects renters application page frontend'


######################################################## S E L L E R ,  S E L L E R - R E A L T O R   A P I s ##########################################################



#SELLER OR SELLER REALTOR CREATELISTING
@app.route('/login/createSaleListing' ,methods=['GET', 'POST'])
def seller():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
            if (usertype=='seller'):
                sellerid = id
                _sellerfirstname=row[1]
                return createSaleListing(sellerid)

            if (usertype=='realtor'):
                realtorid = id
                _realtorfirstname=row[1]
                return createSaleListing(realtorid)

        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller Realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller page frontend'



#SELLER OR SELLER REALTOR VIEWS THEIR LISTINGS
@app.route('/login/mySaleListings' ,methods=['GET', 'POST'])
def sellerViewListings():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]

            if (usertype=='seller'):
                sellerid = id
                _sellerfirstname=row[1]
                return ViewMySaleListings(sellerid)

            if (usertype=='realtor'):
                realtorid = id
                _realtorfirstname=row[1]
                return ViewMySaleListings(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller views his listings page frontend'


#SELLER OR SELLER REALTOR SELECTS ONE LISTING TO VIEW INFORMATION ABOUT IT
@app.route('/login/mySaleListings/selectListing' ,methods=['GET', 'POST'])
def sellerSelectListings():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]

        if usertype=='seller':
            sellerid = id
            return displaySelectedSaleListing(sellerid)
        if usertype=='realtor':
            realtorid = id
            return displaySelectedSaleListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller views/selects his listings page frontend'



#SELLER OR SELLER REALTOR UPDATES THEIR LISTING
@app.route('/login/mySaleListings/selectListing/updateListing' ,methods=['GET', 'POST'])
def sellerUpdatesListing():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
        if usertype=='seller':
            sellerid = id
            return updateSaleListing(sellerid)
        if usertype=='realtor':
            realtorid = id
            return updateSaleListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller updates page frontend'


#SELLER OR SELLER REALTOR DELETES THEIR LISTING
@app.route('/login/mySaleListings/selectListing/deleteListing' ,methods=['GET', 'POST'])
def sellerdeletesListing():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
        if usertype=='seller':
            sellerid = id
            return deleteSaleListing(sellerid)
        if usertype=='realtor':
            realtorid = id
            return deleteSaleListing(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller deletes listing page frontend'



#SELLER OR SELLER REALTOR VIEWS BUYERS APPLICATIONS FOR THAT LISTING
@app.route('/login/mySaleListings/viewApplications' ,methods=['GET', 'POST'])
def sellerViewApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
        if usertype=='seller':
            sellerid = id
            return ViewBuyersApplications(sellerid)
        if usertype=='realtor':
            realtorid = id
            return ViewBuyersApplications(realtorid)
        else:
            session.pop('sellerid', None)
            session.pop('realtorid', None)
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller view application page frontend'



#SELLER OR SELLER REALTOR SELECTS A SALE APPLICATION 
@app.route('/login/mySaleListings/viewApplications/selectApplication' ,methods=['GET', 'POST'])
def sellerSelectApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
        if usertype=='seller':
            sellerid = id
            return selectBuyerApplication(sellerid)
        if usertype=='realtor':
            realtorid = id
            return selectBuyerApplication(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller select application page frontend'



#SELLER OR SELLER REALTOR APPROVES BUYERS APPLICATION
@app.route('/login/mySaleListings/viewApplications/selectApplication/approve' ,methods=['GET', 'POST'])
def sellerApproveApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
        if usertype=='seller':
            sellerid = id
            return approveBuyerApplication(sellerid)
        if usertype=='realtor':
            realtorid = id
            return approveBuyerApplication(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller approves buyers application page frontend'


#SELLER OR SELLER REALTOR REJECTS BUYERS APPLICATION
@app.route('/login/mySaleListings/viewApplications/selectApplication/reject' ,methods=['GET', 'POST'])
def sellerRejectApplication():
    if request.method=='POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))
        
        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            id=row[0]

            usertype=row[8]
        if usertype=='seller':
            sellerid = id
            return rejectBuyerApplication(sellerid)
        if usertype=='realtor':
            realtorid = id
            return rejectBuyerApplication(realtorid)
        else:
            resp = jsonify({'message' : 'Unauthorized. Please log in as seller or seller realtor'})
            resp.status_code = 401
            return resp

    if request.method== 'GET':
        return 'seller rejects buyers application page frontend'



######################################################## L O G O U T ##########################################################

# LOGOUT
@app.route('/logout' ,methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        cursor=None
        cursor=conn.cursor()
        
        print("this is "+str(loggedinid))

        count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
        print(count)

        if count==1:
            row = cursor.fetchone()
            _userid=row[0]
            
           # updatesql = "UPDATE users SET isactive=false"
            cursor.execute("UPDATE users SET isactive=false WHERE userid=%s",[loggedinid])
            conn.commit()

        return jsonify({'message' : 'You successfully logged out'})

    if request.method== 'GET':
        return 'logout frontend'



######################################################## S A L E S  M O D E L ##########################################################

def createSaleListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        _sellerid = sellerid
        _realtorid= 0
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= 'open'
            _price = _form['price']
            _openhouse=_form['openhouse']
            filename =None
            image=''

            if request.files:
                image = request.files['image']
                if image and valid_file(image.filename):
                    filename = secure_filename(image.filename)
                    print(UPLOAD_FOLDER)
                    print(filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      

            cursor = conn.cursor()
            sql = "INSERT INTO salelisting (address,zipcode,area,noofbedrooms,noofbathrooms,hometype,parkingtype,yearbuilt,status,price,sellerid,realtorid,openhouse,filename) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            sql_insert=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price,id, _realtorid,_openhouse, filename,)
            cursor.execute(sql,sql_insert)
            conn.commit()
            jsonuser.append({'Notification' : 'Your listing has been added successfully'})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        _realtorid = realtorid
        _sellerid= 0
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= 'open'
            _price = _form['price']
            _openhouse=_form['openhouse']
            filename =None
            image=''

            if request.files:
                image = request.files['image']
                if image and valid_file(image.filename):
                    filename = secure_filename(image.filename)
                    print(UPLOAD_FOLDER)
                    print(filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      

            cursor = conn.cursor()
            sql = "INSERT INTO salelisting (address,zipcode,area,noofbedrooms,noofbathrooms,hometype,parkingtype,yearbuilt,status,price,sellerid,realtorid,openhouse,filename) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            sql_insert=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price,_sellerid,id,_openhouse,filename,)
            cursor.execute(sql,sql_insert)
            conn.commit()
            jsonuser.append({'Notification' : 'Your listing has been added successfully'})

    return jsonify(jsonuser)


def ViewMySaleListings(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    _listings=[]

    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)


    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})
        sql = "SELECT * FROM salelisting WHERE sellerid=%s"
    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
        sql = "SELECT * FROM salelisting WHERE realtorid=%s"

    sql_where = (id,)

    cursor.execute(sql, sql_where)
    records = cursor.fetchall()
    records=list(records)

    sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
    cursor.execute(sql_column)
    columns=list(cursor.fetchall())

    cols =[i[0] for i in columns]   
    for record in records:
        _list={}
        image, image_path='',''
        for col,val in zip(cols,record):
            _list[col]=val   
        if (record[-1]):
            print(str(record[-1]))    
            image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
            image = get_image(image_path) 
        _list['image']= image
        #print(image_path)
        _listings.append(_list)
        _listings.append('options :Remove Sale Listing /Update Listing/ View applications for this Listing')

    jsonuser.append({'sale listings':_listings})

    return jsonify(jsonuser)

def ViewBuyersApplications(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _salelistingid=_json['salelistingid']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})
        sql = "SELECT * FROM saleapplication WHERE status IS NULL AND sellerid=%s AND salelistingid=%s"
    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
        sql = "SELECT * FROM saleapplication WHERE status IS NULL AND sellerrealtorid=%s AND salelistingid=%s"

    sql_where = (id,_salelistingid,)
    cursor.execute(sql, sql_where)
    records= cursor.fetchall()

    for row in records:
        _saleapplicationid=row[0]
        _name=row[3]
        _contactphone=row[7]
        _email=row[8]
        _offerprice=row[9]

        jsonuser.append({'applicationid' : _saleapplicationid,
        'name' : _name, 
        'phone' : _contactphone, 
        'email' : _email, 
        'offerprice' : _offerprice, 
        'Option' : 'Approve / Reject'})

    return jsonify(jsonuser)


def selectBuyerApplication(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _saleapplicationid=_json['applicationid']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})
        sql = "SELECT * FROM saleapplication WHERE saleapplicationid=%s AND sellerid=%s"
    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
        sql = "SELECT * FROM saleapplication WHERE saleapplicationid=%s AND sellerrealtorid=%s"

    sql_where = (_saleapplicationid,id,)
    cursor.execute(sql, sql_where)
    row= cursor.fetchone()

    _saleapplicationid=row[0]
    _name=row[3]
    _contactphone=row[7]
    _email=row[8]
    _offerprice=row[9]

    jsonuser.append({'applicationid' : _saleapplicationid,
    'name' : _name, 
    'phone' : _contactphone, 
    'email' : _email, 
    'offerprice' : _offerprice,  
    'Option' : 'Approve / Reject'})

    return jsonify(jsonuser)


def approveBuyerApplication(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _applicationid=_json['applicationid']
    _message=_json['messagetobuyer']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})

        sql = "SELECT * FROM saleapplication WHERE sellerid=%s AND saleapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[3]

        updatesql = "UPDATE saleapplication SET status=true WHERE sellerid=%s AND saleapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE saleapplication SET message=%s WHERE sellerid=%s AND saleapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified about the approval'})

    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql = "SELECT * FROM saleapplication WHERE sellerrealtorid=%s AND saleapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[3]

        updatesql = "UPDATE saleapplication SET status=true WHERE sellerrealtorid=%s AND saleapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE saleapplication SET message=%s WHERE sellerrealtorid=%s AND saleapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified about the approval'})

    return jsonify(jsonuser)


def rejectBuyerApplication(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _applicationid=_json['applicationid']
    _message=_json['messagetobuyer']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})

        sql = "SELECT * FROM saleapplication WHERE sellerid=%s AND saleapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[3]

        updatesql = "UPDATE saleapplication SET status=false WHERE sellerid=%s AND saleapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE saleapplication SET message=%s WHERE sellerid=%s AND saleapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified that their application is rejected'})

    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql = "SELECT * FROM saleapplication WHERE sellerrealtorid=%s AND saleapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[3]

        updatesql = "UPDATE saleapplication SET status=false WHERE sellerrealtorid=%s AND saleapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE saleapplication SET message=%s WHERE sellerrealtorid=%s AND saleapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified that their application is rejected'})

    return jsonify(jsonuser)


def updateSaleListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get listing id
    form = request.form
    _salelistingid=form['salelistingid']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        _sellerid = sellerid
        _realtorid= 0
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= _form['status']
            _price = _form['price']

            if _address and _zipcode and _area and _noofbedrooms and _noofbathrooms and _hometype and _parkingtype and _yearbuilt and _status and _price and (_sellerid or _realtorid):
                cursor = conn.cursor()
                sql = "UPDATE salelisting SET address=%s,zipcode=%s,area=%s,noofbedrooms=%s,noofbathrooms=%s,hometype=%s,parkingtype=%s,yearbuilt=%s,status=%s,price=%s,sellerid=%s,realtorid=%s WHERE salelistingid =%s;"
                sql_where=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price,id, _realtorid, _salelistingid)
                cursor.execute(sql,sql_where)
                conn.commit()

                jsonuser.append({'Notification':'listing updated successfully'})
            else:
                jsonuser.append({'Warning' : 'Please fill out the details'})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        _realtorid = realtorid
        _sellerid= 0
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= _form['status']
            _price = _form['price']

            if _address and _zipcode and _area and _noofbedrooms and _noofbathrooms and _hometype and _parkingtype and _yearbuilt and _status and _price and (_sellerid or _realtorid):
                cursor = conn.cursor()
                sql = "UPDATE salelisting SET address=%s,zipcode=%s,area=%s,noofbedrooms=%s,noofbathrooms=%s,hometype=%s,parkingtype=%s,yearbuilt=%s,status=%s,price=%s,sellerid=%s,realtorid=%s WHERE salelistingid =%s;"
                sql_where=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price,_sellerid, id, _salelistingid)
                cursor.execute(sql,sql_where)
                conn.commit()
                
                jsonuser.append({'Notification':'listing updated successfully'})
            else:
                jsonuser.append({'Warning' : 'Please fill out the details'})

    return jsonify(jsonuser)



def deleteSaleListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the listing id
    _json = request.get_json()
    _salelistingid=_json['salelistingid']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})

        sql_select = "SELECT * FROM salelisting where salelistingid =%s AND sellerid=%s"
        sql_select_where= (_salelistingid,id,)
        cursor.execute(sql_select,sql_select_where)
        rec = cursor.fetchone()
        print(rec)
        if rec:
            sql_delete = "DELETE FROM salelisting WHERE salelistingid=%s AND sellerid=%s"
            sql_delete_where = (_salelistingid,id,)
            cursor.execute(sql_delete, sql_delete_where)
            conn.commit()
            #cursor.close()
        else:
            jsonuser.append({'Warning':'Your listing does not exist'})

        jsonuser.append({'Notification':'Your listing has been deleted'})


    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql_select = "SELECT * FROM salelisting where salelistingid =%s AND realtorid=%s"
        sql_select_where= (_salelistingid,id,)
        cursor.execute(sql_select,sql_select_where)
        rec = cursor.fetchone()
        print(rec)
        if rec:
            sql_delete = "DELETE FROM salelisting WHERE salelistingid=%s AND realtorid=%s"
            sql_delete_where = (_salelistingid,id,)
            cursor.execute(sql_delete, sql_delete_where)
            conn.commit()
            jsonuser.append({'Notification':'Your listing has been deleted'})
            #cursor.close()
        else:
            jsonuser.append({'Warning':'Your listing does not exist'})

    return jsonify(jsonuser)


def displaySelectedSaleListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    listingdetails ={}

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]


    #get the listing id
    _json = request.get_json()
    _salelistingid=_json['salelistingid']

    if usertype=='seller':
        sellerid = activeuserid
        _sellerfirstname=activeusername
        jsonuser.append({sellerid: 'id', _sellerfirstname : 'name'})
        
        sql_select = "SELECT * FROM salelisting where salelistingid =%s AND sellerid=%s"
        sql_select_where= (_salelistingid,id,)
        cursor.execute(sql_select, sql_select_where)

        rec = cursor.fetchone()
        rec =list(rec)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for col,val in zip(cols,rec):
            image, image_path='',''
            listingdetails[col]=val 
        if (listingdetails['filename']):
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image
        
        jsonuser.append(listingdetails)

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
        
        sql_select = "SELECT * FROM salelisting where salelistingid =%s AND realtorid=%s"
        sql_select_where= (_salelistingid,id,)
        cursor.execute(sql_select, sql_select_where)

        rec = cursor.fetchone()
        rec =list(rec)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for col,val in zip(cols,rec):
            image, image_path='',''
            listingdetails[col]=val 
        if (listingdetails['filename']):
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image
        
        jsonuser.append(listingdetails)
   
    return jsonify(jsonuser)

def buyerHomePage(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    _listings=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'buyer' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='buyer':
        buyerid = activeuserid
        _buyerfirstname=activeusername
        jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'})

        sql ="select * from salelisting;"
        cursor.execute(sql)
        records = cursor.fetchall()
        records=list(records)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            image=""
            image_path=""
            for col,val in zip(cols,record):
                _list[col]=val 
            if (record[-1]):
                print(str(record[-1]))    
                image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
                image = get_image(image_path)   
            _list['image']= image
            _listings.append(_list)

        jsonuser.append({'sale listings':_listings})


    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql ="select * from salelisting;"
        cursor.execute(sql)
        records = cursor.fetchall()
        records=list(records)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            image=''
            image_path=''
            for col,val in zip(cols,record):
                _list[col]=val   
            if (record[-1]): 
                image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
                image = get_image(image_path)
            _list['image']= image
            _listings.append(_list)

        jsonuser.append({'sale listings':_listings})
    
    return jsonify(jsonuser)

def buyerReviewListing(id):
    listingdetails ={}
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the listing id
    _json = request.get_json()
    _salelistingid=_json['salelistingid']

    if usertype=='buyer':
        buyerid = activeuserid
        _buyerfirstname=activeusername
        buyerrelatorid=0
        jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'})

        sql = "SELECT * FROM salelisting where salelistingid =%s;"
        sql_where=(_salelistingid, )
        cursor.execute(sql,sql_where)

        rec = cursor.fetchone()
        rec =list(rec)
        
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())
        
        cols =[i[0] for i in columns]  
        for col,val in zip(cols,rec):
            listingdetails[col]=val
            image,image_path='','' 
        if (listingdetails['filename']):   
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image

        jsonuser.append(listingdetails)

        if(request.json):
            _json =request.get_json()
            b_in_dict =  "name" in _json
            if b_in_dict:
                _name =_json['name']
                _contact = _json['buyercontact']
                _email = _json['buyeremail']
                _offerprice = _json['offerprice']
                _status= None
                sql ="SELECT salelistingid,sellerid,realtorid from salelisting where salelistingid=%s;"
                sql_where =(_salelistingid,)
                cursor.execute(sql,sql_where)
                rec = cursor.fetchone()
                rec =list(rec)
                print(rec)
                sql_insert ="INSERT into saleapplication(buyerid,buyerrealtorid,salelistingid,sellerid,sellerrealtorid,buyercontact,buyeremail,offerprice,status,name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                sql_insert_where =(id,buyerrelatorid,_salelistingid,rec[1],rec[2],_contact,_email,_offerprice,_status,_name,)
                cursor.execute(sql_insert,sql_insert_where)
                conn.commit()
                
                jsonuser.append({'Note':'Your application has been submitted!'})

                # sender_email = ""
                # receiver_email = ""
                # password = ''

                # message = MIMEMultipart("alternative")
                # message["Subject"] = "APPLICATION FOR YOUR SALE LISTING"
                # message["From"] = sender_email
                # message["To"] = receiver_email

                # # Create the plain-text and HTML version of your message

                # html ="""
                # <html>
                # <head>
                # <style>
                # table, th, td {
                # border: 1px solid black;
                # border-collapse: collapse;
                # }
                # th, td {
                # padding: 5px;
                # text-align: left;
                # }
                # </style>
                # </head>
                # <body>


                # <h2>Sale Application For Your Listing:</h2>
                # <h4></h4>

                # <table style="width:100%">
                # <tr>
                # <th>Name:</th>
                # <td>"""+_name+"""</td>
                # </tr>
                # <tr>
                # <th>Buyer Contact:</th>
                # <td>"""+_contact+"""</td>
                # </tr>
                # <tr>
                # <th>Buyer Email:</th>
                # <td>"""+_email+"""</td>
                # </tr>
                # <tr>
                # <th>Offer Price:</th>
                # <td>"""+_offerprice+"""</td>
                # </tr>
                # <tr>
                # <th>Status:</th>
                # <td>"""+_status+"""</td>
                # </tr>
                # </table>

                # </body>
                # </html>
                # """ 

                # # Turn these into plain/html MIMEText objects
                # #part1 = MIMEText(text, "plain")
                # part2 = MIMEText(html, "html")

                # # Add HTML/plain-text parts to MIMEMultipart message
                # # The email client will try to render the last part first
                # #message.attach(part1)
                # message.attach(part2)

                # # Create secure connection with server and send email
                # context = ssl.create_default_context()
                # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                #     server.login(sender_email, password)
                #     server.sendmail(
                #         sender_email, receiver_email, message.as_string()
                #     )

                # jsonuser.append({'note':'email sent to the Seller.'})
        else:
            jsonuser.append({'Note':' There is errror with the application. it is not filled out'})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        buyerid=0
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql = "SELECT * FROM salelisting where salelistingid =%s;"
        sql_where=(_salelistingid, )
        cursor.execute(sql,sql_where)
        rec = cursor.fetchone()
        rec =list(rec)
        
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())

        cols =[i[0] for i in columns]  
        for col,val in zip(cols,rec):
            listingdetails[col]=val
            image,image_path='',''
        if (listingdetails['filename']):    
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image

        jsonuser.append(listingdetails)

        if(request.data):
            _json =request.get_json()
            b_in_dict =  "name" in _json
            if b_in_dict:
                _name =_json['name']
                _contact = _json['buyercontact']
                _email = _json['buyeremail']
                _offerprice = _json['offerprice']
                _status= None
                sql ="SELECT salelistingid,sellerid,realtorid from salelisting where salelistingid=%s;"
                sql_where =(_salelistingid,)
                cursor.execute(sql,sql_where)
                rec = cursor.fetchone()
                rec =list(rec)
                print(rec)
                sql_insert ="INSERT into saleapplication(buyerid,buyerrealtorid,salelistingid,sellerid,sellerrealtorid,buyercontact,buyeremail,offerprice,status,name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                sql_insert_where =(buyerid,id,_salelistingid,rec[1],rec[2],_contact,_email,_offerprice,_status,_name,)
                cursor.execute(sql_insert,sql_insert_where)
                conn.commit()
                jsonuser.append({'Note':'Your application has been submitted!'})


                sender_email = ""
                receiver_email = ""
                password = ''

                message = MIMEMultipart("alternative")
                message["Subject"] = "APPLICATION FOR YOUR SALE LISTING"
                message["From"] = sender_email
                message["To"] = receiver_email

                # Create the plain-text and HTML version of your message

                html ="""
                <html>
                <head>
                <style>
                table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                }
                th, td {
                padding: 5px;
                text-align: left;
                }
                </style>
                </head>
                <body>


                <h2>Sale Application For Your Listing:</h2>
                <h4></h4>

                <table style="width:100%">
                <tr>
                <th>Name:</th>
                <td>"""+_name+"""</td>
                </tr>
                <tr>
                <th>Buyer Contact:</th>
                <td>"""+_contact+"""</td>
                </tr>
                <tr>
                <th>Buyer Email:</th>
                <td>"""+_email+"""</td>
                </tr>
                <tr>
                <th>Offer Price:</th>
                <td>"""+_offerprice+"""</td>
                </tr>
                <tr>
                <th>Status:</th>
                <td>"""+_status+"""</td>
                </tr>
                </table>

                </body>
                </html>
                """ 

                # Turn these into plain/html MIMEText objects
                #part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")

                # Add HTML/plain-text parts to MIMEMultipart message
                # The email client will try to render the last part first
                #message.attach(part1)
                message.attach(part2)

                # Create secure connection with server and send email
                #context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, receiver_email, message.as_string()
                    )

                jsonuser.append({'note':'email sent to the Seller.'})
            
        else:
            jsonuser.append({'Note':' There is errror with the application. it is out filled out'})

    return jsonify(jsonuser)


def buyerInbox(id):
    listingdetails ={}
    _application=[]
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]


    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='buyer':
        buyerid = activeuserid
        _buyerfirstname=activeusername
        jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'})

        sql ="select * from saleapplication where buyerid=%s and status is not null;"
        sql_where= (id,)
        cursor.execute(sql,sql_where)
        records = cursor.fetchall()
        records=list(records)
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='saleapplication';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _application.append(_list)   
        jsonuser.append({'Applications':_application})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql ="select * from saleapplication where buyerrealtorid=%s and status is not null;"
        sql_where= (id,)
        cursor.execute(sql,sql_where)
        records = cursor.fetchall()
        records=list(records)
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='saleapplication';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _application.append(_list)   
        jsonuser.append({'Applications':_application})

    return jsonify(jsonuser)

def buyerPending(id):
    listingdetails ={}
    _application=[]
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]


    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'seller' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='buyer':
        buyerid = activeuserid
        _buyerfirstname=activeusername
        jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'})

        sql ="select * from saleapplication where buyerid=%s and status is null;"
        sql_where= (id,)
        cursor.execute(sql,sql_where)
        records = cursor.fetchall()
        records=list(records)
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='saleapplication';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _application.append(_list)   
        jsonuser.append({'Applications':_application})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql ="select * from saleapplication where buyerrealtorid=%s and status is null;"
        sql_where= (id,)
        cursor.execute(sql,sql_where)
        records = cursor.fetchall()
        records=list(records)
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='saleapplication';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _application.append(_list)   
        jsonuser.append({'Applications':_application})

    return jsonify(jsonuser)



######################################################## R E N T A L S  M O D E L ########################################################## 

def createRentalListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        _landlordid = landlordid
        _realtorid= 0
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= 'open'
            _price = _form['price']
            _leaseterms = _form['leaseterms']
            _availabilitydate= _form['availabilitydate']
            _securitydeposit = _form['securitydeposit']
            _visits=_form['visits']
            filename=None
            image=''

            if request.files:
                image = request.files['image']
                if image and valid_file(image.filename):
                    filename = secure_filename(image.filename)
                    print(UPLOAD_FOLDER)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            sql = "INSERT INTO rentlisting (address,zipcode,area,noofbedrooms,noofbathrooms,hometype,parkingtype,yearbuilt,status,price,leaseterms,availabilitydate,securitydeposit,landlordid,realtorid,openhouse,filename) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            sql_insert=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price, _leaseterms, _availabilitydate, _securitydeposit, id, _realtorid, _visits, filename,)
            cursor.execute(sql,sql_insert)
            conn.commit()
            jsonuser.append({'Notification' : 'Your listing has been added successfully'})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        _realtorid = realtorid
        _landlordid= 0
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= 'open'
            _price = _form['price']
            _leaseterms = _form['leaseterms']
            _availabilitydate= _form['availabilitydate']
            _securitydeposit = _form['securitydeposit']
            _visits=_form['visits']
            filename=None
            image=''

            if request.files:
                image = request.files['image']
                if image and valid_file(image.filename):
                    filename = secure_filename(image.filename)
                    print(UPLOAD_FOLDER)
                    print(filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            sql = "INSERT INTO rentlisting (address,zipcode,area,noofbedrooms,noofbathrooms,hometype,parkingtype,yearbuilt,status,price,leaseterms,availabilitydate,securitydeposit,landlordid,realtorid,openhouse,filename) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            sql_insert=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price, _leaseterms, _availabilitydate, _securitydeposit, _landlordid,id,_visits,filename,)
            cursor.execute(sql,sql_insert)
            conn.commit()
            jsonuser.append({'Notification' : 'Your listing has been added successfully'})

    return jsonify(jsonuser)

def valid_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ViewRentalApplications(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]
        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _rentlistingid=_json['rentlistingid']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})
        sql = "SELECT * FROM rentapplication WHERE status IS NULL AND landlordid=%s AND rentlistingid=%s"
    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
        sql = "SELECT * FROM rentapplication WHERE status IS NULL AND realtorid=%s AND rentlistingid=%s"

    sql_where = (id,_rentlistingid,)
    cursor.execute(sql, sql_where)
    records= cursor.fetchall()

    for row in records:
        _rentapplicationid=row[0]
        _name=row[9]
        _contactphone=row[5]
        _email=row[6]
        _creditscore=row[7]
        _employmentinfo=row[8]

        jsonuser.append({'applicationid' : _rentapplicationid,
        'name' : _name, 
        'phone' : _contactphone, 
        'email' : _email, 
        'creditscore' : _creditscore, 
        'employmentinfo' : _employmentinfo, 
        'Option' : 'Approve / Reject'})

    return jsonify(jsonuser)


def selectRentalApplication(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _rentapplicationid=_json['applicationid']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})
        sql = "SELECT * FROM rentapplication WHERE rentapplicationid=%s AND landlordid=%s"
    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
        sql = "SELECT * FROM rentapplication WHERE rentapplicationid=%s AND realtorid=%s"

    sql_where = (_rentapplicationid,id,)
    cursor.execute(sql, sql_where)
    row= cursor.fetchone()

    _rentapplicationid=row[0]
    _name=row[9]
    _contactphone=row[5]
    _email=row[6]
    _creditscore=row[7]
    _employmentinfo=row[8]

    jsonuser.append({'applicationid' : _rentapplicationid,
    'name' : _name, 
    'phone' : _contactphone, 
    'email' : _email, 
    'creditscore' : _creditscore, 
    'employmentinfo' : _employmentinfo, 
    'Option' : 'Approve / Reject'})

    return jsonify(jsonuser)


def ViewMyRentalListings(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    _listings=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]
    
        if usertype=='landlord':
            landlordid = activeuserid
            _landlordfirstname=activeusername
            jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})
            sql = "SELECT * FROM rentlisting WHERE landlordid=%s"
        else:
            realtorid = activeuserid
            _realtorfirstname=activeusername
            jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})
            sql = "SELECT * FROM rentlisting WHERE realtorid=%s"

        sql_where = (id,)
        cursor.execute(sql, sql_where)

        records = cursor.fetchall()
        records=list(records)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())

        cols =[i[0] for i in columns]   
        for record in records:
            _list, image={},''
            image_path=''
            for col,val in zip(cols,record):
                _list[col]=val
            if (record[-1]):
                print(str(record[-1]))    
                image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
                image = get_image(image_path)
            _list['image']= image

            #print(image_path)
            _listings.append(_list)
            _listings.append('options :Remove Rental Listing /Update Listing/ View applications for this Listing')

        jsonuser.append({'rental listings':_listings})
    return jsonify(jsonuser)


def approveRentalApplication(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _applicationid=_json['applicationid']
    _message=_json['messagetorenter']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})

        sql = "SELECT * FROM rentapplication WHERE landlordid=%s AND rentapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[9]

        updatesql = "UPDATE rentapplication SET status=true WHERE landlordid=%s AND rentapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE rentapplication SET message=%s WHERE landlordid=%s AND rentapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified about the approval'})

    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql = "SELECT * FROM rentapplication WHERE realtorid=%s AND rentapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[9]

        updatesql = "UPDATE rentapplication SET status=true WHERE realtorid=%s AND rentapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE rentapplication SET message=%s WHERE realtorid=%s AND rentapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified about the approval'})

    return jsonify(jsonuser)


def rejectRentalApplication(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the application id
    _json = request.get_json()
    _applicationid=_json['applicationid']
    _message=_json['messagetorenter']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})

        sql = "SELECT * FROM rentapplication WHERE landlordid=%s AND rentapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[9]

        updatesql = "UPDATE rentapplication SET status=false WHERE landlordid=%s AND rentapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE rentapplication SET message=%s WHERE landlordid=%s AND rentapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified that their application is rejected'})

    else:
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql = "SELECT * FROM rentapplication WHERE realtorid=%s AND rentapplicationid=%s"
        sql_where = (id,_applicationid,)
        cursor.execute(sql, sql_where)
        row= cursor.fetchone()
        name=row[9]

        updatesql = "UPDATE rentapplication SET status=false WHERE realtorid=%s AND rentapplicationid=%s"
        updatesql_where = (id,_applicationid,)
        cursor.execute(updatesql, updatesql_where)
        conn.commit()

        messagesql = "UPDATE rentapplication SET message=%s WHERE realtorid=%s AND rentapplicationid=%s"
        messagesql_where = (_message,id,_applicationid,)
        cursor.execute(messagesql, messagesql_where)
        conn.commit()

        jsonuser.append({'notification' : name + ' has been notified that their application is rejected'})

    return jsonify(jsonuser)


def updateRentalListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get listing id
    form = request.form
    _rentlistingid=form['rentlistingid']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        _landlordid = landlordid
        _realtorid= 0
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= _form['status']
            _price = _form['price']
            _leaseterms = _form['leaseterms']
            _availabilitydate= _form['availabilitydate']
            _securitydeposit = _form['securitydeposit']

        if _address and _zipcode and _area and _noofbedrooms and _noofbathrooms and _hometype and _parkingtype and _yearbuilt and _status and _price and _leaseterms and _availabilitydate and _securitydeposit and (_landlordid or _realtorid):
            cursor = conn.cursor()
            sql = "UPDATE rentlisting SET address=%s,zipcode=%s,area=%s,noofbedrooms=%s,noofbathrooms=%s,hometype=%s,parkingtype=%s,yearbuilt=%s,status=%s,price=%s,leaseterms=%s,availabilitydate=%s,securitydeposit=%s,landlordid=%s,realtorid=%s WHERE rentlistingid =%s;"
            sql_where=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price, _leaseterms, _availabilitydate, _securitydeposit, id, _realtorid, _rentlistingid)
            cursor.execute(sql,sql_where)
            conn.commit()

            jsonuser.append({'Notification':'listing updated successfully'})
        else:
            jsonuser.append({'Warning' : 'Please fill out the details'})

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        _realtorid = realtorid
        _landlordid= 0
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        if(request.form):
            _form = request.form.to_dict()
            _address = _form['address']
            _zipcode = _form['zipcode']
            _area =_form['area']
            _noofbedrooms = _form['noofbedrooms']
            _noofbathrooms = _form['noofbathrooms']
            _hometype = _form['hometype']
            _parkingtype = _form['parkingtype']
            _yearbuilt = _form['yearbuilt']
            _status= _form['status']
            _price = _form['price']
            _leaseterms = _form['leaseterms']
            _availabilitydate= _form['availabilitydate']
            _securitydeposit = _form['securitydeposit']

            if _address and _zipcode and _area and _noofbedrooms and _noofbathrooms and _hometype and _parkingtype and _yearbuilt and _status and _price and _leaseterms and _availabilitydate and _securitydeposit and (_landlordid or _realtorid):
                cursor = conn.cursor()
                sql = "UPDATE rentlisting SET address=%s,zipcode=%s,area=%s,noofbedrooms=%s,noofbathrooms=%s,hometype=%s,parkingtype=%s,yearbuilt=%s,status=%s,price=%s,leaseterms=%s,availabilitydate=%s,securitydeposit=%s,landlordid=%s,realtorid=%s WHERE rentlistingid =%s;"
                sql_where=(_address, _zipcode, _area, _noofbedrooms, _noofbathrooms, _hometype, _parkingtype, _yearbuilt, _status, _price, _leaseterms, _availabilitydate, _securitydeposit, _landlordid, id, _rentlistingid)
                cursor.execute(sql,sql_where)
                conn.commit()

                jsonuser.append({'Notification':'listing updated successfully'})
            else:
                jsonuser.append({'Warning' : 'Please fill out the details'})

    return jsonify(jsonuser)


def deleteRentListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the listing id
    _json = request.get_json()
    _rentlistingid=_json['rentlistingid']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})

        sql_select = "SELECT * FROM rentlisting where rentlistingid =%s AND landlordid=%s"
        sql_select_where= (_rentlistingid,id,)
        cursor.execute(sql_select,sql_select_where)
        rec = cursor.fetchone()
        print(rec)
        if rec:
            sql_delete = "DELETE FROM rentlisting WHERE rentlistingid=%s AND landlordid=%s"
            sql_delete_where = (_rentlistingid,id,)
            cursor.execute(sql_delete, sql_delete_where)
            conn.commit()
            #cursor.close()
        else:
            jsonuser.append({'Warning':'Your listing does not exist'})

        jsonuser.append({'Notification':'Your listing has been deleted'})


    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql_select = "SELECT * FROM rentlisting where rentlistingid =%s AND realtorid=%s"
        sql_select_where= (_rentlistingid,id,)
        cursor.execute(sql_select,sql_select_where)
        rec = cursor.fetchone()
        print(rec)
        if rec:
            sql_delete = "DELETE FROM rentlisting WHERE rentlistingid=%s AND realtorid=%s"
            sql_delete_where = (_rentlistingid,id,)
            cursor.execute(sql_delete, sql_delete_where)
            conn.commit()
            jsonuser.append({'Notification':'Your listing has been deleted'})
            #cursor.close()
        else:
            jsonuser.append({'Warning':'Your listing does not exist'})

    return jsonify(jsonuser)

def get_image(image_path):
    pil_img = Image.open(image_path, mode='r')
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img 


def displaySelectedRentListing(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    listingdetails={}

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'landlord' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]
    

    #get the listing id
    _json = request.get_json()
    _rentlistingid=_json['rentlistingid']

    if usertype=='landlord':
        landlordid = activeuserid
        _landlordfirstname=activeusername
        jsonuser.append({landlordid: 'id', _landlordfirstname : 'name'})
        
        sql_select = "SELECT * FROM rentlisting where rentlistingid =%s AND landlordid=%s"
        sql_select_where= (_rentlistingid,id,)
        cursor.execute(sql_select, sql_select_where)

        rec = cursor.fetchone()
        rec =list(rec)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for col,val in zip(cols,rec):
            image, image_path='',''
            listingdetails[col]=val 
        if (listingdetails['filename']):
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image
        
        jsonuser.append(listingdetails)
  

    if usertype=='realtor':
        realtorid = activeuserid
        _realtorfirstname=activeusername
        jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'})

        sql_select = "SELECT * FROM rentlisting where rentlistingid =%s AND realtorid=%s"
        sql_select_where= (_rentlistingid,id,)
        cursor.execute(sql_select, sql_select_where)

        rec = cursor.fetchone()
        rec =list(rec)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for col,val in zip(cols,rec):
            image, image_path='',''
            listingdetails[col]=val 
        if (listingdetails['filename']):
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image
        
        jsonuser.append(listingdetails)

    return jsonify(jsonuser)

def renterHomePage(id):
    _listings=[]
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'renter' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='renter':
        renterid = activeuserid
        _renterfirstname=activeusername
        jsonuser.append({renterid: 'id', _renterfirstname : 'name'})

        sql ="select * from rentlisting;"
        cursor.execute(sql)
        records = cursor.fetchall()
        records=list(records)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            image,image_path='',''
            for col,val in zip(cols,record):
                _list[col]=val  
            if (record[-1]):
                print(str(record[-1]))    
                image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
                image = get_image(image_path)  
            _list['image']= image
            #print(image_path)
            _listings.append(_list)

        jsonuser.append({'rental listings':_listings})
    
    return jsonify(jsonuser)


def renterReviewListing(id):
    listingdetails ={}
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'renter' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    #get the listing id
    _json = request.get_json()
    _rentlistingid=_json['rentlistingid']

    if usertype=='renter':
        renterid = activeuserid
        _renterfirstname=activeusername
        jsonuser.append({renterid: 'id', _renterfirstname : 'name'})
        
        sql_select = "SELECT * FROM rentlisting where rentlistingid =%s"
        sql_select_where= (_rentlistingid,)
        cursor.execute(sql_select, sql_select_where)
        rec = cursor.fetchone()
        rec =list(rec)

        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
        cursor.execute(sql_column)
        columns=(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for col,val in zip(cols,rec):
            listingdetails[col]=val 
            image,image_path='',''
        if (listingdetails['filename']):   
            image_path = os.getcwd()+'/'+'uploads'+'/'+ listingdetails['filename']
            image = get_image(image_path)
        listingdetails['image']= image

        jsonuser.append(listingdetails)

        if(request.json):
            b_in_dict =  "name" in _json
            if b_in_dict:
                _name =_json['name']
                _contact = _json['rentercontact']
                _email = _json['renteremail']
                _creditscore = _json['creditscore']
                _empinfo = _json['employmentinfo']
                sql ="SELECT rentlistingid,landlordid,realtorid from rentlisting where rentlistingid=%s;"
                sql_where =(_rentlistingid,)
                cursor.execute(sql,sql_where)
                rec = cursor.fetchone()
                rec =list(rec)
                sql_insert ="INSERT into rentapplication(renterid,rentlistingid,landlordid,realtorid,rentercontact,renteremail,creditscore,employmentinfo,rentername) values(%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                sql_insert_where =(id,_rentlistingid,rec[1],rec[2],_contact,_email,_creditscore,_empinfo,_name,)
                cursor.execute(sql_insert,sql_insert_where)
                conn.commit()

                jsonuser.append({'Note':'Your application has been submitted!'})

                # sender_email = ""
                # receiver_email = ""
                # password = ''

                # message = MIMEMultipart("alternative")
                # message["Subject"] = "APPLICATION FOR YOUR SALE LISTING"
                # message["From"] = sender_email
                # message["To"] = receiver_email

                # # Create the plain-text and HTML version of your message

                # html ="""
                # <html>
                # <head>
                # <style>
                # table, th, td {
                # border: 1px solid black;
                # border-collapse: collapse;
                # }
                # th, td {
                # padding: 5px;
                # text-align: left;
                # }
                # </style>
                # </head>
                # <body>


                # <h2>Sale Application For Your Listing:</h2>
                # <h4></h4>

                # <table style="width:100%">
                # <tr>
                # <th>Name:</th>
                # <td>"""+_name+"""</td>
                # </tr>
                # <tr>
                # <th>Renter Contact:</th>
                # <td>"""+_contact+"""</td>
                # </tr>
                # <tr>
                # <th>Renter Email:</th>
                # <td>"""+_email+"""</td>
                # </tr>
                # <tr>
                # <th>Credit score:</th>
                # <td>"""+_creditscore+"""</td>
                # </tr>
                # <tr>
                # <th>Emp info:</th>
                # <td>"""+_empinfo+"""</td>
                # </tr>
                # </table>

                # </body>
                # </html>
                # """ 

                # # Turn these into plain/html MIMEText objects
                # #part1 = MIMEText(text, "plain")
                # part2 = MIMEText(html, "html")

                # # Add HTML/plain-text parts to MIMEMultipart message
                # # The email client will try to render the last part first
                # #message.attach(part1)
                # message.attach(part2)

                # # Create secure connection with server and send email
                # context = ssl.create_default_context()
                # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                #     server.login(sender_email, password)
                #     server.sendmail(
                #         sender_email, receiver_email, message.as_string()
                #     )

                # jsonuser.append({'note':'email sent to the Seller.'})
            
        else:
            jsonuser.append({'Note':' There is errror with the application. it is not filled out'})

    return jsonify(jsonuser)


def renterInbox(id): 
    listingdetails ={}
    _application=[]
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'renter' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='renter':
        renterid = activeuserid
        _renterfirstname=activeusername
        jsonuser.append({renterid: 'id', _renterfirstname : 'name'})

        sql ="select * from rentapplication where renterid=%s and status is not null;"
        sql_where= (id,)
        cursor.execute(sql,sql_where)
        records = cursor.fetchall()
        records=list(records)
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentapplication';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _application.append(_list)   
        jsonuser.append({'Applications':_application})

    return jsonify(jsonuser)

def renterPending(id): 
    listingdetails ={}
    _application=[]
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)
    

    #if 'renter' in session:
    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]

        usertype=row[8]

    if usertype=='renter':
        renterid = activeuserid
        _renterfirstname=activeusername
        jsonuser.append({renterid: 'id', _renterfirstname : 'name'})

        sql ="select * from rentapplication where renterid=%s and status is null;"
        sql_where= (id,)
        cursor.execute(sql,sql_where)
        records = cursor.fetchall()
        records=list(records)
        sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentapplication';"
        cursor.execute(sql_column)
        columns=list(cursor.fetchall())
        
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _application.append(_list)   
        jsonuser.append({'Applications':_application})

    return jsonify(jsonuser)


######################################################## F A V O R I T E S,  S E A R C H,  M A I N - P A G E  A P I s ##########################################################



#HOME FOR ALL
def homeForAll():
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    _listings=[]

    sql ="select * from rentlisting;"
    cursor.execute(sql)
    records = cursor.fetchall()
    records=list(records)

    sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
    cursor.execute(sql_column)
    columns=list(cursor.fetchall())

    cols =[i[0] for i in columns]   
    for record in records:
        _list={}
        image,image_path='',''
        for col,val in zip(cols,record):
            _list[col]=val
        if (record[-1]):
            print(str(record[-1]))    
            image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
            image = get_image(image_path)    
        _list['image']= image
        #print(image_path)
        _listings.append(_list)

    jsonuser.append({'rental listings':_listings})

    sql ="select * from salelisting;"
    cursor.execute(sql)
    records = cursor.fetchall()
    records=list(records)

    sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
    cursor.execute(sql_column)
    columns=list(cursor.fetchall())

    cols =[i[0] for i in columns]   
    for record in records:
        _list={}
        image,image_path='',''
        for col,val in zip(cols,record):
            _list[col]=val  
        if (record[-1]):
            print(str(record[-1]))    
            image_path = os.getcwd()+'/'+'uploads'+'/'+ str(record[-1])
            image = get_image(image_path)  
        _list['image']= image
        _listings.append(_list)

    jsonuser.append({'sale listings':_listings})

    return jsonify(jsonuser)


def addToFavorites(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    rid=0
    sid=0

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)

    #get the listing id
    _json = request.get_json()
    _listingid=_json['listingid']

    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]
        _usertype=row[8]

        if _usertype =='renter':
            renterid = activeuserid
            _renterfirstname=activeusername
            jsonuser.append({renterid: 'id', _renterfirstname : 'name'}) 
            rid=_listingid 

        if _usertype=='buyer':
            buyerid = activeuserid
            _buyerfirstname=activeusername
            jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'}) 
            sid= _listingid

        if _usertype=='realtor':
            realtorid = activeuserid
            _realtorfirstname=activeusername
            jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'}) 
            sid= _listingid

        sql = "Insert into favorites(userid, usertype, rentlistingid, salelistingid) values(%s,%s,%s,%s);"
        sql_where =(id,_usertype,rid,sid,)
        cursor.execute(sql,sql_where)
        conn.commit()
        jsonuser.append({'Note':'Listing has been favorited!'})
    else:
        jsonuser.append({'Error':'cant add to favorites at this time'})

    return jsonify(jsonuser)


def removeFromFav(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    rid=0
    sid=0

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)

    #get the listing id
    _json = request.get_json()
    _listingid=_json['listingid']

    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]
        _usertype=row[8]


        if _usertype =='renter':
            renterid = activeuserid
            _renterfirstname=activeusername
            jsonuser.append({renterid: 'id', _renterfirstname : 'name'}) 
            rid=_listingid 

        if _usertype=='buyer':
            buyerid = activeuserid
            _buyerfirstname=activeusername
            jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'}) 
            sid= _listingid

        if _usertype=='realtor':
            realtorid = activeuserid
            _realtorfirstname=activeusername
            jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'}) 
            sid= _listingid

        sql = "DELETE from favorites where userid=%s and usertype=%s and rentlistingid=%s and salelistingid=%s ;"
        sql_where =(id,_usertype,rid,sid,)
        cursor.execute(sql,sql_where)
        conn.commit()
        jsonuser.append({'Note':'Listing has been removed from favorites!'})
    
    return jsonify(jsonuser)

def viewFav(id):
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    _favorites=[]

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)

    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]
        _usertype=row[8]

        if _usertype =='renter':
            renterid = activeuserid
            _renterfirstname=activeusername
            jsonuser.append({renterid: 'id', _renterfirstname : 'name'}) 
            
            sql = "select * from rentlisting where rentlistingid in (select rentlistingid from favorites where userid =%s);"
            sql_where =(id,)
            cursor.execute(sql,sql_where)
            records = cursor.fetchall()
            records=list(records)
            sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
            cursor.execute(sql_column)
            columns=list(cursor.fetchall())

        if _usertype=='buyer':
            buyerid = activeuserid
            _buyerfirstname=activeusername
            jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'}) 
            
            sql = "select * from salelisting where salelistingid in (select salelistingid from favorites where userid =%s);"
            sql_where =(id,)
            cursor.execute(sql,sql_where)
            records = cursor.fetchall()
            records=list(records)
            sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
            cursor.execute(sql_column)
            columns=list(cursor.fetchall())

        if _usertype=='realtor':
            realtorid = activeuserid
            _realtorfirstname=activeusername
            jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'}) 
            
            sql = "select * from salelisting where salelistingid in (select salelistingid from favorites where userid =%s);"
            sql_where =(id,)
            cursor.execute(sql,sql_where)
            records = cursor.fetchall()
            records=list(records)
            sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
            cursor.execute(sql_column)
            columns=list(cursor.fetchall())

        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _favorites.append(_list)   
        jsonuser.append({'Favorites':_favorites})
    else:
        jsonuser.append({'Error message' : 'Please login to view your favorites!'})
    
    return jsonify(jsonuser)

def searchItAll():
    cursor = None
    cursor = conn.cursor()
    sql=''
    jsonuser=[]
    _listings= []
    res= None

    #if 'user' in session:
    print("this is "+str(loggedinid))

    count= cursor.execute("SELECT * FROM users WHERE isactive=true AND userid=%s",[loggedinid])
    print(count)

    if count==1:
        row = cursor.fetchone()
        activeuserid=str(row[0])
        activeusername=row[1]
        _usertype=row[8]

        if _usertype =='renter' or _usertype=='landlord':
            renterid = activeuserid
            _renterfirstname=activeusername
            jsonuser.append({renterid: 'id', _renterfirstname : 'name'})

            _json = request.get_json()
            _address = _json['address']
            _zipcode = _json['zipcode']
            _area =_json['area']
            _noofbedrooms = _json['noofbedrooms'] if _json['noofbedrooms'] else 'null'
            _noofbathrooms = _json['noofbathrooms'] if _json['noofbathrooms'] else 'null'
            _hometype = _json['hometype'] if _json['hometype'] else 'null'
            _parkingtype = _json['parkingtype'] if _json['parkingtype'] else 'null'
            _yearbuilt = _json['yearbuilt'] if _json['yearbuilt'] else 'null'
            _status= _json['status'] if _json['status'] else 'null'
            _pricemin = _json['pricemin'] if _json['pricemin'] else 'null'
            _pricemax = _json['pricemax'] if _json['pricemax']  else 'null'
            _leaseterms = _json['leaseterms'] if _json['leaseterms'] else 'null'
            _availabilitydate= _json['availabilitydate'] if _json['availabilitydate'] else 'null'
            _securitydeposit = _json['securitydeposit'] if _json['securitydeposit'] else 'null'
            cursor = conn.cursor()

            sql = "select * from rentlisting where address like '%{}%' and zipcode like '{}%' and area like '%{}%' and noofbedrooms like ifnull({},'%') and noofbathrooms like ifnull({},'%') and hometype like ifnull({},'%') and parkingtype like ifnull({},'%') and yearbuilt>ifnull({},'%') and price between ifnull({},0) and ifnull({},100000000000000) and leaseterms like ifnull({},'%') and availabilitydate like ifnull({},'%') and securitydeposit like ifnull({},'%') and status like ifnull({},'%');".format(_address,_zipcode,_area, _noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuilt,_pricemin,_pricemax,_leaseterms,_availabilitydate,_securitydeposit,_status)
            #sql_where=(_zipcode,_area,_noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuiltfrom,_yearbuiltto,_status,_price_from,_price_to,_leaseterms,_availabilitydate, _securitydeposit,)
            cursor.execute(sql,)
            records = cursor.fetchall()
            records=list(records)
            sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
            cursor.execute(sql_column)
            columns=list(cursor.fetchall())
            #print(records)
            #print(columns)

        if _usertype=='buyer' or _usertype=='seller':
            buyerid = activeuserid
            _buyerfirstname=activeusername
            jsonuser.append({buyerid: 'id', _buyerfirstname : 'name'}) 

            _json = request.get_json()
            _address = _json['address']
            _zipcode = _json['zipcode'] 
            _area =_json['area'] 
            _noofbedrooms = _json['noofbedrooms'] if _json['noofbedrooms'] else 'null'
            _noofbathrooms = _json['noofbathrooms'] if _json['noofbathrooms'] else 'null'
            _hometype = _json['hometype'] if _json['hometype'] else 'null'
            _parkingtype = _json['parkingtype'] if _json['parkingtype'] else 'null'
            _yearbuilt= _json['yearbuilt'] if _json['yearbuilt'] else 'null'
            #_yearbuiltto = _json['yearbuiltto']
            _status= _json['status'] if _json['status'] else 'null'
            _pricemin = _json['pricemin'] if _json['pricemin'] else 'null'
            _pricemax = _json['pricemax'] if _json['pricemax'] else 'null'
            cursor = conn.cursor()

            sql = "select * from salelisting where address like '%{}%' and zipcode like '{}%' and area like '%{}%' and noofbedrooms like ifnull({},'%') and noofbathrooms like ifnull({},'%') and hometype like ifnull({},'%') and parkingtype like ifnull({},'%') and yearbuilt>ifnull({},'%') and price between ifnull({},0) and ifnull({},100000000000000) and status like ifnull({},'%');".format(_address,_zipcode,_area, _noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuilt,_pricemin,_pricemax,_status)
            #print(sql)
            #sql_where=(_zipcode, _noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuiltfrom,_yearbuiltto,_status, )
            cursor.execute(sql)
            records = cursor.fetchall()
            records=list(records)
            sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
            cursor.execute(sql_column)
            columns=list(cursor.fetchall())  
            #print(records)
            #print(columns)

        if _usertype=='realtor':
            realtorid = activeuserid
            _realtorfirstname=activeusername
            jsonuser.append({realtorid: 'id', _realtorfirstname : 'name'}) 

            _json = request.get_json()
            if _json['option']=="rent":
                _address = _json['address']
                _zipcode = _json['zipcode']
                _area =_json['area']
                _noofbedrooms = _json['noofbedrooms'] if _json['noofbedrooms'] else 'null'
                _noofbathrooms = _json['noofbathrooms'] if _json['noofbathrooms'] else 'null'
                _hometype = _json['hometype'] if _json['hometype'] else 'null'
                _parkingtype = _json['parkingtype'] if _json['parkingtype'] else 'null'
                _yearbuilt = _json['yearbuilt'] if _json['yearbuilt'] else 'null'
                _status= _json['status'] if _json['status'] else 'null'
                _pricemin = _json['pricemin'] if _json['pricemin'] else 'null'
                _pricemax = _json['pricemax'] if _json['pricemax']  else 'null'
                _leaseterms = _json['leaseterms'] if _json['leaseterms'] else 'null'
                _availabilitydate= _json['availabilitydate'] if _json['availabilitydate'] else 'null'
                _securitydeposit = _json['securitydeposit'] if _json['securitydeposit'] else 'null'
                _option =_json['option']
                cursor = conn.cursor()

                sql = "select * from rentlisting where address like '%{}%' and zipcode like '{}%' and area like '%{}%' and noofbedrooms like ifnull({},'%') and noofbathrooms like ifnull({},'%') and hometype like ifnull({},'%') and parkingtype like ifnull({},'%') and yearbuilt>ifnull({},'%') and price between ifnull({},0) and ifnull({},100000000000000) and leaseterms like ifnull({},'%') and availabilitydate like ifnull({},'%') and securitydeposit like ifnull({},'%') and status like ifnull({},'%');".format(_address,_zipcode,_area, _noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuilt,_pricemin,_pricemax,_leaseterms,_availabilitydate,_securitydeposit,_status)
                #sql_where=(_zipcode,_area,_noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuiltfrom,_yearbuiltto,_status,_price_from,_price_to,_leaseterms,_availabilitydate, _securitydeposit,)
                cursor.execute(sql,)
                records = cursor.fetchall()
                records=list(records)
                sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='rentlisting';"
                cursor.execute(sql_column)
                columns=list(cursor.fetchall())
                #print(records)
                #print(columns)
            
            elif _json['option']== "buy":
                _address = _json['address']
                _zipcode = _json['zipcode'] 
                _area =_json['area'] 
                _noofbedrooms = _json['noofbedrooms'] if _json['noofbedrooms'] else 'null'
                _noofbathrooms = _json['noofbathrooms'] if _json['noofbathrooms'] else 'null'
                _hometype = _json['hometype'] if _json['hometype'] else 'null'
                _parkingtype = _json['parkingtype'] if _json['parkingtype'] else 'null'
                _yearbuilt= _json['yearbuilt'] if _json['yearbuilt'] else 'null'
                #_yearbuiltto = _json['yearbuiltto']
                _status= _json['status'] if _json['status'] else 'null'
                _pricemin = _json['pricemin'] if _json['pricemin'] else 'null'
                _pricemax = _json['pricemax'] if _json['pricemax'] else 'null'
                _option =_json['option'] 
                cursor = conn.cursor()

                sql = "select * from salelisting where address like '%{}%' and zipcode like '{}%' and area like '%{}%' and noofbedrooms like ifnull({},'%') and noofbathrooms like ifnull({},'%') and hometype like ifnull({},'%') and parkingtype like ifnull({},'%') and yearbuilt>ifnull({},'%') and price between ifnull({},0) and ifnull({},100000000000000) and status like ifnull({},'%');".format(_address,_zipcode,_area, _noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuilt,_pricemin,_pricemax,_status)
                #print(sql)
                #sql_where=(_zipcode, _noofbedrooms,_noofbathrooms,_hometype,_parkingtype,_yearbuiltfrom,_yearbuiltto,_status, )
                cursor.execute(sql)
                records = cursor.fetchall()
                records=list(records)
                sql_column ="SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='homefinder' AND `TABLE_NAME`='salelisting';"
                cursor.execute(sql_column)
                columns=list(cursor.fetchall())  
                #print(records)
                #print(columns)
        
        else:
            jsonuser.append({"message" : "Error searching"})
        
        #print("Here we are!")
        cols =[i[0] for i in columns]   
        for record in records:
            _list={}
            for col,val in zip(cols,record):
                _list[col]=val    
            _listings.append(_list)   
        jsonuser.append({'Listings':_listings})

    return jsonify(jsonuser)

###################################################################################################
###################### T E S T I N G  -   M A I N     M E T H O D   A P P   R U N #################
###################################################################################################
       		
if __name__ == "__main__":
    app.run()

###################################################################################################
###################### T E S T I N G  - A L R E A D Y    C A L L E D   A B O V E ##################
###################################################################################################
