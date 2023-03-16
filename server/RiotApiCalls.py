import requests
from config import *
import pandas as pd
import time
import sys
sys.path.append('..')
from databaseQuries import *

API = api_key
MatchIDG = []
playerMatchData = []
participants = []
fullMatch = []
matchData = []

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

summonerSpells = {  # Summoner Spell Image Data Store
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
    print(itemList)
    connection = create_connection()
    cursor =  connection.cursor()
    itemE =[]
    for item in itemList:
        cursor.execute("""SELECT `ItemLink` FROM `ItemTbl` WHERE `ItemID` = '%s' """, (int(item),))
        data = cursor.fetchone()
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

#
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

def getSingleMasteryScore(champId, mastery):
    masteryScore = None
    for m in mastery:
        if int(champId) == int(m['championId']):
            masteryScore = int(m['championPoints'])

    if not masteryScore:
        masteryScore = 0
    

    return masteryScore


def getMatchData(region,id,SummonerInfo):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=5&api_key=" + API)
    MatchIDs = MatchIDs.json()
    data = getMatches("europe", MatchIDs, SummonerInfo)
    return data

def getMatchIds(region,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=5&api_key=" + API)
    MatchIDs = MatchIDs.json()
    return MatchIDs

def getMatches(region,MatchIDs,SummonerInfo):
    puuid = SummonerInfo['puuid']
    SummId = SummonerInfo['id']
    RankedDetails = getRankedStats(region,SummId)
   
    try:
        SOLO = RankedDetails[0]
        FLEX = RankedDetails[1]
    except:
        FLEX = {"queueType":"RANKED_SOLO_5x5","tier":"unranked","rank":"","summonerName":"","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}
        SOLO = {"queueType":"RANKED_SOLO_5x5","tier":"unranked","rank":"","summonerName":"","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}


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
                'ItemImages':None,
                "TowerDamageDealt":None,
                "Role":None,
                "PrimaryKeyStone":None,
                "SecondaryKeyStone":None,
                "EnemyChamp":None,
                "SummonerSpell1":None,
                "SummonerSpell2":None,
                "teamRiftHeraldKills":None
        }

        matchIdsData = {
            'MatchIDS':[],
            'GameType':[],
            'Rank':[],
            'gameVersion':[]
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

        summSpell1 = player_data['summoner1Id']
        summSpell2 = player_data['summoner2Id']

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
            else:
                enemyChampion = FullMatchData['info']['participants'][2]['championName']
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

        
        ItemInGame = GetItemImages(Items)
        player_data = getRoleImages(player_data)
        gameMins = MatchData['info']['gameDuration']
       
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        win = player_data['win']
        GoldPerMin = player_data['goldEarned']
        physicalDamageDealtToChampions = player_data['totalDamageDealtToChampions']
        physicalDamageTaken = player_data['totalDamageTaken']
        cs = player_data['totalMinionsKilled']
        dragonKills = player_data['dragonKills']
        baronKills = player_data['baronKills']
        role = player_data['lane']
        turretDmg = player_data['turretTakedowns']
        jungleCampsKilled = player_data['challenges']['enemyJungleMonsterKills'] + player_data['challenges']['alliedJungleMonsterKills']
        riftHeraldKills = player_data['challenges']['teamRiftHeraldKills']

        data['teamRiftHeraldKills'] = riftHeraldKills
        data['ItemImages'] = ItemInGame
        data['champion'] = champion
        data['kills'] = k
        data['deaths'] = d
        data['assists'] = a
        data['win'] = win  
        data['goldEarned'] = GoldPerMin
        data['physicalDamageDealtToChampions'] = physicalDamageDealtToChampions
        data['physicalDamageTaken'] = physicalDamageTaken
        data['cs'] = cs + jungleCampsKilled
        data['dragonKills'] = dragonKills
        data['baronKills'] = baronKills
        data['GameDuration'] = gameMins
        data['Role'] = role
        data['Items'] = Items
        data['PrimaryKeyStone'] = KeyStone1
        data['SecondaryKeyStone'] = KeyStone2
        data['TowerDamageDealt'] = turretDmg
        data['EnemyChamp'] = enemyChampion
        data['SummonerSpell1'] = summSpell1
        data['SummonerSpell2'] = summSpell2


        gameType = MatchData['info']['gameMode']
        gameVersion = MatchData['info']['gameVersion']
        matchIdsData['MatchIDS'].append(matchID)
        matchIdsData['GameType'].append(gameType)
        matchIdsData['gameVersion'].append(gameVersion)
        matchIdsData['Rank'].append(SOLO['tier'])

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


#Gets AvgStats for Previous x Games
def AvgStats(dataList):
    #Data Store - Dict
    AvgStats = {
        'cs':0,
        'kills':0,
        'assists':0,
        'deaths':0,
        'goldEarned':0,
        'physicalDamageDealtToChampions':0,
        'physicalDamageTaken':0,
        'dragonKills':0,
        'baronKills':0,
        'GameDuration':0,
        'TowerDamageDealt':0
    }
    i = 1 #Iterator
    while i < len(dataList): # Less than x games
        AvgStats['cs'] = AvgStats['cs'] + dataList[i]['cs']
  
        AvgStats['kills'] += dataList[i]['kills']
        AvgStats['assists'] += dataList[i]['assists']
        AvgStats['deaths'] += dataList[i]['deaths']
        AvgStats['goldEarned'] += dataList[i]['goldEarned']
        print(AvgStats['physicalDamageDealtToChampions'])
        AvgStats['physicalDamageDealtToChampions'] += dataList[i]['physicalDamageDealtToChampions'] 
        AvgStats['physicalDamageTaken'] += dataList[i]['physicalDamageTaken']
        AvgStats['dragonKills'] += dataList[i]['dragonKills']
        AvgStats['baronKills'] += dataList[i]['baronKills'] 
        AvgStats['GameDuration'] += dataList[i]['GameDuration'] 
        AvgStats['TowerDamageDealt'] += dataList[i]['TowerDamageDealt'] 
        i = i +1
    for keys in AvgStats: #Divide by number of games
        AvgStats[keys] = AvgStats[keys] / i
        AvgStats[keys] = (AvgStats[keys])
    return AvgStats # Returns Avg Dataset for ml Model predictions

def avgStatsTeam(dataList):
    AvgStats = {
        'kills':0,
        'baronKills':0,
        'riftHeraldKills':0,
        'dragonKills':0,
        'turretKills':0
    }
    i = 0
    while i < len(dataList): # Less than x games
        AvgStats['kills'] += dataList[i]['kills']
        AvgStats['baronKills'] += dataList[i]['baronKills']
        AvgStats['riftHeraldKills'] += dataList[i]['teamRiftHeraldKills']
        AvgStats['dragonKills'] += dataList[i]['dragonKills']
        AvgStats['turretKills'] += dataList[i]['TowerDamageDealt']
        i = i + 1

    for keys in AvgStats: #Divide by number of games
        AvgStats[keys] = AvgStats[keys] / i
        AvgStats[keys] = (AvgStats[keys])
        
    return AvgStats # Returns Avg Dataset for ml Model predictions

#calculate avgTeam Statistics over x games
def calculateAvgTeamStats(Team,Region):
    list = []
    for item in Team:
        summName = item
        SummonerInfo = getSummonerDetails("EUW1",summName)
        SummId = SummonerInfo['id']
        data = getMatchData(Region, SummId, SummonerInfo)
        avg = avgStatsTeam(data) 
        list.append(avg)

    TeamData = {
        'kills':0,
        'baronKills':0,
        'riftHeraldKills':0,
        'dragonKills':0,
        'turretKills':0
    }
    for item in list:
        TeamData['kills'] += item['kills']
        TeamData['baronKills'] += item['baronKills']
        TeamData['riftHeraldKills'] += item['riftHeraldKills']
        TeamData['dragonKills'] += item['dragonKills']
        TeamData['turretKills'] += item['turretKills']

    print(TeamData)
    return TeamData

def makeDataSet(team1,team2,data):
    dataset = {
        "B1": data['B1'],
        "B2":  data['B2'],
        "B3": data['B3'],
        "B4":  data['B4'],
        "B5":  data['B5'],
        "R1":  data['R1'],
        "R2":  data['R2'],
        "R3":  data['R3'],
        "R4": data['R4'],
        "R5":  data['R5'],
        "BlueBaronKills": team1['baronKills'],
        "BlueRiftHeraldKills": team1['riftHeraldKills'],
        "BlueDragonKills": team1['dragonKills'],
        "BlueTowerKills": team1['turretKills'],
        "BlueKills": team1['kills'],

        "RedBaronKills": team2['baronKills'],
        "RedRiftHeraldKills": team2['riftHeraldKills'],
        "RedDragonKills": team2['dragonKills'],
        "RedTowerKills": team2['turretKills'],
        "RedKills": team2['kills'],
    }

    return dataset

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

#Initilizes an array of games - containing all participants that were present in each game 
#List Object Participants
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

#Returns the Participants list object
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

    while i < 0:
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
    
#Checks if user is in game
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
  
    if str(role) == "carry":
        role == "bottom"
    if str(role) == "support":
        role = "utility"
    if str(role) == "solo":
        role = "middle"

    data['role'] = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-"+ role +".png"
    return data

def getRoles():
    list = [["0","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-top.png"],
        ["1","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png"],
        ["2","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-middle.png"],
        ["3","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-bottom.png"],
        ["4","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-utility.png"]]
    RoleList = []

    i = 0
    while i < 5:
        roleImages = {
            "RoleId":int(list[i][0]),
            'RoleLink':list[i][1]
        }
        RoleList.append(roleImages)
        i = i +1
    
    return RoleList
