import sys
import pytest
import requests
import json
from requests_ntlm import HttpNtlmAuth
sys.path.append('..')
from config import *
from RiotApiCalls import *
from championsRequest import *


def test_ChampionPage():
    req = requests.get("http://localhost:5000/champions")
    statCode = int(req.status_code)
    assert statCode == 200

def test_SpecificChampionPage():
    req = requests.get("http://localhost:5000/champion?champion=Annie")
    statCode = int(req.status_code)
    assert statCode == 200

def test_SummonerPage():
    req = requests.get("http://localhost:5000/summoner?summoner=Mealsz&region=EUW1")
    statCode = int(req.status_code)
    assert statCode == 200

def test_ChampionSummonerPage():
    req = requests.get("http://localhost:5000/summoner/champion?summoner=Mealsz&region=EUW1&champion=Annie")
    statCode = int(req.status_code)
    assert statCode == 200

def test_IndexPage():
    req = requests.get("http://localhost:5000/")
    statCode = int(req.status_code)
    assert statCode == 200

def test_PostPredictionData():
    headers = {
        'Content-type': 'application/json',
    }
    json_data = { 
        "MinionsKilled": 1,
        "kills": 4,
        "assists": 32,
        "deaths": 0,
        "TotalGold":100,
        "DmgDealt": 43200,
        "DmgTaken": 3200,
        "DragonKills":5,
        "BaronKills": 2,
        "GameDuration": 3200,
        "TurretDmgDealt":4,
        "ChampionFk": 5,
        "masteryPoints": 2,
        "EnemyChampionFk":4,
        "lane":1
      }

    response = requests.post('http://localhost:5000/post_json', headers=headers, json=json_data)
    assert int(response.status_code) == 200
    pred = response.content
    pred = pred.decode('utf-8')
    pred = json.loads(pred)
    assert pred['pred'] == "1" 

