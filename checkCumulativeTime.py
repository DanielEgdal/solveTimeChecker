import json
from collections import defaultdict
import requests

class Competitor():
    def __init__(self,name,id) -> None:
        self.id = id
        self.name = name
        self.solvesRegged = 0
        self.solvesDone = 0
        self.DNFCount = 0
        self.timeUsed = 0

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

def getCompetitors(data):
    eventOv = {}
    for event in data['events']:
        eventOv[event['id']] = event['rounds'][0]['format']
    personOv = {}
    for person in data['persons']:
        try:
            if person['registration']['status'] == 'accepted':
                # print(person)
                c = Competitor(person['name'],person['registrantId'])
                for event in person['registration']['eventIds']:
                    if eventOv[event] == 'a':
                        c.solvesRegged += 5
                    elif eventOv[event] in ['m','3']:
                        c.solvesRegged += 3
                    else:
                        print('format not defined',event)
                    personOv[person['registrantId']] = c
        except Exception as e:
            # print('not found',person['name'],e)
            pass
    return personOv

def runCheck(compid,which=1):

    response,header = getWcif(compid)
    data = json.loads(response.content)
    personOv = getCompetitors(data)

    c = defaultdict(int)

    for val in data["events"]:
        if val['id'] != '333mbf':
            for val2 in val['rounds']:
                for val3 in val2['results']:
                    for val4 in val3['attempts']:
                        tId = val3['personId']
                        if val4['result'] > 0:
                            personOv[tId].timeUsed += val4['result']
                        elif val4['result'] == -1:
                            personOv[tId].DNFCount += 1
                        elif val4['result'] == -2: # DNS, pass
                            pass
                        else: # No result entered
                            continue
                        personOv[tId].solvesDone +=1

    overview = [(personOv[id].name,competitor) for id,competitor in personOv.items()]

    if which == 0:
        overview.sort(key=lambda x:x[1].timeUsed, reverse=True) # By time
    elif which == 1:
        overview.sort(key=lambda x:x[0], reverse=False) # By name
    elif which == 2:
        overview = [(name, comp) for name, comp in overview if comp.solvesRegged != comp.solvesDone] # Show people with solves left
        # Even if you quit the person on WCA live, they will still be listed here.

    return overview

def makeHtml(compid,which=1):
    overview = runCheck(compid,which)
    start = ["<table border=1>","<tr><td>Name</td><td>Time Used</td><td>DNFs</td><td>Attempts Entered</td><td>Solves Regged</td></tr>"]
    for val in overview:
        start.append(f"<tr><td>{val[0][:25]}</td><td>{convert(val[1].timeUsed)}</td><td>{val[1].DNFCount}</td><td>{val[1].solvesDone}</td><td>{val[1].solvesRegged}</td></tr>")
    start.append("</table")
    return "\n".join(start)
# print(makeHtml("HDCIIIRisbjerggaard2023"))

# runCheck('HDCIIIRisbjerggaard2023')
