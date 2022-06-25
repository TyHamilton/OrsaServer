
import email
import os
from io import BytesIO
import random
from tkinter import Image

from flask import Flask, make_response, redirect, render_template, request, send_file,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import hashlib
import qrcode  
Image  


from sqlalchemy import BLOB, desc, null 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///starter.db'

db = SQLAlchemy(app)
format = '%m/%d/%Y'
salt = b'\xfe\x11i]h\xf7\xfe,\xdbp|&#\xa9B'

class obToPing():
    didIrespond=False
    def __init__(self,name, ip):
        self.name=name
        self.ip= ip
        

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fName = db.Column(db.String(255),nullable =False)
    lName= db.Column(db.String(255),nullable=False)
    pin = db.Column(db.Integer, default =0)
    hashID = db.Column(db.String(255),default ="")
    photoID = db.Column(db.String(255),default ="")
    email = db.Column(db.String(255),default ="")
    phone = db.Column(db.String(255),default ="")
    DateOfB = db.Column(db.String(255),nullable=False)
    LastClock = db.Column(db.String(255),default ="")
    createdDate = db.Column(db.DateTime,default = datetime.utcnow)
    TermDate = db.Column(db.DateTime,default = datetime.utcnow)
    disabled = db.Column(db.Integer, default =0)
    dataReserve1 = db.Column(db.Integer, default =0) 
    dataReserve2 = db.Column(db.String(255),default ="") 
    dataReserve3= db.Column(db.String(255),default ="")
    dataReserve4 = db.Column(db.String(255),default ="")#lastStatus
    photoBlob = db.Column(db.BLOB, nullable =True)
    qrBlob = db.Column(db.BLOB, nullable =True)


    def __repr__(self):
        return '<Employee %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName =db.Column(db.String(255),nullable =False,unique=True)
    fName = db.Column(db.String(255),nullable =False)
    lName= db.Column(db.String(255),nullable=False)
    password = db.Column(db.String(255),default ="")
    email = db.Column(db.String(255),default ="")
    phone = db.Column(db.String(255),default ="")
    admin = db.Column(db.Integer, default =0)
    manager = db.Column(db.Integer, default =0)
    createdDate = db.Column(db.DateTime,default = datetime.utcnow)
    termDate = db.Column(db.DateTime,default = datetime.utcnow)
    disabled = db.Column(db.Integer, default =0)
    dataReserve1 = db.Column(db.Integer, default =0) #phone
    dataReserve2 = db.Column(db.String(255),default ="")
    dataReserve3= db.Column(db.String(255),default ="")
    dataReserve4 = db.Column(db.String(255),default ="")

    def __repr__(self):
        return '<User %r>' % self.id
    
#source env/bin/activate
#python3
#from app import db 
#db.create_all()

class ClickInOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer)
    createdDate = db.Column(db.DateTime,default = datetime.utcnow)
    timeStamp = db.Column(db.String(255),nullable=False)
    inOut = db.Column(db.String(255),nullable=False)
    photoLoc = db.Column(db.String(255),default ="")
    photoBlob = db.Column(db.BLOB, nullable =True)
       
    def __repr__(self):
        return '<CheckInOut %r>' % self.id

class LogView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    createdDate = db.Column(db.DateTime,default = datetime.utcnow)
    log = db.Column(db.String(255),nullable=False)

    def __repr__(self):
        return '<LogView %r>' % self.id


@app.route('/', methods=['POST','GET'])
def index():
    if request.method =='POST':
        print("Post")
    else:
        print("Get")

    emp_Fetch = Employee.query.filter_by(disabled=0)
    return render_template('index.html',emps =emp_Fetch)

@app.route("/PingStuff")
def pingStuff():
    hosts = getHosts()
    for h in hosts:
       response = os.system("ping -c 1 "+h.ip)
       if response == 0:
           pass
        
       else:
           h.didIrespond=True
        
    


    return render_template("pingstuff.html",hosts= hosts)

