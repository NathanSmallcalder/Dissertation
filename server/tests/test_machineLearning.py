import sys
import pytest
import requests

sys.path.append('../')
from config import *
from RiotApiCalls import *

sys.path.append('../mlAlgorithms')

from randomForest import *

rf = getRandomForest()

def test_rf_ObviousLoss():
    prediction = randomForestPredict(rf,1,0,1,200,5000,0,2000,5,1220,0,0)
    assert int(prediction) == 0

def test_rf_MostLikelyLoss():
    prediction = randomForestPredict(rf,1,100,1,5000,10000,2,2500,5,1900,0,0)
    assert int(prediction) == 0

def test_rf_MostLikelyWin():
    prediction = randomForestPredict(rf,1,100,1,6000,4399,2,2500,5,2500,2,1)
    assert int(prediction) == 1

def test_rf_ObviousWin():
    prediction = randomForestPredict(rf,1,259,1,10000,4399,5,5999,5,3000,4,2)
    assert int(prediction) == 1

