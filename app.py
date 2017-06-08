#!/usr/bin/env python3
import random, os, sys, binascii
import subprocess
import sqlite3
from hashlib import md5

from flask import *
app = Flask(__name__)
app.config.from_object(__name__) # configure from this file
app.config["SECRET_KEY"] = "\x9d\xe4AS\xa5\xe6\xc7e\xb9\xa3:\xd1x\x17\x81V\x91p\xc1\xb0\x84\xaaBQd\xfbnZ\x96\x0e\xbd\xd7"

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





# Log in

def get_user():
    if not logged_in():
        return {}
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE userid = '" + user_id() + "'")
    user = cur.fetchone()
    return user


def user_id():
    if not logged_in():
        return ""
    return session["userid"]

def logged_in():
    return "userid" in session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passwordhash = str(md5(request.form["password"]))
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = '" + username + "' AND passwordhash = '" + passwordhash + "'")
        if len(cur.fetchall()) == 0:
            return render_template("login.html", failedattempt = True)
        user = cur.fetchone()
        session["userid"] = user["userid"]
        return redirect(url_for('home'))
    return render_template("login.html", failedattempt = False)

@app.route("/logout")
def logout():
    session.pop("userid")
    return redirect(url_for('home'))





@app.route("/")
def home():
    #return redirect(url_for("file?id=" + binascii.b2a_hex(os.urandom(15)).decode("utf-8"), scheme="https"))
    #return redirect(url_for("loadfile", id=binascii.b2a_hex(os.urandom(15)).decode("utf-8"), _external=True, _scheme="https"))
    return render_template("home.html")

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
        submissions = {}
        if logged_in():
            # get submission id, date, status
            db = get_db()
            cur = db.execute("SELECT userid, problemid, submissionid, submissiontext, submissiondate FROM submissions WHERE userid = '" + user_id() + "' AND problemid = '" + problemid + "' ORDER BY submissiondate")
            submissions = cur.fetchall()
        print(problemstatement)
        return render_template("problem.html", problemid=problemid, problemstatement=problemstatement, submissions=json.dumps(submissions), samples=samples)
    else:
        abort(404)

"""
@app.route("/file", methods=["GET"])
def loadfile():
    filecontents = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    \n    \n    return 0;\n}"
    fileid = request.args["id"]
    if os.path.exists("data/" + fileid + ".cpp"):
        with open("data/" + fileid + ".cpp", "r") as savedfile:
            filecontents = savedfile.read()
    return render_template("index.html", fileid=fileid, filecontents=json.dumps(filecontents))
"""

"""
@app.route("/savefile", methods=["POST"])
def savefile():
    # get data from post
    indata = request.data.decode("utf-8")
    fileid, cpp = indata.split("%%%arvidlunnemarkwowcool%%%")
    
    # create the filename
    filename = "data/" + fileid + ".cpp"
    # write to the file
    with open(filename, "w") as cppfile:
        cppfile.write(cpp)

    return "successfully saved"
"""





@app.route("/compileandrun", methods=["POST"])
def compileandrun():

    # get data from post
    indata = request.data.decode("utf-8")
    fileid, cpp, inputdata = indata.split("%%%arvidlunnemarkwowcool%%%")

    # create the filename
    filename = "data/" + fileid + ".cpp"
    exfilename = filename + ".x"
    infilename = filename + ".in"
    compiledfilename = filename + ".compiled"
    # write to the file
    with open(filename, "w") as cppfile:
        cppfile.write(cpp)

    # create the infile
    with open(infilename, "w") as infile:
        infile.write(inputdata)

    # check if compiled file is different
    compileddifferent = True
    if os.path.exists(compiledfilename):
        with open(compiledfilename, "r") as compiledfile:
            if compiledfile.read() == cpp:
                compileddifferent = False
    # compile the file to the exfile
    if compileddifferent:
        try:
            subprocess.call(["g++", "-std=c++11", "-fsanitize=address,undefined", "-o", exfilename, filename])
        except Exception as exception:
            os.remove(infilename)
            return "A compile error occurred."
        if not os.path.exists(exfilename):
            os.remove(infilename)
            return "A compile error occurred."
        # write to the compile file
        with open(compiledfilename, "w") as cppfile:
            cppfile.write(cpp)

    # get the output
    output = ""
    try:
        with open(infilename, "rb") as infile:
            output = subprocess.check_output([os.path.abspath(exfilename)], stdin=infile, timeout=10).decode("utf-8")
    except Exception as exception:
        os.remove(infilename)
        return "A runtime error occurred."

    # remove temporary files
    os.remove(infilename)

    # return the output
    return output


if __name__ == "__main__":
    app.run()