def getHosts():
    send =[]
    goog=  obToPing("Google","8.8.8.8")
    send.append(goog)
    trash = obToPing(name ="trash",ip="1.2.3.254")
    send.append(trash)
    return send 

@app.route("/EmoyeeIDFix/<int:id>")
def empID(id):
    employeeSend = Employee.query.get_or_404(id)

  
    if employeeSend.hashID =='':
    
        try:
            print("no hash")
            employeeSend.hashID = getQR()
            qr_img = qrcode.make(employeeSend.hashID)
            
            #employeeSend.photoBlob.make_blob(qr_img)
            qr_img.save("qr/"+employeeSend.hashID+".jpg")
            binary = convertToBinaryData("qr/"+employeeSend.hashID+".jpg")
            employeeSend.qrBlob = binary
        
            db.session.commit()
            os.remove("qr/"+employeeSend.hashID+".jpg")
        except Exception as e:
            print(e)
            pass
        

    return render_template('empidfix.html',emp = employeeSend) 

@app.route("/EmoyeeIDView/<int:id>")
def empIDFix(id):
    employeeSend = Employee.query.get_or_404(id)

  
 

    return render_template('empid.html',emp = employeeSend) 

@app.route("/SavePhoto/<int:id>", methods=['POST'])
def savePhotoID(id):
    employeeSend = Employee.query.get_or_404(id)
    #os.save(request.form['scShot'])
    #employeeSend.photoBlob = convertToBinaryData(request.form['file'])
    picture =request.files['file']
    #convert =  base64.standard_b64decode(picture)
    filname = getQR()[0:10]+".png"

    picture.save("qr/"+filname)
    binary = convertToBinaryData("qr/"+filname)
    employeeSend.photoBlob =binary
    db.session.commit()
    os.remove("qr/"+filname)
    return redirect('/EmoyeeIDView/'+str(id))

# def get_img(self, request):
#         data = request.files['file'].read()
#         npimg = npgettext.frombuffer(data, np.uint8)
#         img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#         return img

@app.route("/qrView/<int:id>")
def getQrImage(id):
    employeeSend = Employee.query.get_or_404(id)

    return send_file(BytesIO(employeeSend.qrBlob),mimetype="image/jpg")

#GetCheckInPic

@app.route("/GetCheckInPic/<int:id>")
def logIshView(id):
    checkin = ClickInOut.query.get_or_404(id)

    return send_file(BytesIO(checkin.photoBlob),mimetype="image/jpg")

@app.route("/phoView/<int:id>")
def getPhotoImage(id):
    employeeSend = Employee.query.get_or_404(id)


    return send_file(BytesIO(employeeSend.photoBlob),mimetype="image/jpg")

def getQR():
    qrLetters=''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    charactersLength = len(characters)
    for l in range (22):
        l = random.randrange(charactersLength)
        qrLetters= qrLetters+characters[l]

    return qrLetters

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

@app.route("/LogView")
def getLog():
    sendLog = LogView.query.order_by(desc(LogView.id)).all()
    return render_template("log.html",sendLog=sendLog)

@app.route('/Users', methods=['POST','GET'])
def users():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        user_Fetch = User.query.filter_by(disabled = 0 )
        print(user_Fetch)
        return render_template('users.html',users = user_Fetch ,showDisabled =False) 
    else:
        return redirect("/")

@app.route('/UsersDisabled', methods=['POST','GET'])
def usersAll():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        user_Fetch = User.query.filter_by(disabled = 1)
        return render_template('users.html',users = user_Fetch ,showDisabled =True)
    else:
        return redirect("/")

