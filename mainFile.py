from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from mainDb import Input, Student, User, swim_Details, swim_Requests, image, Driving
from config import admin_name, psdWord
from twilio.rest import Client

# imports for login session
from flask import session as user_session
import random
import string

from flask import make_response

engine = create_engine('sqlite:///onlineRegd.db')
Input.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


app = Flask(__name__)

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        if request.form['usrName'] != "" and request.form['password'] != "":
            user_session['username'] = request.form['usrName']
            user_session['password'] = request.form['password']
            session = DBSession()
            usr = session.query(User).all()
            if request.form['usrName'] == admin_name and request.form['password'] == psdWord:
                return redirect('/admin')
            else:
                for u in usr:
                    if request.form['password'] == u.password and request.form['usrName'] == u.user_name:
                        return redirect('/main')
                return redirect('/login')
        else:
            return redirect('/login')

    else:
        return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        usr = User(user_name = request.form['regdId'], password = request.form['password'])
        session.add(usr)
        session.commit()
        stud = Student(regdNo = request.form['regdId'],firstName = request.form['fname'],lastName=request.form['lname'],email=request.form['email'],phone=request.form['phone'],year=request.form['year'],branch=request.form['branch'],address=request.form['address'])
        session.add(stud)
        session.commit()
        session.close()
        return redirect('/login')
    else:
        return render_template("register.html")


@app.route('/logout')
def logout():
    session.close()
    print(user_session['username'])
    user_session.clear()
    return redirect('/login')


@app.route('/main')
def main():
    return render_template("main.html", user=user_session)


@app.route('/swimming', methods=['POST', 'GET'])
def swimming():
    plan = session.query(swim_Details).all()
    try:
        kk = session.query(image).filter_by(id=1).one()
        session.close()
        return render_template("swimming.html", user = user_session, plan = plan, m=kk)
    except NoResultFound:
        session.close()
        return render_template("swimming.html", user = user_session, plan = plan, m="no events found")

@app.route('/swimming/student', methods=['POST', 'GET'])
def student():
    if request.method == "POST":
        if request.form['month_plan'] != "":
            obj = request.form['month_plan']
            prd = obj.split(":")[0]
            prc = obj.split(":")[1]
            plan = swim_Requests(userName=user_session['username'], period=prd, price=prc)
            session.add(plan)
            session.commit()
            session.close()
            return redirect('/swimming/student')
        else:
            session.close()
            return redirect('/swimming/student')
    else:
        user = user_session
        stud = session.query(Student).filter_by(regdNo = user['username']).one()
        pay = session.query(swim_Details).all()
        session.close()
        return render_template("student.html", user=user_session, stud = stud, pay = pay)


@app.route('/swimming/others')
def others():
    pay = session.query(swim_Details).all()
    session.close()
    return render_template("others.html", pay = pay)

@app.route('/admin')
def admin():
    session.close()
    return render_template("admin.html", user=user_session)

@app.route('/admin/swim_details', methods=['POST','GET'])
def swim_details():
    if request.method == "POST":
        if request.form['period'] != "" and request.form['price'] != "":
            details = swim_Details(period = request.form['period'], price = request.form['price'])
            session.add(details)
            session.commit()
            session.close()
            return redirect('/admin/swim_details')
        else:
            session.close()
            redirect('/admin/swim_details')
    else:
        session.close()
        return render_template("swim_details.html")


@app.route('/admin/swim_details/upload', methods=['POST', 'GET'])
def upload():
    if request.method == "POST":
        l = request.files['img']
        Imag = image(logo = l.read(), title = request.form['title'])
        session.add(Imag)
        session.commit()
        session.close()
        return redirect('/admin/swim_details/upload')
    else:
        return render_template("swim_details.html")

@app.route('/swimming/event_display')
def event_display():
    try:
        event = session.query(image).filter_by(id=1).one()
        session.close()
        return app.response_class(event.logo, mimetype='application/octet-stream')
    except NoResultFound:
        plan = session.query(swim_Details).all()
        session.close()
        return render_template("swimming.html", user=user_session, plan = plan)


@app.route('/driving', methods=['POST', 'GET'])
def driving():
    user = user_session
    if request.method == "POST":
        reg = Driving(userName = user['username'])
        session.add(reg)
        session.commit()
        session.close()
        return redirect('/driving')
    else:
        try:
            stud = session.query(Driving).all()
            session.close()
            try:
                match = session.query(Driving).filter_by(userName = user['username']).one()
                session.close()
                return render_template("driving.html", user=user, stud=stud, match=match)
            except NoResultFound: 
                session.close()
                return render_template("driving.html", user=user, stud=stud, match="No Match Found")
        except NoResultFound:
            session.close()
            return render_template("driving.html", user=user, stud="No students found")


@app.route('/admin/driving')
def driving_details():
    stud = session.query(Driving).all()
    session.close()
    jn = session.query(Driving, Student).filter(Driving.userName == Student.regdNo).add_columns(Driving.userName, Driving.status, Student.phone, Student.firstName, Student.lastName).all()
    session.close()
    return render_template("drive_details.html", stud = stud, jn=jn)

@app.route('/admin/send_sms', methods=['POST', 'GET'])
def msg_send():
    if request.method == "POST":
        # account_sid = "AC7374e12062b74a36d9070eda02efdd9d"

        # auth_token = "ac9096a2bf2295f2e1183df3b6267d6a"

        # client = Client(account_sid, auth_token)
        # x = request.get_data().decode('utf8').replace("'", '"').split('=')[1]
        # x= '+91' + ' ' + x
        # print(x)
        # message = client.messages.create(
        #     to=x,
        #     from_="+16508806369",
        #     body="come to driving school\n")

        # print(message.sid)
        return "hello"
    else:
        return "hello"

#@app.route('/admin/swim_details/swim_payments')
#def swim_payments():
#   pay = session.query(swim_Details).all()
 #   session.close()
  #  return render_template("swim_payments.html", pay = pay)


@app.route('/sports')
def sports():
    return render_template("cricket.html")


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=7000)
