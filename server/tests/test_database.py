import sys
import pytest
import requests
sys.path.append('..')
from config import *
from RiotApiCalls import *
from databaseQuries import *


def test_bestRunes():
    list = bestRunes(1)
    assert len(list) == 5

def test_commonRunes():
    list = commonRunes(1)
    print(len(list))
    assert len(list) == 5

def test_commonSecondaryRunes():
    list = commonSecondaryRunes(1)
    assert len(list) == 3

def test_bestSecondaryRunes():
    list = bestSecondaryRunes(1)
    print(len(list))
    assert len(list) == 3

def test_laneFromDatabase():
    lane = laneFromDatabase(1)
    print(lane)
    assert lane == "MIDDLE"

def test_kdaFromDatabase():
    kda = kdaFromDatabase(1)

def test_bestItems():
    BestItems = bestItems(1)
    print(len(BestItems))
    assert len(BestItems) == 5

def test_avgGold():
    AvgGold = avgGold(1)
    print(AvgGold)

def test_avgDmgDealt():
    AvgDmg = avgDmgDealt(1)
    print(AvgDmg)

def test_avgDmgTaken():
    AvgDmgTaken = avgDmgTaken(1)
    print(AvgDmgTaken)

def test_avgMinions():
    AvgMinions = avgMinions(1)
    print(AvgMinions)

def test_champKills():
    ChampKills =champKills(1)
    print(ChampKills)

def test_champWins():
    ChampWins = champWins(1)
    print(ChampWins)

def test_totalGames():
    TotalGames = totalGames(1)
    print(TotalGames)

def test_avgDmgDealtSummoner():
    avg = avgDmgDealtSummoner(5,1)
    print(avg)
