import sys
import pytest
import requests

sys.path.append('..')
from config import *
from RiotApiCalls import *

api_key= api_key
db = pymysql.connect(host=host,user='o1gbu42_StatTracker',passwd=sql_password,database =sql_user)
cursor = db.cursor()

######## Gets an Image from a ChampionID
def test_ChampionImgSingle():
    champ = getChampImagesSingle(1)
    req = requests.get(champ)
    assert int(req.status_code) == 200
    assert str(champ) == "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/Annie.png"

test_ChampionImgSingle()
######## Champion Details - ChampionPage
def test_ChampionDetails():
    data = getChampDetails("Annie")
    assert int(data['key']) == 1

#### Champion Video Abilities - ChampionPage
def test_getChampAbilities():
    championStats = getChampDetails("Annie")
    data = getChampAbilities(championStats)
    req = requests.get(data['passive']['abilityVideoPath'])
    print(req.status_code)
    assert int(req.status_code) == 200

###### Champ Spell Images -- Champion Page
def test_getChampSpellImages():
    champName = "Annie"
    championStats = getChampDetails(champName)
    ChampionAbilities = getChampAbilities(championStats)
    data = getChampSpellImages(ChampionAbilities)
    req = requests.get(ChampionAbilities['passive']['abilityIconPath'] )
    assert int(req.status_code) == 200

test_getChampSpellImages()

#### Champ Images -- Summoner Page - Mastery Section
def test_getChampImages():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    masteryScore = getMasteryStats("EUW1",SummonerInfo['id'])
    getChampImages(masteryScore)
    req = requests.get(masteryScore[1]['link'])
    assert int(req.status_code) == 200

def test_getRunesImages():
    Runes = cursor.execute("SELECT PrimaryKeyStone, COUNT(PrimaryKeyStone), PrimarySlot1 , COUNT(PrimarySlot1) ,PrimarySlot2 , COUNT(PrimarySlot2) ,PrimarySlot3 , COUNT(PrimarySlot3) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY PrimaryKeyStone ORDER BY PrimaryKeyStone DESC LIMIT 1 ",(1,))
    Runes = cursor.fetchall()
    runes = getRunesImagesList(Runes[0])
    req = requests.get(runes[1]['LinkRef'])
    assert int(req.status_code) == 200

def test_MasterySingle():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    masteryScore = getMasteryStats("EUW1",SummonerInfo['id'])
    Mastery = getSingleMasteryScore(1,masteryScore)
    assert Mastery < 500000

def test_AvgSummData():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    SummId = SummonerInfo['id']
    data = getMatchData("EUW1", SummId, SummonerInfo)
    avg = AvgStats(data)
    print(avg)
    assert avg['cs'] > 0
    assert avg['kills'] > 0
    assert avg['assists'] > 0
    assert avg['deaths'] > 0 
    assert avg['goldEarned'] > 0
    assert avg['physicalDamageDealtToChampions'] > 0 
    assert avg['physicalDamageTaken'] > 0
    assert avg['dragonKills'] > 0
    assert avg['baronKills'] > 0
    assert avg['GameDuration'] > 0
    assert avg['TowerDamageDealt'] > 0 

