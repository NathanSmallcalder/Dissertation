import sys
import pytest
import requests
sys.path.append('..')
from config import *
from RiotApiCalls import *
from databaseQuries import *

def test_commonItems():
    commonItems(1)

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

def test_kdaFromDatabaseSumm():
    kda = kdaFromDatabaseSummoner(876,4)

def test_bestItems():
    BestItems = bestItems(1)
    print(len(BestItems))
    assert len(BestItems) == 5

def test_avgGold():
    AvgGold = avgGold(1)
    print(AvgGold)

def test_avgGoldSummoner():
    avgGold = avgGoldSummoner(876,4)

def test_avgDmgDealt():
    AvgDmg = avgDmgDealt(1)
    print(AvgDmg)

def test_avgDmgDealtSummoner():
    avgDmgDealtSummoner(876,4)

def test_avgDmgTaken():
    AvgDmgTaken = avgDmgTaken(1)

def test_avgDmgTakenSummoner():
    avgDmgTakenSumm = avgDmgTakenSummoner(876,4)
    'AVG(`MatchStatsTbl`.`DmgTaken`)'

def test_avgMinions():
    AvgMinions = avgMinions(1)

def test_avgMinionsSummoner():
    avgMinion = avgMinionsSummoner(876,4)
    avgMinion['AVG(`MatchStatsTbl`.`MinionsKilled`)']

def test_champKills():
    ChampKills =champKills(1)
    print(ChampKills)

def test_champWins():
    champW = champWins(1)
    assert champW > 5

def test_totalGames():
    TotalGames = totalGames(1)
    print(TotalGames)

def test_avgDmgDealtSummoner():
    avg = avgDmgDealtSummoner(5,1)
    print(avg)

def test_totalGames():
    totalGamesOnAnnie = totalGames(1)
    print(totalGamesOnAnnie)
    assert int(totalGamesOnAnnie) < 5999

def test_totalGamesOnSummoner():
    totalGamesSumm = totalGamesSummoner(876,4)
    assert int(totalGamesSumm['COUNT(`MatchStatsTbl`.Win)']) > 10

def test_champWinsSummoner():
    champWinsSumm = champWinsSummoner(876,4)
    assert int(champWinsSumm['COUNT(`MatchStatsTbl`.Win)'])

def test_laneFromDatabaseSummoner():
    laneFromDatabaseSummoner(876,4)

def test_getSummonerIdFromDatabase():
    id = getSummonerIdFromDatabase("Lil Nachty")
    assert id == 4

def test_getItemLink():
    getItemLink(1)

def test_getAllChampions():
    getAllChampions()

def test_getBestPlayers():
    getBestPlayers()

def test_getChampionAverages():
    getChampionAverages

def test_getChampionBestPlayers():
    getChampionBestPlayers()


test_champWinsSummoner()