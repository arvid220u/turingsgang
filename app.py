#!/usr/bin/env python3
import random, os, sys, binascii
import subprocess
import sqlite3
from hashlib import md5
from base64 import b64encode
from datetime import datetime
import time

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
    while True:
        try:
            while 1:
                msg = redis.blpop(app.config['REDIS_QUEUE_KEY'])
                datastring = msg[1].decode("utf-8")
                datalist = datastring.split(separator)
                problemid = datalist[0]
                submissionid = datalist[1]
                submissiontext = datalist[2]
                grade(problemid, submissionid, submissiontext)
        except Exception as exception:
            continue

def delaygradesubmission(problemid, submissionid, submissiontext):
    datastring = problemid + separator + submissionid + separator + submissiontext
    redis.rpush(current_app.config['REDIS_QUEUE_KEY'], datastring)




# Log in

def get_user(userid = None):
    if userid == None:
        userid = user_id()
        if not logged_in():
            return {}
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE userid = '" + userid + "'")
    user = cur.fetchall()
    if len(user) == 0:
        logout()
        return abort(404)
    return user[0]


def get_username(userid = None):
    if userid == None:
        userid = user_id()
        if not logged_in(): return ""
    username = get_user(userid = userid)["username"]
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
    return problemslist()


def problemslist():
    # list all problems
    problemids = os.listdir(rlpt("problems"))
    problems = []
    for problemid in problemids:
        if problemid.startswith("%"):
            continue
        problem = {}
        problem["problemid"] = problemid
        problem["problemtitle"] = getproblemtitle(problemid)
        problem["status"] = "Not Attempted"
        if logged_in():
            # get submission id, date, status
            db = get_db()
            cur = db.execute("SELECT * FROM submissions WHERE userid = '" + user_id() + "' AND problemid = '" + problemid + "' ORDER BY submissiondate")
            for submission in cur.fetchall():
                if problem["status"] != "Accepted":
                    problem["status"] = submission["submissionstatus"]
        problems.append(problem)

    return render_template("problemslist.html", logged_in=logged_in(), username=get_username(), problems = problems)


def addextradatatoproblemstatement(problemstatement, problemid):
    # all extra data is identified by being enclosed in %al% tags
    # thus, all elements on even indices are raw html code,
    # while all odd elements constitute some type of extra data
    problemstatementsplit = problemstatement.split("%al%")

    realproblemstatement = ""

    for index, data in enumerate(problemstatementsplit):
        # if index is even, just continue
        if index % 2 == 0:
            realproblemstatement += data
            continue

        # strip for whitespace in identifier part
        data.lstrip()

        if data.startswith("image"):
            # images are identified by %al%image:filename.png%al%
            filenamestring = data.split(":")[1].strip()
            # add an img tag. add an extra class that is this problems id concatenated with the filename (without extension), for custom styling
            realproblemstatement += "<img class='problemstatementimage " + problemid + filenamestring.split('.')[0].split(' ')[0] + "' src='" + url_for('static', filename='problems/' + problemid + "/" + filenamestring) + "'>"

        elif data.startswith("problemlink"):
            # problemlink has format problemlink:problemid
            problemidstring = data.split(":")[1].strip()
            realproblemstatement += url_for("problem", problemid=problemidstring)

        elif data.startswith("problemtitle"):
            # formt problemlink:problemtitle
            problemidstring = data.split(":")[1].strip()
            realproblemstatement += getproblemtitle(problemidstring)



    return realproblemstatement

        





@app.route("/problems/<problemid>", methods=["GET"])
def problem(problemid):
    statementspath = rlpt("problems/" + problemid + "/statement.html")
    if os.path.exists(statementspath):
        # load problem statement, and submissions history
        problemstatement = "hej"
        with open(statementspath) as statementfile:
            problemstatement = statementfile.read()

        # maybe add images to the problem statement
        problemstatement = addextradatatoproblemstatement(problemstatement, problemid)

        problemcredits = ""
        try:
            with open(rlpt("problems/" + problemid + "/credits.html")) as creditsfile:
                problemcredits = creditsfile.read()
        except Exception as exception:
            pass
        # get all sample test cases
        sampleinfilenames = []
        sampleoutfilenames = set()
        for testfile in os.listdir(rlpt("problems/" + problemid + "/testdata")):
            if testfile.startswith("sample"):
                if testfile.endswith(".in"):
                    sampleinfilenames.append(testfile)
                elif testfile.endswith(".out"):
                    sampleoutfilenames.add(testfile)
        sampleinfilenames.sort()
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
                realsubmission["executiontime"] = getrealexecutiontime(submission["executiontime"], submission["submissionstatus"], problemid)
                submissions.append(realsubmission)
        return render_template("problem.html", problemid=problemid, problemstatement=problemstatement, submissions=submissions, samples=samples, logged_in=logged_in(), username=get_username(), problemcredits = problemcredits, problemtitle=getproblemtitle(problemid))
    else:
        return abort(404)