@app.route("/ManualCheckin", methods=['POST','GET'])
def loginManual():
    emp_Fetch = Employee.query.filter_by(disabled=0)
    if request.method =='POST':
        subPin = request.form['pin']
        subID = request.form['id']
        
        employeeSend = Employee.query.get_or_404(subID)
        
        if str(employeeSend.pin) == subPin and employeeSend.disabled==0:
            message = "Clock Out"
            if employeeSend.dataReserve4 =="Clock Out" or employeeSend.dataReserve4 =="":
                message = "Clock In"

            return render_template("clockinout.html",employee = employeeSend, message = message)
        else:
            return render_template("index.html",emps=emp_Fetch, error="Incorrect Credentials")

@app.route("/QrCheckin", methods=['POST','GET'])
def qrCheckin():
    if request.method =='POST':
        message= ""
        hashCHeck =request.form['qrCheckin']
        employeeSend = Employee.query.filter_by(hashID=hashCHeck).first()
        if employeeSend.disabled==0:
            message = "Clock Out"
            if employeeSend.dataReserve4 =="Clock Out" or employeeSend.dataReserve4 =="":
                message = "Clock In"


        if employeeSend.id>0:
            return render_template("clockinout.html",employee = employeeSend, message = message)
        else:
            redirect("/")
    else:
        pass
         


@app.route("/ClockInOut/<int:id>/<message>", methods=['POST','GET'])
def clockInOut(id,message):
    print("ID:"+str(id))
    print("Message:"+message)
    try:
        time = datetime.now()
    
        
        
       
        employeeSend = Employee.query.get_or_404(id)
        employeeSend.dataReserve4= message
        
        employeeSend.LastClock=  time.strftime("%Y-%m-%d %H:%M:%S.%f")
    
        db.session.commit()
        print("Message: empsaved")
        picture =request.files['file']
        filname = getQR()[0:10]+".png"
        picture.save("qr/"+filname)
        binary = convertToBinaryData("qr/"+filname)
        check = ClickInOut(employeeID=id,inOut=message,timeStamp=employeeSend.LastClock,photoBlob=binary)

        db.session.add(check)
        db.session.commit()
        os.remove("qr/"+filname)
        print("Message: checkin saved")
        emp_Fetch = Employee.query.filter_by(disabled=0)
        return render_template("index.html",emps=emp_Fetch, error="")
    
    except:
        emp_Fetch = Employee.query.filter_by(disabled=0)
        return render_template("index.html",emps=emp_Fetch, error="Error from posting time")



@app.route('/UserUpdate/<int:id>', methods=['POST','GET'])
def updateUser(id):
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        userFetch = User.query.get_or_404(id)
        global salt
        if request.method =='POST':
            userFetch.fName = request.form['fName']
            userFetch.lName = request.form['lName']
            userFetch.userName=request.form['userName']
            pasCheck = request.form['password']
      
   
            #hmac.compare_digest(pasCheck,userFetch.password)
            if pasCheck==str(userFetch.password):
            # print("old password")
                pass
            else:
            #print("new password")
                password_hash =  hashlib.pbkdf2_hmac(
                'sha256', # The hash digest algorithm for HMAC
                pasCheck.encode('utf-8'), # Convert the password to bytes
                salt, # Provide the salt
                100000 # It is recommended to use at least 100,000 iterations of SHA-256 
                )
                userFetch.password = password_hash

            userFetch.email = request.form['email']
            try:
                db.session.commit()
                log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +" udpated user: "+ str(userFetch.id) +" "+userFetch.fName)
                db.session.add(log)
                db.session.commit()
                return redirect("/Users")
            except:
                return render_template("userUpdate.html",userFetch=userFetch)
        else:
            render_template("userUpdate.html",userFetch=userFetch)

        return render_template("userUpdate.html",userFetch=userFetch)
    else:
        return redirect("/")

@app.route('/X42/<int:id>/<int:admin>/<int:val>')
def x42(id,admin,val):
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        userFetch= User.query.get_or_404(id)
        if admin ==0:
            print(userFetch.fName +" made admin")
            userFetch.admin = val

        else:
            userFetch.manager = val

        db.session.commit()
        log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +" Rights change for user : "+ str(userFetch.id) +" "+userFetch.fName)
        db.session.add(log)
        db.session.commit()
        return render_template("userUpdate.html",userFetch=userFetch)
    else:
        return redirect("/")

