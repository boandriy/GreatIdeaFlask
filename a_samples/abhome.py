# -*- coding: utf-8 -*-

from flask import Flask, render_template, json, request, redirect, session, url_for, Response
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import abhomeclass
import datetime


mysql = MySQL()

app = Flask(__name__)
app.secret_key = 'ab9'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'templog'
app.config['MYSQL_DATABASE_PASSWORD'] = 'templog'
app.config['MYSQL_DATABASE_DB'] = 'abhome'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#
#  Utility functions
#

def getPageParam(name):
    timeParam = request.args.get(name)

    if not timeParam or not str(timeParam).isdigit():
        timeParamN = 6
    else:
        timeParamN = int(timeParam)

    if timeParamN > 168:

        timeParamN = 168

    return timeParamN

from functools import wraps
from flask import g

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            #print "At decorator"
            return redirect(url_for('showSignin'))  #, next=request.url
        return f(*args, **kwargs)
    return decorated_function
#
#  app routes
#

@app.route('/')
def main():
    currentuser = session.get('username')
    if currentuser:
        return redirect(url_for('userHome'))
    else:
        return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/showSignin')
def showSignin():
    currentuser = session.get('username')
    if currentuser:
        return redirect(url_for('userHome'))
    else:
        return render_template('signin.html')   #, next=request.url


@app.route('/userHome')
@login_required
def userHome():
    timeParam = getPageParam('time')
    currentuser = session.get('username')
    rep = abhomeclass.abDB()
    stats = abhomeclass.MakeStatsHTMLBlock(rep, timeParam)
    bstats = abhomeclass.getTechStats()
    hometemps = rep.getGoogleTableDataHomeTemps(timeParam)
    boilertemps = rep.getGoogleTableDataBoilerTemps(timeParam)

    return render_template('userHome.html', user=currentuser,
                           chart1=hometemps, chart2=boilertemps,
                           stats=stats, bstats=bstats)


@app.route('/boilerStats')
@login_required
def boilerStats():
    # print(session)

    timeParam = getPageParam('time')
    currentuser = session.get('username')
    rep = abhomeclass.abDB()
    stats = abhomeclass.MakeStatsHTMLBlock(rep, timeParam)
    bstats = abhomeclass.getTechStats()
    hometemps = rep.getGoogleTableDataHomeTemps(timeParam)
    boilertemps = rep.getGoogleTableDataBoilerTemps(timeParam)

    return render_template('boilerStats.html', user=currentuser,
                           var=timeParam,
                           chart1=hometemps, chart2=boilertemps, stats=stats, bstats=bstats)



@app.route('/boilerSettings')
@login_required
def boilerSettings():
    # return render_template('error.html', error='page not impemented.', message='work in progress')
    timeParam = getPageParam('time')
    currentuser = session.get('username')
    rep = abhomeclass.abDB()
    stats = abhomeclass.MakeStatsHTMLBlock(rep, timeParam)
    bstats = abhomeclass.getTechStats()
    hometemps = rep.getGoogleTableDataHomeTemps(timeParam)
    boilertemps = rep.getGoogleTableDataBoilerTemps(timeParam)

    return render_template('boilerSettings.html', user=currentuser,
                           var=timeParam,
                           chart1=hometemps, chart2=boilertemps, stats=stats, bstats=bstats)


@app.route('/changeBoilerSettings', methods=['POST'])
@login_required
def changeBoilerSettings():
    paramsAccepted = {"curve": ["Hc1HeatCurve", 0.8, 4.0],
                      "supply": ["Hc1MinimalFlowTempDesired", 40, 70],
                      "power": ["PartloadHcKW", 9, 28],
                      "roomt": ["Hc1DayTemp", 16, 22]}

    form = request.form
    paramName = form.keys()[0]
    value = form[paramName]
    if paramName not in paramsAccepted:
        message = 'Wrong value' + value
        return json.dumps({'status': 'error', 'message': message});
    else:
        if not value.replace(".", '', 1).isdigit():
            message = 'Wrong value' + value
            return json.dumps({'status': 'error', 'message': message});
        paramValue = float(value)

        if paramValue < paramsAccepted[paramName][1] or \
                        paramValue > paramsAccepted[paramName][2]:
            message = "param is not in range: {}[{}]".format(paramName, paramValue)
            return json.dumps({'status': 'error', 'message': message});
        else:
            command = paramsAccepted[paramName][0]
            if paramName == "power":
                device = "BAI"
            else:
                device = "470"
            if paramName =="roomt":
                install = ""
            else:
                install = "#install"
    command = "w -c {}{} {} {}".format(device, install, command, value)

    ebus = abhomeclass.ABebusdTC(host="192.168.1.100", port=8888)
    if not ebus.connected():
        return json.dumps({'status': 'error', 'message': "Can't connect to EBUS"})
    if session.get('permissions')==1:
        response = ebus.execute(command)
    else:
        response = "ERR: Not authorized to actually change boiler params"
    if "ERR: " in response:
        return json.dumps({'status': 'error', 'message': response})
    message = 'Command accepted\n' + "command: " + command +"\n"+"response: "+response
    return json.dumps({'status': 'ok', 'message': message})

