#!/usr/bin/env python3
import random, os, sys, binascii
import subprocess
import sqlite3
from hashlib import md5
from base64 import b64encode
from datetime import datetime
import time
import config as turingconfig

# set timezone
os.environ["TZ"] = "Europe/Stockholm"

from flask import *
app = Flask(__name__)
app.config.from_object(__name__) # configure from this file
app.config["SECRET_KEY"] = turingconfig.FLASK_SECRET_KEY
#HTTPS
app.config["PREFERRED_URL_SCHEME"] = "https"

# apparently this is for safety of some sort
def rlpt(pt):
    return os.path.join(app.root_path, pt)


@app.route("/loaderio-74214b0f5a6a4416bafb4a09fa7769b5.txt")
def authenticate_for_loaderio():
    return "loaderio-74214b0f5a6a4416bafb4a09fa7769b5"

@app.route("/googled4987f8a6a3dfeee.html")
def authenticate_for_google():
    return "google-site-verification: googled4987f8a6a3dfeee.html"


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

def submissionsdaemon():
    while True:
        try:
            while 1:
                msg = redis.blpop(app.config['REDIS_QUEUE_KEY'])
                datastring = msg[1].decode("utf-8")
                datalist = json.loads(datastring)
                problemid = datalist["problemid"]
                submissionid = datalist["submissionid"]
                submissiontext = datalist["submissiontext"]
                grade(problemid, submissionid, submissiontext)
        except Exception as exception:
            continue

def delaygradesubmission(problemid, submissionid, submissiontext):
    #datastring = problemid + separator + submissionid + separator + submissiontext
    datadict = {}
    datadict["problemid"] = problemid
    datadict["submissionid"] = submissionid
    datadict["submissiontext"] = submissiontext
    datastring = json.dumps(datadict)
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
        userid = binascii.b2a_hex(os.urandom(20)).decode("utf-8")

        db = get_db()

        # make sure username is unique
        usernamecur = db.execute("SELECT COUNT(1) from users WHERE username ='" + username + "'") 
        usernamecount = usernamecur.fetchone()[0]
        if usernamecount != 0:
            return render_template("signup.html", failedattempt = True)

        # make sure userid is unique
        useridcur = db.execute("SELECT COUNT(1) from users WHERE userid ='" + userid + "'")
        while useridcur.fetchone()[0] != 0:
            userid = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
            useridcur = db.execute("SELECT COUNT(1) from users WHERE userid ='" + userid + "'")

        db.execute("INSERT into users (username, userid, passwordhash, email, groupstatus) values ('" + username + "', '" + userid + "', '" + passwordhash + "', '" + email + "', 'regular')")

        db.commit()
        
        if "loginfrom" in request.args:
            return redirect(url_for('login', s = "true", urlfrom=request.args["loginfrom"], _scheme="https", _external=True))
        return redirect(url_for('login', s = "true", _scheme="https", _external=True))

    return render_template("signup.html", failedattempt = False)






@app.route("/")
def home():

    return render_template("home.html", logged_in=logged_in(), username=get_username())


@app.route("/problems")
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
        data = data.lstrip()

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

        
def addextradatatoblogpost(problemstatement, problemid):
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
        data = data.lstrip()


        if data.startswith("image"):
            # images are identified by %al%image:filename.png%al%
            filenamestring = data.split(":")[1].strip()
            # add an img tag. add an extra class that is this problems id concatenated with the filename (without extension), for custom styling
            realproblemstatement += "<img class='blogpostimage " + blogid + filenamestring.split('.')[0].split(' ')[0] + "' src='" + url_for('static', filename='blog/' + blogid + "/" + filenamestring) + "'>"

        elif data.startswith("problemlink"):
            # problemlink has format problemlink:problemid
            problemidstring = data.split(":")[1].strip()
            realproblemstatement += url_for("problem", problemid=problemidstring)

        elif data.startswith("problemtitle"):
            # formt problemlink:problemtitle
            problemidstring = data.split(":")[1].strip()
            realproblemstatement += getproblemtitle(problemidstring)

        elif data.startswith("link"):
            # format link:selector
            selectorstring = data.split(":")[1].strip()
            realproblemstatement += url_for(selectorstring, _external=True, _scheme="https")

        elif data.startswith("staticlink"):
            # format link:path
            selectorstring = data.split(":")[1].strip()
            realproblemstatement += url_for("static", filename=selectorstring, _external=True, _scheme="https")



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