@app.route('/UserDisable/<int:id>')
def disableUser(id):
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        userFetch = User.query.get_or_404(id)
        if userFetch.disabled == 0:
            userFetch.disabled =1
        else:
         userFetch.disabled =0
    
        try:
            db.session.commit()
            log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +"Disabled User: "+ str(userFetch.id) +" "+userFetch.fName)
            db.session.add(log)
            db.session.commit()

            return redirect("/Users")
        except:
            return render_template("userUpdate.html",userFetch=userFetch)
    else:
        return redirect("/")
    


@app.route('/UserNew', methods=['POST','GET'])
def userNew():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        if request.method =='POST':
            global salt
            password1 = request.form['password']
            password1 = password1.encode()    
            password_hash = hashlib.pbkdf2_hmac("sha256", password1,salt, 100000)
            userNew = User(fName = request.form['fName'], lName = request.form['lName'],userName=request.form['userName']
            ,password =password_hash,email =request.form['email'])
            print(password_hash)
            #print(hmac.compare_digest(password_hash, badPasswordHash))
            try:
                db.session.add(userNew)
                db.session.commit()
                log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +"New Employee: " +userNew.fName+" "+userNew.fName)
                db.session.add(log)
                db.session.commit()
                return redirect("/Users")
            except:
                pass
                return render_template('usernew.html')
       

        else:
            return render_template('usernew.html')
    return redirect("/")  

    

@app.route('/UserLogin', methods=['POST','GET'])
def updateLogin():
    return ""

@app.route('/Employees', methods=['POST','GET'])
def employees():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
   
        emp_Fetch = Employee.query.filter_by(disabled=0)
     
        return render_template('employees.html',emps= emp_Fetch,showDisabled =False)
    return redirect("/")

@app.route('/EmployeesAll', methods=['POST','GET'])
def employeesAll():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        if request.method =='POST':
            pass

        else:
            emp_Fetch = Employee.query.filter_by(disabled=1)
            return render_template('employees.html',emps= emp_Fetch,showDisabled =True)     
    else:
        return redirect("/")

@app.route('/EmployeeNew',methods=['POST','GET'])
def newEmployee():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        if request.method =='POST':
       
            print(request.form['fName'])
            employee_Fname = request.form['fName']
            employee_Lname = request.form['lName']
            employee_dob = request.form['DateOfB']
            employee_pin = request.form['pin']
            employee_email= request.form['email']
            employee_phone= request.form['phone']
            employee_new= Employee(fName = employee_Fname,lName =  employee_Lname
            ,DateOfB =  employee_dob,pin = employee_pin,email =employee_email,phone = employee_phone)
        
            try:
                db.session.add(employee_new)
                db.session.commit()
                log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +" created Employee: " +" "+employee_Fname +" "+employee_Lname)
                db.session.add(log)
                db.session.commit()
                return redirect('Employees')
            except:
                return render_template('employees.html')
        else:
            return render_template('employeenew.html')
    else:
        redirect("/")

@app.route('/EmployeeDisable/<int:id>')
def disableEmp(id):
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        emloyeeSend = Employee.query.get_or_404(id)
        if emloyeeSend.disabled ==0:
            time = datetime.now()
            emloyeeSend.TermDate=  time
            emloyeeSend.disabled =1
        else:
            emloyeeSend.disabled =0
    
        try:
            db.session.commit()
            log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +" Disabled/Enabled Employee: "+ str(emloyeeSend.id) +" "+emloyeeSend.fName)
            db.session.add(log)
            db.session.commit()
        
        except:
            pass
        return redirect('/Employees')
    return redirect("/")



