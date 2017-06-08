#!/usr/bin/env python3
import random, os, sys, binascii
import subprocess

from flask import *
app = Flask(__name__)


@app.route("/")
def main():
    #return redirect(url_for("file?id=" + binascii.b2a_hex(os.urandom(15)).decode("utf-8"), scheme="https"))
    return redirect(url_for("loadfile", id=binascii.b2a_hex(os.urandom(15)).decode("utf-8"), _external=True, _scheme="https"))

@app.route("/file", methods=["GET"])
def loadfile():
    filecontents = "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    \n    \n    return 0;\n}"
    fileid = request.args["id"]
    if os.path.exists("data/" + fileid + ".cpp"):
        with open("data/" + fileid + ".cpp", "r") as savedfile:
            filecontents = savedfile.read()
    return render_template("index.html", fileid=fileid, filecontents=json.dumps(filecontents))


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
