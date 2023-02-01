import requests
from config import *
import pandas as pd
import time
import pymysql


API = api_key
MatchIDG = []
playerMatchData = []
participants = []
fullMatch = []

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
def getSummonerSpellsImages(match):
        spellId1 = match['summoner1Id']
        spellId2 = match['summoner2Id']

        spellId1 = summonerSpells[spellId1]
        spellId2 = summonerSpells[spellId2]
        match['summoner1Id'] = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/' + spellId1
        match['summoner2Id'] = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/' + spellId2
        return match

#Gets ChampionImage URLS into masteryScore JSON file
def getChampImages(masteryScore):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data']
    for item in DDRAGON:
        temp = DDRAGON.get(item)
        for mastery in masteryScore:
            if int(temp['key']) == int(mastery['championId']):
                mastery['name'] = temp['id']
                mastery['link'] = "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/" + temp['id'] +".png"

#Gets RankTierIcon     
def RankedImages(RankedMode):
    RankedMode['ImageUrl'] = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/" + RankedMode['tier'].lower() + ".png"

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
    getChampImages(masteryScore)
    return masteryScore

def getMatchData(region,id,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=10&api_key=" + API)
    MatchIDs = MatchIDs.json()
    data = getMatches("europe", MatchIDs, puuid)
    return data

def getMatchIds(region,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=10&api_key=" + API)
    MatchIDs = MatchIDs.json()
    return MatchIDs

def getMatches(region,MatchIDs,puuid):
    temp = []
    playerMatchDataTemp = []
    for matchID in MatchIDs:
        data = {
                'GameDuration':[], 
                'champion': [],
                'kills':[] ,
                'deaths': [],
                'assists': [],
                'win': [],
                'goldEarned':[],
                'physicalDamageDealtToChampions':[],
                'physicalDamageTaken':[],
                'cs':[],
                'dragonKills':[],
                'baronKills':[],
                'Items':[]
        }
        MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
        print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
        MatchData = MatchData.json()
        #http://ddragon.leagueoflegends.com/cdn/12.16.1/data/en_US/runesReforged.json
        getGameParticipants(MatchData)
        participants = MatchData['metadata']['participants']
        player_index = participants.index(puuid)
        
 
        player_data = MatchData['info']['participants'][player_index]

        player_data = getSummonerSpellsImages(player_data)
        player_data = getRoleImages(player_data)
     
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

        ItemInGame = GetItemImages(Items)
   
        gameMins = MatchData['info']['gameDuration']
        champion = player_data['championName']
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

        data['champion'].append(champion)
        data['kills'].append(k)
        data['deaths'].append(d)
        data['assists'].append(a)
        data['win'].append(win)    
        data['goldEarned'].append(GoldPerMin)
        data['physicalDamageDealtToChampions'].append(physicalDamageDealtToChampions)
        data['physicalDamageTaken'].append(physicalDamageTaken)
        data['cs'].append(cs)
        data['dragonKills'].append(dragonKills)    
        data['baronKills'].append(baronKills)
        data['GameDuration'].append(gameMins)

        data['Items'] = ItemInGame
        data2 = dict(data)
        del data
        temp.append(data2)
    

   
    array2 = playerMatchDataTemp[:]
    setPlayerMatchData(array2)
    dataList = list(temp)
    del temp
    return dataList

#Sets Player Match Data
def setPlayerMatchData(match):
    global fullMatch
    fullMatch = match

#Returns Player Match Data
def getPlayerMatchData():
    global fullMatch
    return fullMatch

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
            matchLength = data[ie]['GameDuration'][0]
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