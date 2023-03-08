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
    req = requests.get("http://localhost:5000/champion")
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