def getblogposttitle(blogid):
    blogtitlepath = rlpt("blog/" + blogid + "/title.txt")
    problemtitle = blogid
    with open(blogtitlepath) as blogtitlefile:
        problemtitle = blogtitlefile.read()
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
        submissionid = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
        submissionidcur = db.execute("SELECT COUNT(1) from submissions WHERE submissionid ='" + submissionid + "'")
        while submissionidcur.fetchone()[0] != 0:
            submissionid = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
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




# GRADING

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



# EDITOR

@app.route("/editor")
def editor():

    myfiles = []
    if logged_in():
        db = get_db()
        cur = db.execute("SELECT * FROM files WHERE userid = '" + user_id() + "'")
        results = cur.fetchall()
        results.sort(key = lambda k: k["filename"])
        myfiles = results
    
    return render_template("myfiles.html", myfiles=myfiles, logged_in=logged_in(), username=get_username())

@app.route("/deletefile", methods=["GET"])
def deletefile():
    if not logged_in():
        abort(404)

    fileid = request.args["fileid"]

    db = get_db()
    filecur = db.execute("SELECT * FROM files WHERE fileid ='" + fileid + "' AND userid ='" + user_id() + "'")
    results = filecur.fetchall()
    if len(results) == 0:
        return abort(404)
    myfile = results[0]

    # remove the file from the database, and all its associated files
    db.execute("DELETE FROM files WHERE fileid ='" + fileid + "' AND userid = '" + user_id() + "'")
    db.commit()
    filename = rlpt("data/" + fileid + ".cpp")
    exfilename = filename + ".x"
    compiledfilename = filename + ".compiled.cpp"
    try:
        os.remove(filename)
    except OSError:
        pass
    try:
        os.remove(exfilename)
    except OSError:
        pass
    try:
        os.remove(compiledfilename)
    except OSError:
        pass

    return redirect(url_for('editor', _external=True, _scheme="https"))


@app.route("/newfile")
def newfile():
    if not logged_in():
        return redirect(url_for('login', g="true",  _external=True, _scheme="https"))

    # create a file with filename namnlos.cpp
    # append a number in order for it to be unique
    # also generate a file id
    fileid = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
    db = get_db()

    # make sure fileid is unique
    fileidcur = db.execute("SELECT COUNT(1) from files WHERE fileid ='" + fileid + "'")
    while fileidcur.fetchone()[0] != 0:
        fileid = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
        fileidcur = db.execute("SELECT COUNT(1) from files WHERE fileid ='" + fileid + "'")


    filename = "Namnlös fil"
    # make sure filename is unique
    filenamecur = db.execute("SELECT COUNT(1) from files WHERE filename ='" + filename + "'")
    filecount = 2
    while filenamecur.fetchone()[0] != 0:
        filename = "Namnlös fil "  + str(filecount)
        filenamecur = db.execute("SELECT COUNT(1) from files WHERE filename ='" + filename + "'")
        filecount += 1

    db.execute("INSERT into files (fileid, userid, creationdate, lastupdateddate, filename) values (?, ?, ?, ?, ?)", (fileid, user_id(), datetime.now(), datetime.now(), filename))

    db.commit()

    # create the actual file
    filecontents = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    \n    \n    return 0;\n}"
    realfilename = rlpt("data/" + fileid + ".cpp")
    with open(realfilename, "w") as realfile:
        realfile.write(filecontents)

    return redirect(url_for('file', fileid=fileid, _external=True, _scheme="https"))


