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
        "MinionsKilled": 258,
        "kills": 25,
        "assists": 56,
        "deaths": 1,
        "TotalGold": 32355,
        "DmgDealt": 422425,
        "DmgTaken": 24567,
        "DragonKills": 4,
        "BaronKills": 3,
        "GameDuration": 200,
        "TurretDmgDealt": 4,
        "ChampionFk": 1,
        "masteryPoints": 42257,
        "EnemyChampionFk":2 ,
        "lane": 1
      }

    response = requests.post('http://localhost:5000/predictSolo', headers=headers, json=json_data)
    assert int(response.status_code) == 200
    pred = response.content
    pred = pred.decode('utf-8')
    pred = json.loads(pred)
    assert pred['pred'] == "1" 

def test_teamPrediction():
    
    headers = {
        'Content-type': 'application/json',
    }

    json_data = {
        "B1Summ": "Mealsz",
        "B2Summ": "Ehhhh",
        "B3Summ": "Itwoznotmee",
        "B4Summ": "Lil Nachty",
        "B5Summ": "Forza Napøli ",
        "R1Summ": "Primabel Ayuso",
        "R2Summ": "NateNatilla",
        "R3Summ": "sweet af",
        "R4Summ": "Fedy9 ",
        "R5Summ": "ChampagneCharlie ",
        "B1": 44,
        "B2": 876,
        "B3": 136,
        "B4": 221,
        "B5": 74,
        "R1": 122,
        "R2": 20,
        "R3": 99,
        "R4": 202,
        "R5": 412,
        'Region':"EUW1"
    }
    response = requests.post('http://localhost:5000/teamData', headers=headers, json=json_data)
    assert int(response.status_code) == 200
    pred = response.content
    pred = pred.decode('utf-8')
    pred = json.loads(pred)
    assert prediction['BlueTeam'] == 0 or 1



def test_summData():
    req = requests.get("http://localhost:5000/summData?summoner=Mealsz&region=EUW1&champ=1&enemyChamp=3&lane=5")
    statCode = int(req.status_code)
    print(statCode)
    assert statCode == 200


test_summData()