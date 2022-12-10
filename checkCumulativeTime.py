import json
from collections import defaultdict
import requests

def getWcif(id):
    # https://www.worldcubeassociation.org/oauth/authorize?client_id=5U1L9es8uMLPEPM_qbQuWWOqIY8NJiXcWC_4V1sLLgw&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=token&scope=manage_competitions+public
    with open('authcode','r') as f:
        token = f.readline().strip('\n')
    header = {'Authorization':f"Bearer {token}"}
    
    wcif = requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif",headers=header)
    assert wcif.status_code == 200
    return wcif,header

def convert(seconds):
    seconds = seconds/100
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def runCheck(compid,which=1):

    response,header = getWcif(compid)
    data = json.loads(response.content)

    c = defaultdict(int)
    dnfcounter = defaultdict(int)

    for val in data["events"]:
        if val['id'] != '333mbf':
            for val2 in val['rounds']:
                for val3 in val2['results']:
                    for val4 in val3['attempts']:

                        if val4['result'] > 0:
                            c[val3['personId']] +=val4['result']
                        elif val4['result'] == -1:
                            dnfcounter[val3['personId']] += 1

    translater = {}

    for val in data['persons']:
        translater[val['registrantId']] = val['name']


    overview = [(name,value) for name,value in c.items()]

    if which == 0:
        overview.sort(key=lambda x:x[1], reverse=True) # By time
    elif which == 1:
        overview.sort(key=lambda x:translater[x[0]], reverse=False) # By name

    # returnList = [f"{translater[val[0]][:15]}\tTime used: {convert(c[val[0]])}\tDNFs: {dnfcounter[val[0]]}" for val in overview]
    
    # return "\n".join(returnList)
    return overview,c,dnfcounter,translater

def makeHtml(compid,which=1):
    overview,c,dnfcounter,translater = runCheck(compid,which)
    start = ["<table border=1>","<tr><td>Name</td><td>Time Used</td><td>DNFs</td></tr>"]
    for val in overview:
        start.append(f"<tr><td>{translater[val[0]][:15]}</td><td>{convert(c[val[0]])}</td><td>{dnfcounter[val[0]]}</td></tr>")

    start.append("</table")
    return "\n".join(start)
# print(makeHtml("HDCIIHvidovre2022"))
