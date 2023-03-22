import sys
import pytest
import requests

sys.path.append('../')
from config import *
from RiotApiCalls import *

from mlAlgorithms import SoloPredictor
from mlAlgorithms import TeamPredictor


rf = randomForestSolo.getRandomForest()
rfTeam = randomForestMultiRun()

def test_rf_ObviousLossTeam():
    dataset = {
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
        "BlueBaronKills": 1,
        "BlueRiftHeraldKills":2 ,
        "BlueDragonKills": 2.33,
        "BlueTowerKills": 9,
        "BlueKills": 37,

        "RedBaronKills": 0.3333,
        "RedRiftHeraldKills": 0,
        "RedDragonKills": 0,
        "RedTowerKills": 0,
        "RedKills":0,
    }

    prediction = randomForestPredictMulti(rfTeam,dataset)
    assert prediction[0][0] == 0
    assert prediction[0][1] == 1

test_rf_ObviousLossTeam()

def test_rf_ObviousLossTeam():
    dataset = {
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
        "BlueBaronKills": 1,
        "BlueRiftHeraldKills":2,
        "BlueDragonKills": 2.33,
        "BlueTowerKills": 9,
        "BlueKills": 37,

        "RedBaronKills": 0.3333,
        "RedRiftHeraldKills": 0.2,
        "RedDragonKills": 0,
        "RedTowerKills": 2,
        "RedKills": 15,
    }

    prediction = randomForestPredictMulti(rfTeam,dataset)
    assert prediction[0][0] == 0
    assert prediction[0][1] == 1


def test_rf_LessObviousLossTeam():
    dataset = {
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
        "BlueBaronKills": 1,
        "BlueRiftHeraldKills":2 ,
        "BlueDragonKills": 2.33,
        "BlueTowerKills": 9,
        "BlueKills": 37,

        "RedBaronKills": 1,
        "RedRiftHeraldKills": 1.2,
        "RedDragonKills": 2,
        "RedTowerKills": 4,
        "RedKills": 23,
    }

    prediction = randomForestPredictMulti(rfTeam,dataset)
    assert prediction[0][0] == 0
    assert prediction[0][1] == 1


def test_rf_ObviousLoss():
    prediction = randomForestPredict(rf,1,0,0,50,2,1,200, 200,5000,0,2000,5,1220,0,0)
    assert int(prediction) == 0

def test_rf_MostLikelyLoss():
    prediction = randomForestPredict(rf,1,100,1,10,5,2,250,5000,10000,2,2500,5,1900,0,0)
    assert int(prediction) == 0

def test_rf_MostLikelyWin():
    prediction = randomForestPredict(rf,1,100,20,3,10,1,4000,6000,4399,2,2500,5,2500,2,1)
    assert int(prediction) == 1

def test_rf_ObviousWin():
    prediction = randomForestPredict(rf,1,259,25,1,25,5,40000,30000,4399,5,5999,5,3000,4,2)
    assert int(prediction) == 1

