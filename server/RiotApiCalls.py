import requests
from config import *
import pandas as pd
import time

from championsRequest import *

API = api_key
MatchIDG = []
playerMatchData = []
participants = []
fullMatch = []
matchData = []

db = pymysql.connect(host=host,user='o1gbu42_StatTracker',passwd=sql_password,database =sql_user)
cursor = db.cursor()

class SummonerInGameObj:
  def __init__(self, SummonerName, Rank, WinRate, AvgGold, AvgDmg, AvgDmgTaken, ProfileIcon):
    self.SummonerName = SummonerName
    self.Rank = Rank
    self.WinRate = WinRate
    self.AvgGold = AvgGold
    self.AvgDmg = AvgDmg
    self.AvgDmgTaken = AvgDmgTaken
    self.profileIcon = ProfileIcon

Summoners = []

summonerSpells = {
    21: 'summonerbarrier.png',
    1: 'summoner_boost.png',
    14: 'summonerignite.png',
    3: 'summoner_exhaust.png',
    4: 'summoner_flash.png',
    6: 'summoner_haste.png',
    7: 'summoner_heal.png',
    13: 'summonermana.png',
    11: 'summoner_smite.png',
    32: 'summoner_mark.png',
    12: 'summoner_teleport.png',
    55: 'summoner_smite.png'
}

#Get Item Images - Pass in itemList []
def GetItemImages(itemList):
    itemE =[]
    for item in itemList:
        print(item)
        cursor.execute("SELECT `ItemLink` FROM `ItemTbl` WHERE `ItemID` = % s", (item,))
        data = str(cursor.fetchall())
        data = data.replace(')', '')
        data = data.replace('(', '')
        data = data.replace(',', '')
        data = data.replace("'", '')
        print(data)

        itemE.append(data)

    ItemList = itemE
    return ItemList

#https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/
#Gets Summoner Spell Icons and Replaces them in the match data store
def getSummonerSpellsImages(match):
        spellId1 = match['summoner1Id']
        spellId2 = match['summoner2Id']

        spellId1 = summonerSpells[spellId1]
        spellId2 = summonerSpells[spellId2]
        match['summoner1Id'] = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/' + spellId1
        match['summoner2Id'] = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/' + spellId2
        return match


#Gets RankTierIcon     
def RankedImages(RankedMode):
    RankedMode['ImageUrl'] = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/" + RankedMode['tier'].lower() + ".png"

#Calculates Win Rate for the RankedStats []
def CalcWinRate(RankedMode):
    GamesPlayed = RankedMode['losses'] + RankedMode['wins']
    WinRate = RankedMode['wins'] / GamesPlayed
    RankedMode['WinRate'] = WinRate * 100

#Gets Profile Image
def getImageLink(SummonerInfo):
    profileIcon = str(SummonerInfo['profileIconId'])
    SummonerInfo['profileIconId'] = 'http://ddragon.leagueoflegends.com/cdn/12.6.1/img/profileicon/' + profileIcon +'.png'
   
def getSummonerDetails(Region,summonerName):
    SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    SummonerInfo = SummonerInfo.json()
    return SummonerInfo

def getRankedStats(Region,id):
    RankedMatches = requests.get("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key="+API)
    Ranked = RankedMatches.json()
    return Ranked

