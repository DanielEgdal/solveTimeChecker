import subprocess
from copy import deepcopy
from time import sleep
import json
import requests
import pytz
from pandas import Timestamp
import os

def get_me(header):
    return requests.get("https://www.worldcubeassociation.org/api/v0/me",headers=header)
    
def get_coming_comps(header):
    comps_json = json.loads(requests.get("https://www.worldcubeassociation.org/api/v0/competitions?managed_by_me=true",headers=header).content)
    comps=  [(comp['name'],comp['id']) for comp in comps_json if Timestamp(comp['end_date']) > Timestamp.now()]
    return comps


def getWcif(id,header):
    wcif = requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif",headers=header)
    # assert wcif.status_code == 200
    return json.loads(wcif.content),wcif.status_code

def getWCIFPublic(id):
    wcif = requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif/public")
    return json.loads(wcif.content),wcif.status_code
