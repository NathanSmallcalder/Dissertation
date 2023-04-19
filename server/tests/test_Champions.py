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

#### Champ Images -- Summoner Page - Mastery Section
def test_getChampImages():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    masteryScore = getMasteryStats("EUW1",SummonerInfo['id'])
    getChampImages(masteryScore)
    req = requests.get(masteryScore[1]['link'])
    assert int(req.status_code) == 200

# Gets Rune Images
# Should be status code 200
def test_getRunesImages():
    Runes = commonRunes(1)
    req = requests.get(Runes[1]['LinkRef'])
    assert int(req.status_code) == 200

### Gets a Single Mastery Score for a summoner
### Should not be none
def test_MasterySingle():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    masteryScore = getMasteryStats("EUW1",SummonerInfo['id'])
    Mastery = getSingleMasteryScore(1,masteryScore)
    assert Mastery != None

def test_getSummoner():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    assert 'id' in SummonerInfo.keys()
    assert 'accountId' in SummonerInfo.keys()
    assert 'puuid' in SummonerInfo.keys()
    assert 'profileIconId' in SummonerInfo.keys()

def test_getImageLink():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    getImageLink(SummonerInfo)
    req = requests.get(SummonerInfo['profileIconId'])
    assert req.status_code == 200

### Gets Avg Summoner Statistics.
def test_AvgSummData():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    SummId = SummonerInfo['id']
    RankedDetails = getRankedStats("EUW1",SummId)
    data = getMatchData("EUW1", SummId, SummonerInfo,RankedDetails)
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

###Get Match History
def test_getMatchData():
    SummonerInfo = getSummonerDetails("EUW1","Mealsz")
    SummId = SummonerInfo['id']
    RankedDetails = getRankedStats("EUW1",SummId)
    data = getMatchData("EUW1", SummId, SummonerInfo,RankedDetails)
    assert 'kills' in data[0].keys()
    assert 'assists' in data[0].keys()
    assert 'win' in data[0].keys()
    assert 'deaths' in data[0].keys()


### Test Rank Images
### Response 200
def test_RankedImages():
    rank = {
        'tier':"gold",
    }
    print(rank['tier'])
    RankedImages(rank)
    req = requests.get(rank['ImageUrl'])
    assert req.status_code == 200

## Calculate Win Rate
## Should be 66.66.....%
def test_CalcWinRate():
    rank = {
        'losses':5,
        'wins':10
    }
    CalcWinRate(rank)
    assert rank['WinRate'] > 65

## Calculates Avg Team Statistics
## Value always changes
## Should return an dictionary
def test_calculateAvgTeamStats():
    team = ["Lil Nachty", "Mealsz", "ItWoZnotmee","Ehhhh","Ehhhh"]
    team = calculateAvgTeamStats(team, "EUW1")
    assert len(team) > 5

###Gets Role Images
### Status Code == 200
def test_getRoleImages():
    role = {
        'role':"utility"
    }
    role = getRoleImages(role)
    print(role)
    req = requests.get(role['role'])
    assert req.status_code == 200

### Gets a Array of Role Image Links
### Static
def test_getRoles():
    roles = getRoles()
    assert roles[0]['RoleLink'] == "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-top.png"
    assert roles[1]['RoleLink'] == "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png"
    assert roles[2]['RoleLink'] == "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-middle.png"
    assert roles[3]['RoleLink'] == "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-bottom.png"
    assert roles[4]['RoleLink'] == "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-utility.png"
    