def getMasteryStats(Region,id):
    masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
    masteryScore = masteryScore.json()
    print("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
    getChampImages(masteryScore)
    return masteryScore

def getSingleMasteryScore(champId,summonerName,Region):
    Summoner = getSummonerDetails(Region, summonerName)
    Mastery = getMasteryStats(Region,Summoner['id'])
    
    for m in Mastery:
        if champId == int(m['championId']):
            masteryScore = int(m['championPoints'])
            break

    return masteryScore

def getMatchData(region,id,SummonerInfo):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=15&api_key=" + API)
    MatchIDs = MatchIDs.json()
    data = getMatches("europe", MatchIDs, SummonerInfo)
    return data

def getMatchIds(region,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=15&api_key=" + API)
    MatchIDs = MatchIDs.json()
    return MatchIDs

def getMatches(region,MatchIDs,SummonerInfo):
    puuid = SummonerInfo['puuid']
    SummId = SummonerInfo['id']
    RankedDetails = getRankedStats(region,SummId)
    print(RankedDetails)
    try:
        SOLO = RankedDetails[0]
    except:
        FLEX = {"queueType":"RANKED_SOLO_5x5","tier":"unranked","rank":"","summonerName":"Frycks","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}
        SOLO = {"queueType":"RANKED_SOLO_5x5","tier":"unranked","rank":"","summonerName":"Frycks","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}

    matchIdsData = {
        'MatchIDS':[],
        'GameType':[],
        'Rank':[]
    }

    temp = []
    tempMatchIds = []
    playerMatchDataTemp = []

    for matchID in MatchIDs:
        data = {
                'GameDuration':None, 
                'champion': None,
                'kills':None ,
                'deaths': None,
                'assists': None,
                'win': None,
                'goldEarned':None,
                'physicalDamageDealtToChampions':None,
                'physicalDamageTaken':None,
                'cs':None,
                'dragonKills':None,
                'baronKills':None,
                'Items':None,
                "TowerDamageDealt":None,
                "Role":None,
                "PrimaryKeyStone":None,
                "SecondaryKeyStone":None,
                "EnemyChamp":None
        }

        matchIdsData = {
            'MatchIDS':[],
            'GameType':[],
            'Rank':[]
        }

        MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
        print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
        MatchData = MatchData.json()
        FullMatchData = MatchData
        #http://ddragon.leagueoflegends.com/cdn/12.16.1/data/en_US/runesReforged.json
        getGameParticipants(MatchData)
        participants = MatchData['metadata']['participants']
        player_index = participants.index(puuid)
        
 
        player_data = MatchData['info']['participants'][player_index]

        player_data = getSummonerSpellsImages(player_data)
  
        role = player_data['lane']
        champion = player_data['championName']
        i = 0
        while i <= 9:
            enemyLane = FullMatchData['info']['participants'][i]['lane']
            enemyChampTemp = FullMatchData['info']['participants'][i]['championName']
            if (role == enemyLane and enemyChampTemp != champion):
                enemyChampion = FullMatchData['info']['participants'][i]['championName']
                break
            i = i + 1

        playerMatchDataTemp.append(player_data)
  
        Items = [
            player_data['item0'],
            player_data['item1'],
            player_data['item2'],
            player_data['item3'],
            player_data['item4'],
            player_data['item5'],
            player_data['item6'],
        ]
     
        print(player_data["perks"]['styles'][0]['selections'][0]['perk'])
        KeyStone1=[
            player_data["perks"]['styles'][0]['selections'][0]['perk'],
            player_data["perks"]['styles'][0]['selections'][1]['perk'],
            player_data["perks"]['styles'][0]['selections'][2]['perk'],
            player_data["perks"]['styles'][0]['selections'][3]['perk']
        ]
        
        KeyStone2= [
            player_data["perks"]['styles'][1]['selections'][0]['perk'],
            player_data["perks"]['styles'][1]['selections'][1]['perk'],

        ]
        #ItemInGame = GetItemImages(Items)
        #player_data = getRoleImages(player_data)
        gameMins = MatchData['info']['gameDuration']
       
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        win = player_data['win']
        GoldPerMin = player_data['goldEarned']
        physicalDamageDealtToChampions = player_data['physicalDamageDealtToChampions']
        physicalDamageTaken = player_data['physicalDamageTaken']
        cs = player_data['totalMinionsKilled']
        dragonKills = player_data['dragonKills']
        baronKills = player_data['baronKills']
        role = player_data['lane']
        turretDmg = player_data['turretTakedowns']

        data['champion'] = champion
        data['kills'] = k
        data['deaths'] = d
        data['assists'] = a
        data['win'] = win  
        data['goldEarned'] = GoldPerMin
        data['physicalDamageDealtToChampions'] = physicalDamageDealtToChampions
        data['physicalDamageTaken'] = physicalDamageTaken
        data['cs'] = cs
        data['dragonKills'] = dragonKills
        data['baronKills'] = baronKills
        data['GameDuration'] = gameMins
        data['Role'] = role
        data['Items'] = Items
        data['PrimaryKeyStone'] = KeyStone1
        data['SecondaryKeyStone'] = KeyStone2
        data['TowerDamageDealt'] = turretDmg
        data['EnemyChamp'] = enemyChampion
        gameType = MatchData['info']['gameMode']
        matchIdsData['MatchIDS'].append(matchID)
        matchIdsData['GameType'].append(gameType)
        matchIdsData['Rank'].append(SOLO['tier'])
        print(SOLO['tier'])

        data2 = dict(data)
        matchIds2 = dict(matchIdsData)
        del data
        del matchIdsData
        temp.append(data2)
        tempMatchIds.append(matchIds2)

    tempPlayerMatch = playerMatchDataTemp[:]
    tempMatchIds1 = tempMatchIds

    setPlayerMatchData(tempPlayerMatch)
    setsMatchData(tempMatchIds1)

    dataList = list(temp)
    matchIDS = list(tempMatchIds)

    del temp
    del tempMatchIds 
    return dataList

#Sets Player Match Data
def setPlayerMatchData(match):
    global fullMatch
    fullMatch = match

#Returns Player Match Data
def getPlayerMatchData():
    global fullMatch
    return fullMatch

#Sets Match Data
def setsMatchData(match):
    global matchData
    matchData = match

#Returns Match Data
def getsMatchData():
    global matchData
    return matchData

def getGameParticipants(game):
    x=0
    participantsTemp = {
        'name': [],
        'champion':[]
    }
    while x < 10:
        summonerTemp = game['info']['participants'][x]['summonerName']
        championTemp = game['info']['participants'][x]['championName']

        participantsTemp['name'].append(summonerTemp)
        participantsTemp['champion'].append(championTemp)
        x = x + 1

    participants.append(participantsTemp)

def getGameParticipantsList():
    return participants


def getMatchTimeline(region,id,puuid,data):
    MatchIDs = getMatchIds(region,puuid)
    MeanData = {
            'avgGoldPerMin': [],
            'creepScore': [],
            'totalDamageDonePerMin': [],
            'totalDamageTakenPerMin': []
    }

    ListS = []
    ie = 0
    for matchID in MatchIDs:
            data2 = {
                    'currentGold': [],
                    'minionsKilled': [],
                    'totalDamageDoneToChampions': [],
                    'totalDamageTaken': []
            }

            tempParticipants = []
            MeanData = {
                    'avgGoldPerMin': [],
                    'creepScore': [],
                    'totalDamageDonePerMin': [],
                    'totalDamageTakenPerMin': []
            }
            MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/" + matchID + "/timeline?api_key=" + api_key)
     
            MatchData = MatchData.json()
      

            participants = MatchData['metadata']['participants']
            # Now, find where in the data our players puuid is found
            player_index = participants.index(puuid)
            player_index = str(player_index + 1)

   
            i = 0
            print(data[ie]['GameDuration'])
            matchLength = data[ie]['GameDuration']
            matchLength = int(matchLength)
 
            matchL = matchLength / 60
            ie =  ie + 1 
            while i < matchL:
                    player_data = MatchData['info']['frames'][i]['participantFrames'][player_index]
                    currentGold = player_data['totalGold']
                    minionsKilled = player_data['minionsKilled']
                    
                    totalDamageDoneToChampions = player_data['damageStats']['totalDamageDoneToChampions']
                    totalDamageTaken = player_data['damageStats']['totalDamageTaken']
                    
                    data2['currentGold'].append(currentGold)
                    data2['minionsKilled'].append(minionsKilled)
                    data2['totalDamageDoneToChampions'].append(totalDamageDoneToChampions)
                    data2['totalDamageTaken'].append(totalDamageTaken)
                    i= i + 1   
            ListS.append(data2)



    i = 0
    count = 0

    while i < 11:
            for line in ListS:
                dmgTaken = line['totalDamageTaken'][i]
                minions = line['minionsKilled'][i]
                dmgDelt = line['totalDamageDoneToChampions'][i]
                gold = line['currentGold'][i]
                meanDmgTaken =+ dmgTaken
                meanMinions =+ minions
                meanDmgDealt =+ dmgDelt
                meanGold =+ gold
                count=count +1
            
       
            count=0
            MeanData['totalDamageTakenPerMin'].append(meanDmgTaken)
            MeanData['avgGoldPerMin'].append(meanGold)
            MeanData['creepScore'].append(meanMinions)
            MeanData['totalDamageDonePerMin'].append(meanDmgDealt)
            i = i + 1
                
    return MeanData

def SummonerInGame(LiveGame,region):
    LiveGame = LiveGame['participants']
    i = 0
    summonerIds = []
    while i < 10:
        summonerIds.append(LiveGame[i]['summonerId'])
        i = i + 1

    for summonerId in summonerIds:
        puuid = requests.get("https://"+ region + ".api.riotgames.com/lol/summoner/v4/summoners/" +summonerId + "?api_key=" + api_key)
        puuid = puuid.json()
        name = puuid['name']
        puuid = puuid['puuid']
        Rank = "Unranked"
        MatchIDs = getMatchIds(region,puuid)
        SummonerDetails = getSummonerDetails(region, name)
        Image = getImageLink(SummonerDetails)
        img = str(SummonerDetails['profileIconId'])
        ##GetMatch
        Last5Games = getMatches(region, MatchIDs, puuid)
        MeanData = getMatchTimeline(region, summonerId, puuid, Last5Games)

        champion = []
        WinRate = 0
        for rows in Last5Games:
            if rows['win'] == True:
                WinRate = WinRate + 1
        

        WinRate = WinRate / 5
  

        avgGoldPerMin = MeanData['avgGoldPerMin'].pop()
        totalDamageTakenPerMin = MeanData['totalDamageTakenPerMin'].pop()
        totalDamageTakenPerMin = MeanData['totalDamageTakenPerMin'].pop()
        summ = SummonerInGameObj(name,Rank, WinRate, avgGoldPerMin,totalDamageTakenPerMin,totalDamageTakenPerMin,img)
        Summoners.append(summ)
        time.sleep(30)
    return Summoners
    
def summonerInGameCheck(region,summonerId):
    LiveGame = requests.get("https://"+ region + ".api.riotgames.com/lol/spectator/v4/active-games/by-summoner/" + summonerId + "?api_key=" + api_key)
    LiveGame = LiveGame.json()
    if LiveGame == 404:
        return 404
    else:
        Summoners = SummonerInGame(LiveGame,region)
        return Summoners

def getRoleImages(data):
    role = data['role'].lower()
    if role == "support":
        role = "utility"
    if role == "solo":
        role = "middle"
    data['role'] = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-"+ role +".png"
    return data