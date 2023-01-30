import flask
from wsgiref.simple_server import make_server
import re
from markupsafe import escape

from checkCumulativeTime import makeHtml

from flask import Flask
app = Flask(__name__)


@app.route('/')
def startPage():
    return "Hi, enter a competition ID into the URL"


@app.route('/<compid>')
def calculate(compid):

    escapedCompid = escape(compid)
    pattern = re.compile("^[a-zA-Z\d]+$")
    
    if pattern.match(escapedCompid):
        printingString = makeHtml(escapedCompid)
        return printingString
    else:
        return "doesn't match correct format"

@app.route('/<compid>/<which>')
def calculateOtherOrder(compid,which):

    escapedCompid = escape(compid)
    escapedWhich = escape(which)
    pattern = re.compile("^[a-zA-Z\d]+$")
    pattern2 = re.compile("^(0|1|2)$")
    
    if pattern.match(escapedCompid) and pattern2.match(escapedWhich):
        printingString = makeHtml(escapedCompid,int(escapedWhich))
        return printingString
    else:
        return "doesn't match correct format"

# host = '' 
host = '0.0.0.0'
port = 8000
# app.run(host=host,port=port)

with make_server(host,port,app) as server:
    print(f"serving on http://{host}:{port}/")
    server.serve_forever()
