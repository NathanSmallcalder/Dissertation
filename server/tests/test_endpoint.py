import sys
import pytest
import requests
import json
from requests_ntlm import HttpNtlmAuth
sys.path.append('..')
from config import *
from RiotApiCalls import *
from championsRequest import *

api_key= api_key
db = pymysql.connect(host=host,user='o1gbu42_StatTracker',passwd=sql_password,database =sql_user)
cursor = db.cursor()

def test_IndexPage():
    req = requests.get("http://172.17.0.2:5000")
    statCode = int(req.status_code)
    assert statCode == 200

def test_IndexPage():
    req = requests.get("http://172.17.0.2:5000")
    statCode = int(req.status_code)
    assert statCode == 200

def test_IndexPage():
    req = requests.get("http://172.17.0.2:5000/predictorSend?prediction=[1,24 ,72,5,1,2,5255,255,1,2000,52,2000,5,5]")
    statCode = int(req.status_code)
    assert statCode == 200

def test_PostPredictionData():
    headers = {
        'Content-type': 'application/json',
    }

    json_data = {
        'ChampionFk': '1',
        'MinionsKilled': '20',
        'kills': '1',
        'deaths': '1',
        'assists': '1',
        'lane': '1',
        'DmgDealt': '1',
        'DmgTaken': '1',
        'TurretDmgDealt': '1',
        'TotalGold': '1',
        "EnemyChampionFk": '1',
        'GameDuration': '2000',
        'DragonKills': '1',
        'BaronKills': '0',
    }

    response = requests.post('http://localhost:5000/post_json', headers=headers, json=json_data)
    assert int(response.status_code) == 200
    pred = response.content
    pred = pred.decode('utf-8')
    pred = json.loads(pred)
    assert pred['pred'] == "0" 


test_PostPredictionData()