@app.route("/Main")
def mainPage():
    name = request.cookies.get('id')
    print("name="+name)
    
    if str(name)!="None":
        userSend = User.query.filter_by(id=int(name)).first()
        print(userSend.fName)
        if userSend.disabled ==1:
            return  redirect('/')

        return render_template("main.html",userSend=userSend)
    else:
        return redirect('/')

@app.route("/Logout")
def logout():
    
    ren = make_response(render_template('login.html'))
    ren.set_cookie('id','')
    return ren

@app.route('/LoginUser',methods=['POST','GET'])
def loginPage():
   
    if request.method =='POST':
        global salt
        user =request.form['user']
        password = request.form['password']
        try:
            userFetch = User.query.filter_by(userName=user).first()
            password = password.encode()    
            password_hash = hashlib.pbkdf2_hmac("sha256", password,salt, 100000)
            try:
                 if str(userFetch.password) == str(password_hash):
                    print("Loginworked")

                    # session['user'] = userFetch
                    ren = make_response(render_template('main.html',userSend=userFetch))
                    ren.set_cookie('id',str(userFetch.id))
                    # ren.set_cookie('fName', userFetch.fName)
                    # ren.set_cookie('a',str(userFetch.admin))
                    # ren.set_cookie('m',str(userFetch.manager))

                    return ren
                    
                 else:
                    return render_template("login.html",message="Password Incorrect")
            except Exception as e:
                return render_template("login.html",message=e)
           
        except:
            return render_template("login.html",message="Password Incorrect")
       
       
    else:
        return render_template("login.html",message ="")

@app.route('/ChangeTimeStamp/<int:id>',methods=['POST','GET'])
def updateTimeStamp(id):
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        timeStamp = ClickInOut.query.get_or_404(id)
        if request.method=='POST':
            theDate = request.form['date1']
            
            theTime =request.form['time1']
            totalTime = theDate+" "+theTime+":00.000000"
            print("GoZera:"+totalTime)
            #subDate = datetime.strptime(totalTime,"%Y-%m-%d %H:%M:%S.%f")
            timeStamp.timeStamp = totalTime
            db.session.commit()

            log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +" change timestamp: "+ str(timeStamp.id) +" "+timeStamp.timeStamp)
            db.session.add(log)
            db.session.commit()
            return redirect("/EmployeeUpdate/"+str(timeStamp.employeeID))
            
            
        else:
            return render_template("timestamp.html", timeStamp = timeStamp.timeStamp ,dataStuff= timeStamp)
    else:
        return redirect("/")




@app.route('/TimeSheet',methods=['POST','GET'])
def timeSheetPage():
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        if request.method =='POST':
            submitDay = request.form['tp']
            now = datetime.strptime(submitDay,"%Y-%m-%d")
        #print(submitDay)
            monday = now - timedelta(days = now.weekday())
            sunday = monday + timedelta(days=6)
            he = calMake(monday,sunday)
            return render_template("timesheet.html",hd = he[0],tb=he[1])
        else:
            now = datetime.now()
            monday = now - timedelta(days = now.weekday())
            sunday = monday + timedelta(days=6)
            he = calMake(monday,sunday)
    
            return render_template("timesheet.html",hd = he[0],tb=he[1])
    return redirect("/")