import html

@app.route("/submission", methods=["GET"])
def submission():
    #return render_template("submission.html")
    #return getsubmissionstatus(request.args["id"])
    # make the page static. i need to do imo asap
    submissionid = request.args["id"]
    db = get_db()
    cur = db.execute("SELECT * FROM submissions WHERE submissionid = '" + submissionid + "'")
    results = cur.fetchall()
    if len(results) == 0:
        return abort(404)

    result = results[0]


    problemid = result["problemid"]
    problemtitle = getproblemtitle(problemid)

    executiontime = getrealexecutiontime(result["executiontime"], result["submissionstatus"], problemid)
    
    return render_template("submission.html", problemid=problemid, problemtitle = problemtitle, submissionusername=get_username(userid = result["userid"]), submissiondate=result["submissiondate"], submissiontext=html.escape(result["submissiontext"]), submissionstatus=result["submissionstatus"], logged_in=logged_in(), username = get_username(), executiontime = executiontime)



def getproblemtitle(problemid):
    problemtitlepath = rlpt("problems/" + problemid + "/title.txt")
    problemtitle = problemid
    with open(problemtitlepath) as problemtitlefile:
        problemtitle = problemtitlefile.read()
    return problemtitle

def getrealexecutiontime(extime, status, problemid):
    inttime = float(extime)
    if status == "Compile Error":
        return "-"
    if status == "Time Limit Exceeded":
        timelimit = gettimelimit(problemid)
        timstring = "{:.2f}".format(timelimit) 
        realstring = ">" + timstring + " s"
        return realstring
    if inttime == -1:
        return "?"
    timstring = "{:.2f}".format(inttime) 
    timstring = timstring + " s"
    return timstring






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
        db.execute("INSERT into submissions (submissionid, userid, submissiondate, problemid, submissiontext, submissionstatus, executiontime) values (?, ?, ?, ?, ?, ?, ?)", (submissionid, user_id(), datetime.now(), problemid, submissiontext, 'Running', -1))
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




@app.route("/submissionshistory", methods=["GET"])
def submissionshistory():
    if not logged_in():
        return abort(404)
    if get_username() != "Teodor Bucht" and get_username() != "arvid220u":
        return abort(404)
    return "you are privileged to view submissions history"



def gettimelimit(problemid):
    timelimit = 1
    timelimitpath = rlpt("problems/" + problemid + "/timelimit.txt")
    try:
        with open(timelimitpath, "r") as timelimitfile:
            timelimit = float(timelimitfile.read())
    except Exception as exception:
        pass
    return timelimit

import resource
def setgradelimits():
    # set memory limit to 1024 MB = 2**30
    resource.setrlimit(resource.RLIMIT_AS, (2**30,2**30))


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
        subprocess.call(["g++", "-std=c++11", "-static", "-O2", "-o", exfilename, filename])
    except Exception as exception:
        status = "Compile Error"
    if not os.path.exists(exfilename):
        status = "Compile Error"

    executiontime = -1
    
    if status == "":

        executiontime = 0

        timelimit = gettimelimit(problemid)

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
                        starttime = time.time()
                        output = subprocess.check_output([os.path.abspath(exfilename)], stdin=infile, timeout=timelimit, preexec_fn = setgradelimits).decode("utf-8")
                        endtime = time.time()
                        realexecutiontime = endtime - starttime
                        executiontime = max(realexecutiontime, executiontime)
                except subprocess.TimeoutExpired as expiredexception:
                    status = "Time Limit Exceeded"
                    shouldbreak = True
                    executiontime = -1
                except Exception as exception:
                    status = "Runtime Error"
                    shouldbreak = True
                if shouldbreak: break
                # rstrip so that users don't have to end with newlines
                if output.rstrip() != realoutput.rstrip():
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
    db.execute("UPDATE submissions SET submissionstatus = '" + status + "', executiontime = '" + str(executiontime) + "' WHERE submissionid = '" + submissionid + "'")
    db.commit()

    # return the status
    return status


if __name__ == "__main__":
    app.run()
