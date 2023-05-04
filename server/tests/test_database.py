import sys
import pytest
import requests
sys.path.append('..')
from config import *
from RiotApiCalls import *
from databaseQuries import *

# gets common items on given champId
# If more than 4 in itemList, pass
def test_commonItems():
    items = commonItems(1)
    assert len(items) > 4

# gets best Runes on given champId
# If more than 4 in runesList, pass
def test_bestRunes():
    list = bestRunes(1)
    assert len(list) == 5

# gets common Runes on given champId
# If more than 4 in runesList, pass
def test_commonRunes():
    list = commonRunes(1)
    print(len(list))
    assert len(list) == 5

# gets common Runes on given champId
# If more than 4 in runesList, pass
def test_commonSecondaryRunes():
    list = commonSecondaryRunes(1)
    assert len(list) == 3

# gets best Runes on given champId
# If more than 4 in runesList, pass
def test_bestSecondaryRunes():
    list = bestSecondaryRunes(1)
    print(len(list))
    assert len(list) == 3

# gets best lane on given champId
# If more than 4 in runesList, pass
# ChampId 1 = Annie, Should be Lane MIDDLE
def test_laneFromDatabase():
    lane = laneFromDatabase(1)
    print(lane)
    assert lane == "MIDDLE"

# gets Kda on given champ
# Should return dict format of {Kills:x} , {Deaths:x} , {assists: x}
def test_kdaFromDatabase():
    kda = kdaFromDatabase(1)
    assert len(kda) > 3

# gets Kda on given champ and summoner
# Should return dict format of {Kills:x} , {Deaths:x} , {assists: x}
def test_kdaFromDatabaseSumm():
    kda = kdaFromDatabaseSummoner(876,4)
    assert len(kda) > 3

# gets best RUNES on given champId
# If more than 4 in runesList, pass
def test_bestItems():
    BestItems = bestItems(1)
    print(len(BestItems))
    assert len(BestItems) == 5

#Gets avgGold on each rank
# For each champion, data should be above 2 ranks.
def test_avgGold():
    AvgGold = avgGold(1)
    print(AvgGold)
    assert len(AvgGold) > 2

#Gets avgGold on each Summoner
# Length of dictionary should be 2
def test_avgGoldSummoner():
    avgGold = avgGoldSummoner(876,4)
    assert len(avgGold) > 1

#Gets avgDmgDealt on each rank
# For each champion, data should be above 2 ranks.
def test_avgDmgDealt():
    AvgDmg = avgDmgDealt(1)
    assert len(AvgDmg) > 3

#Gets avgDmgTaken on each rank
# For each champion, data should be above 2 ranks.
def test_avgDmgTaken():
    AvgDmgTaken = avgDmgTaken(1)
    assert len(AvgDmgTaken) > 3

#Gets avgDmgTaken on each Summoner
# Length of dictionary should be 2
def test_avgDmgTakenSummoner():
    avgDmgTakenSumm = avgDmgTakenSummoner(876,4)
    avgDmgTakenSumm = avgDmgTakenSumm[0]['AVG(`MatchStatsTbl`.`DmgTaken`)']
    assert avgDmgTakenSumm > 5


#Gets avgMinions on each rank
# For each champion, data should be above 2 ranks.
def test_avgMinions():
    AvgMinions = avgMinions(1)
    assert len(AvgMinions) > 3

#Gets avgMinions on each Summoner
# Length of dictionary should be 2
def test_avgMinionsSummoner():
    avgMinion = avgMinionsSummoner(876,4)
    avgMinion = avgMinion[0]['AVG(`MatchStatsTbl`.`MinionsKilled`)']
    assert avgMinion > 0

#Gets avgMinions on each rank
# Annie was the champ with the most data
# Kills should be higher on each champion.
def test_champKills():
    ChampKills =champKills(1)
    assert ChampKills > 250

#Gets avgMinions on each rank
# Annie was the champ with the most data
# Win should be higher on each champion as more data is collected.
def test_champWins():
    champW = champWins(1)
    assert champW > 5

#Gets avgMinions on each rank
# Lilia was the champ chosen
# Games should be higher on each champion as more data is collected.
def test_totalGames():
    TotalGames = totalGames(876)
    assert TotalGames > 5

# Gets avgDmgDealt on summoner
# Should not be 0.
def test_avgDmgDealtSummoner():
    avg = avgDmgDealtSummoner(876,4)
    avg = avg[0]['AVG(`MatchStatsTbl`.`DmgDealt`)']
    assert avg > 5

#Gets avgMinions on each rank
# Annie was the champ with the most data
# Games should be higher on each champion as more data is collected.
def test_totalGames():
    totalGamesOnAnnie = totalGames(1)
    assert int(totalGamesOnAnnie) < 100000

# Gets total games on champion and summoner
# Should be higher than 5.
def test_totalGamesOnSummoner():
    totalGamesSumm = totalGamesSummoner(876,4)
    assert int(totalGamesSumm['COUNT(`MatchStatsTbl`.Win)']) > 10

# Gets wins on champion and summoner
# Should be higher than 5.
def test_champWinsSummoner():
    champWinsSumm = champWinsSummoner(876,4)
    assert int(champWinsSumm[0]['COUNT(`MatchStatsTbl`.Win)']) > 5

# Gets the most common lane played from summoner/champ
# 67(Vayne) , 4(Lil Nachty), Role should be BOTTOM
def test_laneFromDatabaseSummoner():
    lane = laneFromDatabaseSummoner(67,4)
    assert lane == "BOTTOM"

#Returns summonerID from database
#This summoner has an id of 4.
def test_getSummonerIdFromDatabase():
    id = getSummonerIdFromDatabase("Lil Nachty")
    assert id == 4

#Retrieve ItemLink from itemId.
#Request itemLink.
def test_getItemLink():
    link = getItemLink(1001)
    req = requests.get(link)
    assert req.status_code == 200

#Gets all champions
#Length should be more than 130 (As champs get added tests will still pass)
def test_getAllChampions():
    champs = getAllChampions()
    assert len(champs) > 130

# Gets Best Players
# If more than 5. pass
def test_getBestPlayers():
    best = getBestPlayers()
    assert len(best) > 5

#Gets ChampionTable
# If more than 130 champs, pass
# Else fail
def test_getChampionAverages():
    champs = getChampionAverages()
    assert len(champs) > 130

#Gets Best players on ChampionTable
# If more than 5, pass
# Else fail
def test_getChampionBestPlayers():
    best = getChampionBestPlayers(1)
    assert len(best) > 5

# Gets Avg Minions Per rank
# If more than 4 instances, pass
def test_avgMinionsAll():
    AvgMinionsRanked = avgMinionsAll()
    avgMinionsStatsSummoner = avgMinionsSummonerAll(4)
    assert len(AvgMinionsRanked) > 4
