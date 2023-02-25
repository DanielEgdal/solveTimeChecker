import json
from collections import defaultdict
import requests
from typing import List

class Competitor():
    def __init__(self,name,id) -> None:
        self.id = id
        self.name = name
        self.solvesRegged = 0
        self.solvesDone = 0
        self.DNFCount = 0
        self.timeUsed = 0
        self.printTime = 0

    def cal_print(self):
        self.printTime = convert(self.timeUsed)

def convert(seconds):
    seconds = seconds/100
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    seconds = "{:05.2f}".format(seconds)
      
    return f"%d:%02d:{seconds}" % (hour, minutes)

def getCompetitors(data,eventsCheck):
    eventOv = {}
    for event in data['events']:
        if eventToUse(event['id'],eventsCheck):
            eventOv[event['id']] = event['rounds'][0]['format']
    personOv = {}
    for person in data['persons']:
        if person['registration']:
            if person['registration']['status'] == 'accepted':
                # print(person)
                c = Competitor(person['name'],person['registrantId'])
                for event in person['registration']['eventIds']:
                    if eventToUse(event,eventsCheck):
                        if eventOv[event] == 'a':
                            c.solvesRegged += 5
                        elif eventOv[event] in ['m','3']:
                            c.solvesRegged += 3
                        else:
                            print('format not defined',event)
                    personOv[person['registrantId']] = c
    return personOv

def eventToUse(eventId,Events:List):
    if Events:
        if eventId in Events:
            return True
        else:
            return False
    return True

def getSolveTime(data,eventsCheck):
    personOv = getCompetitors(data,eventsCheck)

    c = defaultdict(int)

    for val in data["events"]:
        if val['id'] != '333mbf' and eventToUse(val['id'],eventsCheck):
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
    for person in personOv:
        personOv[person].cal_print()
    overview = [(personOv[id].name,competitor) for id,competitor in personOv.items()]
    return overview

def applySorting(overview,which=0):
    if which == 0:
        overview.sort(key=lambda x:x[1].timeUsed, reverse=True) # By time
    elif which == 1:
        overview.sort(key=lambda x:x[0], reverse=False) # By name
    elif which == 2:
        overview = [(name, comp) for name, comp in overview if comp.solvesRegged != comp.solvesDone] # Show people with solves left
        # Even if you quit the person on WCA live, they will still be listed here.
    return overview

def makeHtml(data,eventsCheck,which=0):
    overview = applySorting(getSolveTime(data,eventsCheck),which)
    start = ["<table border=1>","<tr><td>Name</td><td>Time Used</td><td>DNFs</td><td>Attempts Entered</td><td>Solves Regged</td></tr>"]
    for val in overview:
        start.append(f"<tr><td>{val[0][:30]}</td><td>{val[1].printTime}</td><td>{val[1].DNFCount}</td><td>{val[1].solvesDone}</td><td>{val[1].solvesRegged}</td></tr>")
    start.append("</table>")
    return "\n".join(start)
# print(makeHtml("HDCIIIRisbjerggaard2023"))

# runCheck('HDCIIIRisbjerggaard2023')