@app.route('/jsonstatus')
@login_required
def jsonstatus():
    import json
    bstats = abhomeclass.getTechStats()
    return json.dumps(bstats.getDict())

@app.route('/updategraph')
@login_required
def updategraph():
    import json
    rep = abhomeclass.abDB()
    bstats = abhomeclass.getTechStats()
    hometemps = rep.getGoogleTableDataHomeTemps(6)
    boilertemps = rep.getGoogleTableDataBoilerTemps(6)
    print json.dumps({'hometemps':hometemps, 'boilertemps':boilertemps})
    return json.dumps({'hometemps':hometemps, 'boilertemps':boilertemps})

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('permissions',None)
    session.pop('username', None)
    session.clear()  ## abababa
    return redirect('/')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()
        #print(data)

        if len(data) > 0:
            #            if data[0][3] == _password:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][2]
                session['username'] = data[0][1]
                session['permissions'] = data[0][4]
                #print "At validateLogin: "
                #print "request: ", request.url
                #print "url: ", getPageParam('url')
                return redirect('/userHome?time=6')
            else:
                return render_template('error.html', error='Wrong Email address or Password.',
                                       message='authentication failed')
        else:
            return render_template('error.html', error='Wrong Email address or Password.',
                                   message='authentication failed')


    except Exception as e:
        return render_template('error.html', error=str(e), message='failure during authentication request')
    finally:
        cursor.close()
        con.close()

@app.route('/signUp', methods=['POST', 'GET'])x2
@login_required
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            # All Good, let's call MySQL
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(str(_password))
            cursor.callproc('sp_createWebUser', (_name, _email, str(_hashed_password)))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

import sys
sys.path.append("/opt/abhome")
from abhomeGasmeter import GasMeter

@app.route('/gasMeter')
@login_required
def gasMeter():
    pager = getPageParam('page')
    if pager=="":
        pager="3"
    currentuser = session.get('username')
    rep = abhomeclass.abDB()
    readings = rep.getLastGasMeter(int(pager))

    return render_template('gasMeter.html', user=currentuser,
                           var=pager, readings=readings)


@app.route('/submitReading',methods=['POST'])
@login_required
def submitReading():
    perm = session.get('permissions')
    if perm !=1:
        return render_template('error.html', error='Not allowed to submit reading', message='page restricted to admin users')
    form = request.form
    param = form["reading"]

    value = float(param)
    rep = abhomeclass.abDB()
    readings = rep.getLastGasMeter(1)
    last = readings[0].get_reading()
    date = datetime.datetime.now()  #.strftime("%Y-%m-%d %H:%M")
    if (value > last):
        currentuser=session.get('user')
        record = abhomeclass.GasMeter(gm_reading=value, gm_submitter =currentuser, gm_date=date)
        status = rep.appendGasMeterRecord(record)
        message = "reading accepted: {}\n DB status:{}".format(param,status)
        return json.dumps({'status': 'ok', 'message': message})
    else:
        message = "reading rejected: submitted:{} (last:{})".format(param,last)
        return json.dumps({'status': 'error', 'message': message})

####
####  aba routes and tests
####

@app.route('/users')
@login_required
def users():
    if session.get('permissions')!=1:
        return render_template('error.html', error='Not authorized', message='page restricted to admin users')

    currentuser = session.get('username')

    rep = abhomeclass.abDB()
    users = rep.getAllWebUsers()
    message = "Number of users: {}".format(len(users))
    return render_template('users.html',users=users, user=currentuser, message = message)

@app.route('/deleteUser')
@login_required
def deleteUser():

    if session.get('permissions')==1:
        param_id = getPageParam('id')
        rep = abhomeclass.abDB()
        ### check if user in database
        #print ("at delete user: ",param_id)
        response = rep.deleteUserById(param_id)
        #print (response)
        return json.dumps({'status':'ok', 'message': 'User deleted'})
    else:
        return render_template('error.html', error='Not authorized', message='page restricted to admin users')

############### Test ##################

@app.route('/test')
def test():
    return render_template('test.html')

#######################################

if __name__ == "__main__":
    app.run(debug=True, port=5002, host='0.0.0.0')
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='favicon.ico'))



$(function(){
        $('#btnSignUp').click(function(){

                $.ajax({
                        url: '/signUp_check',
                        data: $('form').serialize(),
                        type: 'POST',
                        success: function(response){
                                console.log(response);
                                alert(response);
                        },
                        error: function(error){
                                console.log(error);
                                alert(error);
                        }
                });
        });
});
