import sys
import pytest
import requests

sys.path.append('..')
from config import *
from RiotApiCalls import *

api_key= api_key
db = pymysql.connect(host=host,user='o1gbu42_StatTracker',passwd=sql_password,database =sql_user)
cursor = db.cursor()

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
    data = getChampSpellImages(championStats)
    assert int(req.status_code) == 200
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

    runes = getRunesImages(Runes)
    req = requests.get(runes[1]['LinkRef'])
    assert int(req.status_code) ==200

test_getRunesImages()
test_ChampionDetails()
test_getChampAbilities()
test_getChampSpellImages()
test_getChampImages()