@app.route("/file/<fileid>", methods=["GET"])
def file(fileid):
    if not logged_in():
        return redirect(url_for('editor', _external=True, _scheme="https"))

    db = get_db()
    filecur = db.execute("SELECT * FROM files WHERE fileid ='" + fileid + "' AND userid ='" + user_id() + "'")
    results = filecur.fetchall()
    if len(results) == 0:
        return abort(404)
    myfile = results[0]

    filecontents = ""
    realfilename = rlpt("data/" + fileid + ".cpp")
    if not os.path.exists(realfilename):
        filecontents = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    \n    \n    return 0;\n}"
        with open(realfilename, "w") as realfile:
            realfile.write(filecontents)
    else:
        with open(realfilename, "r") as realfile:
            filecontents = realfile.read()

    safefilecontents = json.dumps(filecontents)

    return render_template("file.html", myfile=myfile, filecontents=safefilecontents, logged_in=logged_in(), username=get_username())

@app.route("/changefilename", methods=["POST"])
def changefilename():
    if not logged_in():
        return abort(404)

    indata = request.data.decode("utf-8")
    filedata = json.loads(indata)

    db = get_db()
    db.execute("UPDATE files SET filename = '" + filedata["filename"] + "' WHERE fileid = '" + filedata["fileid"] + "'")
    db.execute("UPDATE files SET lastupdateddate = '" + str(datetime.now()) + "' WHERE fileid = '" + filedata["fileid"] + "'")
    db.commit()


    return "Successfully changed name!"



@app.route("/savefile", methods=["POST"])
def savefile():

    indata = request.data.decode("utf-8")
    filedata = json.loads(indata)

    realfilename = rlpt("data/" + filedata["fileid"] + ".cpp")
    with open(realfilename, "w") as realfile:
        realfile.write(filedata["filecontents"])

    # change date of last updated file
    db = get_db()
    db.execute("UPDATE files SET lastupdateddate = '" + str(datetime.now()) + "' WHERE fileid = '" + filedata["fileid"] + "'")
    db.commit()

    return "Successfully saved!"


