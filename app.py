#!/usr/bin/env python3
import random, os, sys, binascii
import subprocess
import sqlite3
from hashlib import md5
from base64 import b64encode
from datetime import datetime

from flask import *
app = Flask(__name__)
app.config.from_object(__name__) # configure from this file
app.config["SECRET_KEY"] = "\x9d\xe4AS\xa5\xe6\xc7e\xb9\xa3:\xd1x\x17\x81V\x91p\xc1\xb0\x84\xaaBQd\xfbnZ\x96\x0e\xbd\xd7"
#HTTPS
app.config["PREFERRED_URL_SCHEME"] = "https"

# apparently this is for safety of some sort
def rlpt(pt):
    return os.path.join(app.root_path, pt)


# DATABASE
app.config["DATABASE"] = rlpt("app.db")

def connect_db():
    # use detect_types for easy datetime
    rv = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    rv.row_factory = sqlite3.Row
    return rv

# get database
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# tear down database
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



# redis queues
app.config['REDIS_QUEUE_KEY'] = 'submissionsqueue'
from redis import Redis
redis = Redis()

separator = "%%%%%%%%%%%%%%arvidlunnemarkisdabestevercoolestguywowowow%%%%%%%%%%%%%%"
def submissionsdaemon():
    while 1:
        msg = redis.blpop(app.config['REDIS_QUEUE_KEY'])
        datastring = msg[1].decode("utf-8")
        datalist = datastring.split(separator)
        problemid = datalist[0]
        submissionid = datalist[1]
        submissiontext = datalist[2]
        grade(problemid, submissionid, submissiontext)

def delaygradesubmission(problemid, submissionid, submissiontext):
    datastring = problemid + separator + submissionid + separator + submissiontext
    redis.rpush(current_app.config['REDIS_QUEUE_KEY'], datastring)




# Log in

def get_user():
    if not logged_in():
        return {}
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE userid = '" + user_id() + "'")
    user = cur.fetchall()
    if len(user) == 0:
        logout()
        return abort(404)
    return user[0]

def get_username():
    username = ""
    if logged_in():
        username = get_user()["username"]
    return username

def user_id():
    if not logged_in():
        return ""
    return session["userid"]

def logged_in():
    return "userid" in session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if logged_in():
        return redirect(url_for('home', _external=True, _scheme="https"))
    if request.method == 'POST':
        username = request.form['username']
        passwordhash = md5(request.form["password"].encode("utf-8")).hexdigest()
        print("passwordhash: " + passwordhash)
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = '" + username + "' AND passwordhash = '" + passwordhash + "'")
        curlist = cur.fetchall()
        if len(curlist) == 0:
            return render_template("login.html", failedattempt = True)
        user = curlist[0]
        session["userid"] = user["userid"]
        if "urlfrom" in request.args:
            return redirect(httpsify(request.args["urlfrom"]))
        return redirect(url_for('home', _external=True, _scheme="https"))
    signupsuccess = False
    if "s" in request.args:
        signupsuccess = True
    loginfirstmessage = False
    if "g" in request.args:
        loginfirstmessage = True
        signupsuccess = False
    if "urlfrom" in request.args:
        return render_template("login.html", failedattempt = False, signupsuccess = signupsuccess, loginfirstmessage = loginfirstmessage, urlfrom = request.args["urlfrom"])
    else:
        return render_template("login.html", failedattempt = False, signupsuccess = signupsuccess, loginfirstmessage = loginfirstmessage, urlfrom = "nourlfrom")


def httpsify(url):
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    return url