def calMake(start, end):
    stStr =" 00:00:00.000001"
    enStr =" 23:59:59.000001"
    empList =[]
    empNames=[]
    global format
    thead = ["Employee"]
    daysList = dateRange(start, end)
    startSt = str(start)[0:10]+stStr
    startDate = datetime.strptime(startSt,"%Y-%m-%d %H:%M:%S.%f")
    print(startDate)
    endStr = str(end)[0:10]+enStr
    endDate = datetime.strptime(endStr,"%Y-%m-%d %H:%M:%S.%f")
    print(endDate)
    masterTable=[]
    #print(startSt)
    timeStampList = ClickInOut.query.filter(startDate<ClickInOut.createdDate).filter(endDate>ClickInOut.createdDate)
    for stamp in timeStampList:
        #print(stamp.createdDate)
        if(stamp.employeeID in empList):
            pass
        else:
            empList.append(stamp.employeeID)
    masterLines =[]
    addHead =False
    for emp in empList:
        employeeLine=[]
        e = Employee.query.get_or_404(emp)
        #print(e.fName)
        sendE ="("+str(e.id)+") "+ e.fName +" "+ e.lName
        employeeLine.append(sendE)
        
        for day in daysList:
            s = day
             #print(s)
            hd =datetime.strftime(s,format)
            if addHead ==False:
                thead.append(hd)
            
            timeWorking=0
            
            checkIn=null
            checkout=null
                 
            for line in timeStampList:
                 
                #print(str(line.createdDate)[0:10] +"vs"+ str(s)[0:10])
                #print(str(line.createdDate)[0:10]== str(s)[0:10])
                if str(line.timeStamp)[0:10]== str(s)[0:10] and line.employeeID == e.id:
                    #print(line.createdDate)
                    if line.inOut=="Clock In":
                        
                        checkIn = line.timeStamp
                        #print("Clock In "+str(checkIn))
                    else:
                        
                        checkout =line.timeStamp
                        #print("Clock Out " + str(checkout))
                       
                    if  checkIn !=null and checkout !=null:   
                        conST = datetime.strptime(str(checkIn),"%Y-%m-%d %H:%M:%S.%f")
                        conEn= datetime.strptime(str(checkout),"%Y-%m-%d %H:%M:%S.%f")
                         
                          
                        timeOfWork = conEn -conST 
                        hours = timeOfWork.total_seconds() / 3600
                        if hours >0:
                            timeWorking = timeWorking+hours
                            #print(str(hours))
            employeeLine.append(str(timeWorking)[0:5])
            timeWorking=0
        addHead=True
        masterLines.append(employeeLine)
      
      
        #end of day loop                
    masterTable=masterLines
    #end of emp    
    return [thead,masterTable]

def dateRange(start, end):
    send =[]

    delta = end - start       # as timedelta

    for i in range(delta.days + 1):
        day = start + timedelta(days=i)
        #print(day)
        send.append(day)
    return send 

@app.route('/EmployeeUpdate/<int:id>',methods=['POST','GET'])
def updateEmployee(id):
    name = request.cookies.get('id')
    userLog = User.query.filter_by(id=int(name)).first()
    if userLog.disabled == 0:
        employeeSend = Employee.query.get_or_404(id)
        today = datetime.today()
        thirty_days_ago = today - timedelta(days=30)
        print(thirty_days_ago)
    
        timeStampList = ClickInOut.query.filter_by(employeeID=id).filter(thirty_days_ago<ClickInOut.createdDate)
        if request.method =='POST':
            employee_Fname = request.form['fName']
            employee_Lname = request.form['lName']
            employee_dob = request.form['DateOfB']
            employee_pin = request.form['pin']
            employeeSend.fName = employee_Fname
            employeeSend.lName = employee_Lname
            employeeSend.DateOfB = employee_dob
            if employeeSend =='':
                pass
            else:
                employeeSend.pin = employee_pin
            
            employeeSend.email = request.form['email']
            employeeSend.phone =request.form['phone']
   
            try:
           
                db.session.commit()
                log = LogView(log="User: "+str(userLog.id)+" " +userLog.fName +" udpated Employee: "+ str(employeeSend.id) +" "+employeeSend.fName)
                db.session.add(log)
                db.session.commit()
                return render_template('employeeupdate.html',emloyeeSend = employeeSend,times =timeStampList)
            except Exception as e:
                print(e)
                pass

        
        else: 
            return render_template('employeeupdate.html',emloyeeSend = employeeSend,times=timeStampList)
    else:
        return redirect("/")

if __name__=="__main__":
    app.run(debug=True)


