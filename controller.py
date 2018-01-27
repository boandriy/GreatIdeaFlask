from flask import Flask, render_template, json, request, redirect, session, url_for, Response,json
from functools import wraps
from sqlalchemy import create_engine, desc, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from flask_paginate import Pagination
from werkzeug.security import generate_password_hash, \
     check_password_hash      ###generate_password_hash(pass),check_password_hash(hash,pass)

import sys
import os
import datetime
sys.path.append(os.getcwd())
from dbObjects import User, Idea
from userMail import UserMail

app = Flask(__name__)
app.secret_key = 'GI'

engine = create_engine('mysql://username:pass@127.0.0.1/idea?charset=utf8',encoding='utf-8')         #username and password of database
Session = sessionmaker(bind=engine)
dbSession = Session()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("username") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/login')
def login():
    return render_template ('login.html')

@app.route('/loginaction', methods=['GET', 'POST'])
def loginaction():
    username = request.form['username']
    password =  request.form['password']
    print "username:", username
    print "password:", password

    result = dbSession.query(User).filter(User.username == username).first()
    print result
    print result.password
    if(result == None):
        return "Wrong username"
    if(not check_password_hash(result.password,password)):
        return "Wrong password"
    if(result.status == 0):
        return render_template ('validation.html')

    #login password match
    session['username']= username
    session['userid'] = result.id

    return redirect("/user")#render_template ('user.html',username = result.username)

@app.route('/logout')
def logout():
    if(session['username']):
        session.pop('username',None)
        session.clear()
    return redirect('/')

@app.route('/register')
def register():
    return render_template ('register.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    first= request.form['first']
    last= request.form['last']
    username= request.form['username']
    email= request.form['email']
    psw1 = request.form['psw1']
    psw2 = request.form['psw2']
    pin = generate_password_hash(username)


    print "first name:",first
    print "last name:", last
    print "username:", username
    print "Email:", email
    print "password:", psw1
    print "re-password:", psw2

    found = dbSession.query(User).filter(User.username == username).first()
    print(found)
    if(found):
        return render_template('register.html',message = username + ': username taken')


    if(psw1 != psw2):
        return "Passwords don't match"


    password = generate_password_hash(psw1)
    user = User(first=first,last=last,email=email,status=0, password=password,pin=pin,username=username)
    #print(user)

    #print "Adding user to db"
    add = dbSession.add(user)
    commit = dbSession.commit()
    print (add, commit)
    userMail = UserMail(user)

    userMail.send_signup()
    return render_template ('validation.html')

@app.route('/Submitpin', methods=['GET', 'POST'])
def Submitpin():
    pin = request.form['pin']
    found = dbSession.query(User).filter(User.pin == pin).first()
    if(found):
        found.status += 1
        dbSession.commit()

    return redirect("/")#render_template ('user.html',username = result.username)


@app.route('/signup_check', methods=['GET', 'POST'])
def signup_check():
    username= request.form['username']
    result = dbSession.query(User).filter(User.username == username).first()
    if result:
        return json.dumps({'status': 'error', 'message': "Username taken!"})
    return json.dumps({'status': 'ok', 'message': ""})

@app.route('/user')
@login_required
def user():

    userid = session.get('userid')
    username = str(session.get('username'))+"["+str(userid)+"]"
    page = request.args.get('page', type=int, default=1)
    ideasLst = dbSession.query(Idea).order_by(desc(Idea.datetime))
    result = dbSession.query(Idea).filter(Idea.userid == userid).order_by(desc(Idea.datetime))
    pagination = Pagination(page=page, total=300, search=True, record_name='posts')

    return render_template ('user.html',username =username, ideas=result, pagination=pagination)



####################################################news ################################not implemented
@app.route('/news')
@login_required
def news():

    userid = session.get('userid')
    username = str(session.get('username'))+"["+str(userid)+"]"
    print "HERE"
    ideasLst = dbSession.query(Idea).order_by(desc(Idea.datetime))
    print ideasLst
    result = dbSession.query(Idea).filter(Idea.status == 1).order_by(desc(Idea.datetime))

    return render_template ('news.html',username = username, ideas=result)





@app.route('/newidea')
@login_required
def newIdea():
    username = session.get('username')

    return render_template ('newIdea.html',username = username)

@app.route('/postidea', methods=['GET', 'POST'])
@login_required
def postidea():
    '''
    username = session.get('username')
    if( not username):
        return redirect('/login')
    '''
    body   = request.form['body']
    status = request.form['status']
    userid = session.get('userid')

    currenttime = datetime.datetime.now()
    print "uid:",userid
    print "body:", body
    print "status:", status
    print "currenttime:", currenttime

    print "compiling idea object..."

    idea = Idea(userid=userid, body=body,datetime=currenttime,status=status)
    #print(idea)

    print "Adding idea to db"
    add = dbSession.add(idea)
    print "session"
    commit = dbSession.commit()
    print "commSit"
    return redirect ('/user')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/html')
def html():
    PAGE="""
    <html>
    <head><title>HTML!!!</title></head>
    <body>
     <p>Test <b>Web</b>Page</p>
    </body>
    </html>
    """
    return PAGE


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
