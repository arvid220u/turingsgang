#!/usr/bin/env python3
from datetime import datetime

import os, sys
name = input()
if len(name.split()) != 1:
    print("must be onw word")
    sys.exit()

if os.path.exists("blog/" + name):
    print("Potentially dangerous  – blogid already taken. Continue? (y/n)")
    ans = input()
    if ans != "y" and ans != "Y":
        sys.exit()
else:
    os.makedirs("blog/" + name)

with open("blog/" + name + "/content.html", "w") as cf:
    cf.write("blogcontent")
with open("blog/" + name + "/title.txt", "w") as cf:
    cf.write("blogtitle")
with open("blog/" + name + "/showintroductoryproblems.txt", "w") as cf:
    cf.write("NO")
with open("blog/" + name + "/introductoryproblems.txt", "w") as cf:
    cf.write("NOINTRODUCTORYPROBLEMS")
with open("blog/" + name + "/problems.txt", "w") as cf:
    cf.write("NOPROBLEMS")
with open("blog/" + name + "/extraproblems.txt", "w") as cf:
    cf.write("NOEXTRAPROBLEMS")
with open("blog/" + name + "/date.txt", "w") as cf:
    cf.write(str(datetime.now()))