@app.route("/logout", methods=["GET"])
def logout():
    if logged_in():
        session.pop("userid")
    if "from" in request.args:
        return redirect(httpsify(request.args["from"]))
    return redirect(url_for('home', _external=True, _scheme="https"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if logged_in():
        return redirect(url_for('home', _external=True, _scheme="https"))
    if request.method == 'POST':

        # get all necessary details
        username = request.form['username']
        passwordhash = md5(request.form["password"].encode("utf-8")).hexdigest()
        print("passwordhash: " + passwordhash)
        email = request.form['email']
        userid = b64encode(os.urandom(64)).decode("utf-8")

        db = get_db()

        # make sure username is unique
        usernamecur = db.execute("SELECT COUNT(1) from users WHERE username ='" + username + "'") 
        usernamecount = usernamecur.fetchone()[0]
        if usernamecount != 0:
            return render_template("signup.html", failedattempt = True)

        # make sure userid is unique
        useridcur = db.execute("SELECT COUNT(1) from users WHERE userid ='" + userid + "'")
        while useridcur.fetchone()[0] != 0:
            userid = b64encode(os.urandom(64)).decode("utf-8")
            useridcur = db.execute("SELECT COUNT(1) from users WHERE userid ='" + userid + "'")

        db.execute("INSERT into users (username, userid, passwordhash, email) values ('" + username + "', '" + userid + "', '" + passwordhash + "', '" + email + "')")

        db.commit()
        
        if "loginfrom" in request.args:
            return redirect(url_for('login', s = "true", urlfrom=request.args["loginfrom"], _scheme="https", _external=True))
        return redirect(url_for('login', s = "true", _scheme="https", _external=True))

    return render_template("signup.html", failedattempt = False)






@app.route("/")
def home():
    #return redirect(url_for("file?id=" + binascii.b2a_hex(os.urandom(15)).decode("utf-8"), scheme="https"))
    #return redirect(url_for("loadfile", id=binascii.b2a_hex(os.urandom(15)).decode("utf-8"), _external=True, _scheme="https"))
    return render_template("home.html", logged_in=logged_in(), username=get_username())

@app.route("/problem", methods=["GET"])
def loadproblem():
    problemid = request.args["id"]
    statementspath = rlpt("problems/" + problemid + "/statement.html")
    if os.path.exists(statementspath):
        # load problem statement, and submissions history
        problemstatement = "hej"
        with open(statementspath) as statementfile:
            problemstatement = statementfile.read()
        # get all sample test cases
        sampleinfilenames = []
        sampleoutfilenames = set()
        for testfile in os.listdir(rlpt("problems/" + problemid + "/testdata")):
            if testfile.startswith("sample"):
                if testfile.endswith(".in"):
                    sampleinfilenames.append(testfile)
                elif testfile.endswith(".out"):
                    sampleoutfilenames.add(testfile)
        samples = []
        for samplein in sampleinfilenames:
            sampleout = samplein[:-2] + "out"
            if (sampleout in sampleoutfilenames):
                sampledict = {}
                with open(rlpt("problems/" + problemid + "/testdata/" + samplein)) as sampleinfile:
                    sampledict["in"] = sampleinfile.read()
                with open(rlpt("problems/" + problemid + "/testdata/" + sampleout)) as sampleoutfile:
                    sampledict["out"] = sampleoutfile.read()
                samples.append(sampledict)
        # check if logged in
        submissions = []
        if logged_in():
            # get submission id, date, status
            db = get_db()
            cur = db.execute("SELECT * FROM submissions WHERE userid = '" + user_id() + "' AND problemid = '" + problemid + "' ORDER BY submissiondate DESC")
            for submission in cur.fetchall():
                realsubmission = {}
                realsubmission["submissionlink"] = url_for("submission", id=submission["submissionid"], _external=True, _scheme="https")
                realsubmission["submissionstatus"] = submission["submissionstatus"]
                realsubmission["submissiondate"] = submission["submissiondate"]
                submissions.append(realsubmission)
        return render_template("problem.html", problemid=problemid, problemstatement=problemstatement, submissions=submissions, samples=samples, logged_in=logged_in(), username=get_username())
    else:
        return abort(404)




@app.route("/submission", methods=["GET"])
def submission():
    #return render_template("submission.html")
    #return getsubmissionstatus(request.args["id"])
    # make the page static. i need to do imo asap
    db = get_db()
    cur = db.execute("SELECT * FROM submissions WHERE submissionid = '" + submissionid + "'")
    results = cur.fetchall()
    if len(results) == 0:
        return abort(404)




@app.route("/submissionstatus", methods=["POST"])
def submissionstatus():
    submissionid = request.args["submissionid"]
    return getsubmissionstatus(submissionid)

def getsubmissionstatus(submissionid):
    db = get_db()
    cur = db.execute("SELECT submissionstatus FROM submissions WHERE submissionid = '" + submissionid + "'")
    results = cur.fetchall()
    if len(results) == 0:
        return "No Submission"
    return results[0]["submissionstatus"]


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if not logged_in():
        return redirect(url_for('login', g="true",  _external=True, _scheme="https"))


    if request.method == "POST":
        problemid = request.form["problem"]
        submissiontext = request.form["submission"]
        print(problemid)
        print(submissiontext)

        db = get_db()

        # create a random submission id
        submissionid = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        submissionidcur = db.execute("SELECT COUNT(1) from submissions WHERE submissionid ='" + submissionid + "'")
        while submissionidcur.fetchone()[0] != 0:
            submissionid = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
            submissionidcur = db.execute("SELECT COUNT(1) from submissions WHERE submissionid ='" + submissionid + "'")

        # create a database entry for this submission, and add the submission to the submission queue
        db.execute("INSERT into submissions (submissionid, userid, submissiondate, problemid, submissiontext, submissionstatus) values (?, ?, ?, ?, ?, ?)", (submissionid, user_id(), datetime.now(), problemid, submissiontext, 'Running'))
        db.commit()

        # compile and run this submission
        #grade.delay(problemid, submissionid, submissiontext)
        #hej.delay()
        delaygradesubmission(problemid, submissionid, submissiontext)
        return redirect(url_for("submission", id=submissionid, _external=True, _scheme="https"))


    problemid = request.args["problem"]
    problemtitlepath = rlpt("problems/" + problemid + "/title.txt")
    if os.path.exists(problemtitlepath):
        problemtitle = ""
        with open(problemtitlepath) as problemtitlefile:
            problemtitle = problemtitlefile.read()
        return render_template("submit.html", problemid = problemid, problemtitle = problemtitle, logged_in = logged_in(), username = get_username())
    else:
        return abort(404)



def grade(problemid, submissionid, submissiontext):

    # create the filename
    filename = "grading/" + submissionid + ".cpp"
    exfilename = filename + ".x"
    # write to the file
    with open(filename, "w") as cppfile:
        cppfile.write(submissiontext)


    status = ""

    # compile the file to the exfile
    try:
        subprocess.call(["g++", "-std=c++11", "-fsanitize=address,undefined", "-O2", "-o", exfilename, filename])
    except Exception as exception:
        status = "Compile Error"
    if not os.path.exists(exfilename):
        status = "Compile Error"

    
    if status == "":

        timelimit = 1
        timelimitpath = rlpt("problems/" + problemid + "/timelimit.txt")
        try:
            with open(timelimitpath, "r") as timelimitfile:
                timelimit = int(timelimitfile.read())
        except Exception as exception:
            pass

        tests = []
        testinfilenames = []
        testoutfilenames = set()
        for testfile in os.listdir(rlpt("problems/" + problemid + "/testdata")):
            if testfile.endswith(".in"):
                testinfilenames.append(testfile)
            elif testfile.endswith(".out"):
                testoutfilenames.add(testfile)
        for testin in testinfilenames:
            testout = testin[:-2] + "out"
            if (testout in testoutfilenames):
                realoutput = ""
                with open(rlpt("problems/" + problemid + "/testdata/" + testout), "r") as testoutfile:
                    realoutput = testoutfile.read()
                # get the output
                output = ""
                shouldbreak = False
                try:
                    with open(rlpt("problems/" + problemid + "/testdata/" + testin), "rb") as infile:
                        output = subprocess.check_output([os.path.abspath(exfilename)], stdin=infile, timeout=timelimit).decode("utf-8")
                except subprocess.TimeoutExpired as expiredexception:
                    status = "Time Limit Exceeded"
                    shouldbreak = True
                except Exception as exception:
                    status = "Runtime Error"
                    shouldbreak = True
                if shouldbreak: break
                if output != realoutput:
                    status = "Wrong Answer"
                    break

    if status == "":
        status = "Accepted"
    # remove temporary files
    os.remove(filename)
    try:
        os.remove(exfilename)
    except OSError:
        pass

    # write to the sqlite database
    db = connect_db()
    db.execute("UPDATE submissions SET submissionstatus = '" + status + "' WHERE submissionid = '" + submissionid + "'")
    db.commit()

    # return the status
    return status


if __name__ == "__main__":
    app.run()
