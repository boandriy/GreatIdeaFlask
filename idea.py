from flask import Flask, flash, render_template, json, request, redirect, session, url_for, Response,json
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
from dbObjects import User, Idea, Comment
from userMail import UserMail
from feed import generateFeed
from greatIdeaDB import GreatIdeaDB


app = Flask(__name__)
app.secret_key = 'GI'

dbQuery = GreatIdeaDB()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("username") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template ('index.html', title="GreatIdea:Start")

@app.route('/login')
def login():
    return render_template ('login.html')

@app.route('/loginaction', methods=['GET', 'POST'])
def loginaction():
    username = request.form['username']
    password =  request.form['password']

    result = dbQuery.findUserByUsername(username)
    if(result == None):
        return "Wrong username"
    if(not check_password_hash(result.password,password)):
        return "Wrong password"
    if(result.status == 0):
        return render_template ('validation.html')

    #login password match
    session['username']= username
    session['userid'] = result.id

    return redirect("/feed")#render_template ('user.html',username = result.username)

@app.route('/logout')
def logout():
    if(session['username']):
        #session.pop('username',None) not important
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

    found = dbQuery.findUserByUsername(username)
    print(found)
    if(found):
        return render_template('register.html',message = username + ': username taken')
    if(psw1 != psw2):
        return "Passwords don't match"


    password = generate_password_hash(psw1)
    user = User(first=first,last=last,email=email,status=0, password=password,pin=pin,username=username)
    #print(user)

    #print "Adding user to db"
    dbQuery.add(user)
    userMail = UserMail(user)

    userMail.send_signup()
    return render_template ('validation.html')

@app.route('/Submitpin', methods=['GET', 'POST'])    # AB - does it work???? I mean dbSession.commit() at the end?
def Submitpin():
    pin = request.form['pin']
    foundUser = dbQuery.findUserByPin(pin)
    if(foundUser):
        dbQuery.activateUser(foundUser)
    return redirect("/")#render_template ('user.html',username = result.username)


@app.route('/signup_check', methods=['GET', 'POST'])
def signup_check():
    username= request.form['username']
    result = dbQuery.findUserByUsername(username)
    if result:
        return json.dumps({'status': 'error', 'message': "Username taken!"})
    return json.dumps({'status': 'ok', 'message': ""})

@app.route('/user')
@login_required
def user():
    per_page = 5
    userid = session.get('userid')
    username = str(session.get('username'))          #+"["+str(userid)+"]"
    page = request.args.get('page', type=int, default=1)
    result = dbQuery.getAllIdeasByUserId(userid,-1)
    total=result.count()
    if (page-1)>total/per_page:                     # was page > total/per_page  FIXED!
        return redirect ('/user?page=1')
    pagination = Pagination(page=page, total=total, per_page=per_page,search=False, record_name='posts')
    start = (page-1) * per_page
    end = start+per_page


    return render_template ('user.html',username = username,
                            ideas=result[start:end],
                            pagination=pagination)

@app.route('/gettcomments/<ideaid>/<numcomments>', methods=['GET', 'POST'])
@login_required
def gettcomments(ideaid, numcomments):
    username = str(session.get('username'))

    if not ideaid:
        return ""

    idea = dbQuery.getIdeaById(ideaid)

    if not idea:
        return json.dumps({'status': 'error', 'message': "<p>Can't get comments for idea!</p>"})

    print "gettcomments: ", numcomments, type(numcomments)

    result = render_template('_idea_comment.html', idea = idea, numberOfComments=int(numcomments), username = username);

    json_response = json.dumps({'status': 'ok', 'message': "{}".format(result) })
    return json_response


@app.route('/feed')
@login_required
def feed():
    per_page = 5
    username = str(session.get('username'))
    page = request.args.get('page', type=int, default=1)
    feed = generateFeed(dbQuery.dbSession)
    total=feed.count()
    print total
    if (page-1)>total/per_page:                 # was page > total/per_page  FIXED!
        return redirect ('/feed')
    pagination = Pagination(page=page, total=total, per_page=per_page,search=False, record_name='posts')
    start = (page-1) * per_page
    end = start+per_page
    return render_template ('feed.html',ideas = feed[start:end],
                            pagination=pagination,
                            username = username)


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

    idea = Idea(user_id=userid, body=body,datetime=currenttime,status=status)
    dbQuery.add(idea)

    return redirect ('/user')

@app.route('/postcomment/<ideaid>', methods=['GET', 'POST'])
@login_required
def postcomment(ideaid):
    userid = session.get('userid')
    currenttime = datetime.datetime.now()
    body   = request.form['comment']

    comment = Comment(user_id=userid, idea_id=ideaid,datetime=currenttime,body=body)
    print (comment)
    dbQuery.add(comment)

    return redirect ('/user')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
