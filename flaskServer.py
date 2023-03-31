from flask import session, Flask, render_template,request,redirect,url_for,jsonify,Response
import re
from markupsafe import escape
from WCIFManip import *

from checkCumulativeTime import *
from secret_key import secret_key

app = Flask(__name__)

app.config.update(
    SECRET_KEY = secret_key,
    SESSION_COOKIE_SECURE = True,
    PERMANENT_SESSION_LIFETIME = 7200
)


@app.before_request
def give_name():
    if 'name' not in session:
        session['name'] = None
    if 'id' not in session:
        session['id'] = None

@app.route('/')
def startPage():
    return render_template('index.html',user_name=session['name'])

@app.route('/logout',methods=['GET','POST'])
def logout():
    keys = [key for key in session.keys()]
    for key in keys:
        session.pop(key)
    return redirect(url_for('startPage'))

@app.route('/show_token') # If we can get SSL/Https, then this function might be able to display the code. Or better, oauth can happen as intended.
def show_token():
    return render_template('show_token.html',user_name=session['name'])

@app.route('/process_token',methods=['POST'])
def process_token():
    access_token_temp = escape(request.form['access_token'])
    access_token= access_token_temp.split('access_token=')[1].split('&')[0]
    session['token'] = {'Authorization':f"Bearer {access_token}"}
    return "Redirect should be happening to /me. Otherwise do it manually."

@app.route('/playground')
def playground():
    return render_template('playground.html',user_name=session['name'])

@app.route("/localhost")
def localhost_login():
    return redirect("https://www.worldcubeassociation.org/oauth/authorize?client_id=jvK8thQ_pdL4Tf2lmXcjuQrr11X1mjw0p0UtF8M4q4o&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fshow_token&response_type=token&scope=manage_competitions+public")

@app.route('/me', methods = ['POST', 'GET'])
def logged_in():
    if request.method == 'POST':
        token = escape(request.form['token'])
        session['token'] = {'Authorization':f"Bearer {token}"}
    if 'token' in session:
        if not session['name']:
            me = get_me(session['token'])
            if me.status_code == 200:
                user_name = json.loads(me.content)['me']['name']
                user_id = int(json.loads(me.content)['me']['id'])
                session['name'] = user_name
                session['id'] = user_id
            else:
                return f"Some error occured: {me.status_code}, {me.content}"
        comps = get_coming_comps(session['token'],session['id'])
        return render_template('logged_in.html',user_name=session['name'],comps=comps)   
    else:
        return "You are currently not authorized. You will have to manually type in the comp id into the URL."

@app.route('/<compid>')
def calculate(compid):
    fail_string = "The ID you have hardcoded into the URL doesn't match a valid format of a competition url."
    escapedCompid = escape(compid)
    if len(escapedCompid) <= 32:
        pattern = re.compile("^[a-zA-Z\d]+$")
        if pattern.match(escapedCompid):
            session['compid'] = compid
            if 'token' in session:
                wcif,statusCode =  getWcif(session['compid'],session['token'])
                session['canAdminComp'] = True if statusCode == 200 else False
            else:
                session['canAdminComp'] = False
            if not session['canAdminComp']:
                wcif,_ =  getWCIFPublic(session['compid'])
            # printingString = makeHtml(wcif)
            return render_template("comp_settings.html",comp=session['compid'],user_name=session['name'])
        else:
            return fail_string
    else:
        fail_string

@app.route('/show',methods=['GET','POST'])
def showCompetition():
    if request.method == 'POST':
        form_data = request.form
        
        tempEventsCal = escape(form_data["eventsCalculate"]).strip().lower()
        competitorOrdering = escape(form_data["competitorOrdering"]).strip().lower()
        pattern2 = re.compile("^(0|1)$")
        if pattern2.match(competitorOrdering):
            session['competitorOrdering'] = int(competitorOrdering)
        if not tempEventsCal:
            session['eventsCalculate'] = []
        else:
            session['eventsCalculate'] = [event.strip() for event in tempEventsCal.split(',')]
    
    if session['canAdminComp']:
        wcif,statusCode =  getWcif(session['compid'],session['token'])
    else:
        wcif,_ =  getWCIFPublic(session['compid'])
        statusCode = 401
    if not session['eventsCalculate']:
        printEvents = "all events"
    else:
        printEvents = session['eventsCalculate'] 
    overview = applySorting(getSolveTime(wcif,session['eventsCalculate']),session['competitorOrdering'])
    return render_template("show_comp.html",overview=overview,status=statusCode,events=printEvents,comp=session['compid'],user_name=session['name'])

# app.run(host=host,port=port)

if __name__ == '__main__':
    app.run(port=5000,debug=False)


# https://www.worldcubeassociation.org/api/v0/users/6777?upcoming_competitions=true&ongoing_competitions=true
# https://www.worldcubeassociation.org/api/v0/competitions?managed_by_me=true&start=2022-12-31