@app.route("/compileandrun", methods=["POST"])
def compileandrun():
    if not logged_in():
        return abort(404)

    # get data from post
    indata = request.data.decode("utf-8")
    filedata = json.loads(indata)
    fileid = filedata["fileid"]
    filecontents = filedata["filecontents"]
    inputdata = filedata["inputfile"]


    # create the filename
    filename = rlpt("data/" + fileid + ".cpp")
    exfilename = filename + ".x"
    infilename = filename + ".in"
    compiledfilename = filename + ".compiled.cpp"
    # write to the file
    with open(filename, "w") as cppfile:
        cppfile.write(filecontents)

    # create the infile
    with open(infilename, "w") as infile:
        infile.write(inputdata)


    # if filecontents uses bits/stdc++.h, include allc++.h instead for faster compilation time (precompiled header)
    # we don't do this in judging though, since it is potentially dangerous (for unclear reasons, though)
    # IMPORTANT: make sure the allc++.h file is present in the same folder as the 'compiledfilename' file.
    # the allc++.h file should contain a single row, including bits/stdc++.h.
    # it should be compiled in the same folder, to the filename allc++.h.gch
    if filecontents.startswith("#include <bits/stdc++.h>\n"):
        filecontents = filecontents.split("\n", 1)[1]
        filecontents = '#include "allc++.h"\n' + filecontents

    # check if compiled file is different
    compileddifferent = True
    if os.path.exists(compiledfilename):
        with open(compiledfilename, "r") as compiledfile:
            if compiledfile.read() == filecontents:
                compileddifferent = False
    if compileddifferent:
        with open(compiledfilename, "w") as compiledfile:
            compiledfile.write(filecontents)

    if compileddifferent:
        # change date of last updated file
        db = get_db()
        db.execute("UPDATE files SET lastupdateddate = '" + str(datetime.now()) + "' WHERE fileid = '" + filedata["fileid"] + "'")
        db.commit()

    returndata = {}

    returndata["success"] = True

    # compile the file to the exfile
    if compileddifferent:
        compileoutput = ""
        compileerror = ""
        try:
            popn = subprocess.Popen(["g++", "-std=c++11", "-fsanitize=address,undefined", "-Wall", "-o", exfilename, compiledfilename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            compileoutput, compileerror = popn.communicate()
        except Exception as exception:
            pass
        compileoutput = compileoutput.decode("utf-8")
        compileerror = compileerror.decode("utf-8")

        # check if there is an internal compile error present
        if "internal compiler error" in compileerror:
            print("RECOMPILING")
            # try to compile again, using the original filename
            try:
                popn = subprocess.Popen(["g++", "-std=c++11", "-fsanitize=address,undefined", "-Wall", "-o", exfilename, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                compileoutput, compileerror = popn.communicate()
            except Exception as exception:
                pass
            compileoutput = compileoutput.decode("utf-8")
            compileerror = compileerror.decode("utf-8")


        # remove all references to the filename
        compileerror = compileerror.replace(compiledfilename, "")

        if popn.returncode != 0:
            os.remove(infilename)
            returndata["success"] = False
            returndata["compileerror"] = compileerror
            with open(compiledfilename, "w") as compiledfile:
                compiledfile.write("wweifojqwoifjq")
            return json.dumps(returndata)
        if not os.path.exists(exfilename):
            os.remove(infilename)
            returndata["success"] = False
            returndata["compileerror"] = "A mysterious error occurred. No one knows why. Try again, maybe?"
            with open(compiledfilename, "w") as compiledfile:
                compiledfile.write("wweifojqwoifjq")
            return json.dumps(returndata)
        returndata["compilewarnings"] = compileerror

    # get the output
    output = ""
    try:
        with open(infilename, "rb") as infile:
            starttime = time.time()
            result = subprocess.run([os.path.abspath(exfilename)], stdin=infile, timeout=4, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            endtime = time.time()
            returndata["executiontime"] = "{:.2f}".format(endtime - starttime) + " s"
            if result.stderr.decode("utf-8") != "":
                returndata["runtimeerror"] = result.stderr.decode("utf-8").replace(compiledfilename, "")
            result.check_returncode()
            output = result.stdout.decode("utf-8")
    except subprocess.TimeoutExpired as timeoutexception:
        os.remove(infilename)
        returndata["success"] = False
        returndata["timeout"] = True
        returndata["executiontime"] = ">4.00 s"
        return json.dumps(returndata)
    except Exception as exception:
        os.remove(infilename)
        returndata["success"] = False
        return json.dumps(returndata)

    # remove temporary files
    os.remove(infilename)

    returndata["output"] = output

    # return the output
    return json.dumps(returndata)







# ABOUT

@app.route("/om")
def about():
    return render_template("about.html", logged_in=logged_in(), username=get_username())



def is_admin():
    return (get_username() == "arvid220u" or get_username() == "Teodor Bucht")

# control panel, only for arvid220u and teodor bucht
@app.route("/controlpanel")
def controlpanel():
    if not logged_in():
        return abort(404)
    if not is_admin():
        return abort(404)
    # list all users, with links to their userstats page
    # also list all assignments, showing solvecount and such things

    db = get_db()
    alluserscur = db.execute("SELECT * FROM users")
    allusers = alluserscur.fetchall()

    return render_template("controlpanel.html", logged_in=logged_in(), username=get_username(), allusers=allusers)



@app.route("/problemstats/<problemid>")
def problemstats(problemid):
    if not logged_in():
        return abort(404)
    # for now, only for admins
    if not is_admin():
        return abort(404)
    # list all users who have solved it
    # rank by cpu time, then by submission date
    return "problemstats"


@app.route("/user/<userid>")
def userstats(userid):
    if not logged_in():
        return abort(404)
    # for now, only for admins
    if not is_admin():
        return abort(404)
    # list all solved problems and all unsolved

    db = get_db()
    userscur = db.execute("SELECT * FROM users WHERE userid='" + userid + "'")
    userslist = userscur.fetchall()
    if len(userslist) != 1:
        return abort(404)
    user = userslist[0]

    # get all submissions
    # both as a list sorted by date, and processed as problem solved/unsolved
    submissionscur = db.execute("select * from submissions where userid ='" + userid + "' order by submissiondate DESC")
    submissions = submissionscur.fetchall()

    realsubmissions = []
    for submission in submissions:
        realsubmission = {}
        realsubmission["submissionlink"] = url_for("submission", id=submission["submissionid"], _external=True, _scheme="https")
        realsubmission["submissionid"] = submission["submissionid"]
        realsubmission["problemid"] = submission["problemid"]
        realsubmission["submissionstatus"] = submission["submissionstatus"]
        realsubmission["submissiondate"] = submission["submissiondate"]
        realsubmission["executiontime"] = getrealexecutiontime(submission["executiontime"], submission["submissionstatus"], submission["problemid"])
        realsubmissions.append(realsubmission)
    submissions = realsubmissions

    problemstatus = {}
    problemsubmissions = {}
    for submission in submissions:
        if submission["problemid"] not in problemstatus:
            problemstatus[submission["problemid"]] = submission["submissionstatus"]
            problemsubmissions[submission["problemid"]] = []
        else:
            if problemstatus[submission["problemid"]] != "Accepted":
                problemstatus[submission["problemid"]] = submission["submissionstatus"]
        problemsubmissions[submission["problemid"]].append(submission)

    problemids = os.listdir(rlpt("problems"))
    problems = []
    for problemid in problemids:
        if problemid.startswith("%"):
            continue
        problem = {}
        problem["problemid"] = problemid
        problem["problemtitle"] = getproblemtitle(problemid)
        problem["status"] = "Not Attempted"
        problem["submissions"] = []
        if problemid in problemstatus:
            problem["status"] = problemstatus[problemid]
            problem["submissions"] = problemsubmissions[problemid]
            for sub in problemsubmissions[problemid]:
                sub["problemtitle"] = problem["problemtitle"]

        problems.append(problem)

    return render_template("userstats.html", logged_in=logged_in(), username=get_username(), user=user, submissions=submissions, problems=problems)






# FEED

@app.route("/flode")
def feed():
    blogids = os.listdir(rlpt("blog"))
    blogposts = []
    for blogid in blogids:
        if blogid.startswith("%"):
            continue
        post = {}
        post["blogid"] = blogid
        post["title"] = getblogposttitle(blogid)

        statementspath = rlpt("blog/" + blogid + "/content.html")
        blogstatement = "Tomt inlägg."
        if os.path.exists(statementspath):
            # load blog statement
            with open(statementspath) as statementfile:
                blogstatement = statementfile.read()


        datepath = rlpt("blog/" + blogid + "/date.txt")
        dat = datetime.now()
        # load date 
        with open(datepath) as datefile:
            datsr = datefile.read().strip()
            dat = datetime.strptime(datsr, "%Y-%m-%d %H:%M:%S.%f")
            post["realdate"] = dat

        # convert dat to the right format
        months = ["coolt", "januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"]
        post["date"] = str(dat.day) + " " + months[dat.month] + " " + str(dat.year)

        # get problems
        problempath = rlpt("blog/" + blogid + "/problems.txt")
        problems = []
        hasproblems = True
        with open(problempath) as problemsfile:
            for line in problemsfile.readlines():
                if line.startswith("NOPROBLEMS"):
                    hasproblems = False
                    break
                problemid = line.strip("\n")
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
        extraproblempath = rlpt("blog/" + blogid + "/extraproblems.txt")
        extraproblems = []
        hasextraproblems = True
        with open(extraproblempath) as problemsfile:
            for line in problemsfile.readlines():
                if line.startswith("NOEXTRAPROBLEMS"):
                    hasextraproblems = False
                    break
                problemid = line.strip("\n")
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
                extraproblems.append(problem)

        post["problems"] = problems
        post["hasproblems"] = hasproblems and (len(problems) != 0)
        post["extraproblems"] = extraproblems
        post["hasextraproblems"] = hasextraproblems and (len(extraproblems) != 0)

        # maybe add images to the problem statement
        blogstatement = addextradatatoblogpost(blogstatement, blogid)

        post["content"] = blogstatement

        blogposts.append(post)

    # sort by date
    blogposts = sorted(blogposts, key=lambda k: k["realdate"], reverse=True)
    for b in blogposts:
        b.pop("realdate", None)

    return render_template("feed.html", logged_in=logged_in(), username=get_username(), blogposts=blogposts)






if __name__ == "__main__":
    app.run()
