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

#Gets Basic Summoner Details
def getSummonerDetails(Region,summonerName):
    SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    SummonerInfo = SummonerInfo.json()
    return SummonerInfo

#Gets Summoner Ranked Stats
def getRankedStats(Region,id):
    RankedMatches = requests.get("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key="+API)
    Ranked = RankedMatches.json()
    return Ranked

#Gets Mastery Stats
def getMasteryStats(Region,id):
    masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
    masteryScore = masteryScore.json()
    getChampImages(masteryScore)
    return masteryScore

### Gets a single mastery score value
### pass in the desired champion id and mastery score array from getMasteryStats
def getSingleMasteryScore(champId, mastery):
    masteryScore = None
    for m in mastery:
        champMastery = m['championId']
        if int(champId) == int(champMastery):
            masteryScore = int(champMastery)

    if not masteryScore:
        masteryScore = 0

    return masteryScore

### Gets MatchIds
### calls getMatches
### Returns data from getMatches
def getMatchData(region,id,SummonerInfo,RankedDetails):
    mastery = getMasteryStats(region, SummonerInfo['id'])
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=10&api_key=" + API)
    MatchIDs = MatchIDs.json()
    data = getMatches("europe", MatchIDs, SummonerInfo,RankedDetails,mastery)
    return data

### Gets 5 MatchIds
def getMatchData5Matches(region,id,SummonerInfo,RankedDetails):
    mastery = getMasteryStats(region, SummonerInfo['id'])
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=5&api_key=" + API)
    MatchIDs = MatchIDs.json()
    data = getMatches("europe", MatchIDs, SummonerInfo,RankedDetails,mastery)
    return data

### Gets x MatchIds
def getMatchIds(region,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=10&api_key=" + API)
    MatchIDs = MatchIDs.json()
    return MatchIDs

# Gets Summoner match data
def getMatches(region,MatchIDs,SummonerInfo,RankedDetails,mastery):
    puuid = SummonerInfo['puuid']
    SummId = SummonerInfo['id']
    summonerName = SummonerInfo['name']

    #if user doesnt exist insert into database
    try:
        SummonerFk = getSummonerIdFromDatabase(summonerName)
    except:
        SummonerFk = None
    
    if SummonerFk != None:
        pass
    else:
        try:
            SummonerFk = insertUser(summonerName)
        except:
            pass
    
    temp = []
    tempMatchIds = []
    playerMatchDataTemp = []

    for matchID in MatchIDs:
        data = { # Temp Data Store
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

        matchIdsData = { # Temp Data store - Match Values
            'MatchIDS':[],
            'GameType':[],
            'Rank':[],
            'gameVersion':[]
        }

        MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
   
        MatchData = MatchData.json()
        FullMatchData = MatchData
        #http://ddragon.leagueoflegends.com/cdn/12.16.1/data/en_US/runesReforged.json
        getGameParticipants(MatchData)
        patch = MatchData['info']['gameVersion']
        GameType = MatchData['info']['gameMode']
        participants = MatchData['metadata']['participants']
        player_index = participants.index(puuid)
        player_data = MatchData['info']['participants'][player_index]
        gameMins = MatchData['info']['gameDuration']
        summSpell1 = player_data['summoner1Id']
        summSpell2 = player_data['summoner2Id']

        player_data = getSummonerSpellsImages(player_data)
        
        role = player_data['lane']
        champion = player_data['championName']
        
        RankId = getRankId(RankedDetails[0]['tier'])
  

        #Find opposing laner
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
        matchIdsData['Rank'].append(RankedDetails[0]['tier'])

        champId = getChampId(champion)
        enemyChampion = getChampId(enemyChampion)
        MatchVerify = matchCheck(matchID)
 

        masteryScore = getSingleMasteryScore(champId,mastery)
        if MatchVerify == None:
            insertMatch(matchID,patch,GameType,RankId,gameMins)
        else:
            pass
        print("ITEMS", Items[0] , " ", Items[1] , " ", Items[2] , " ", Items[3] , " ", Items[4] , " ", Items[5], " ", Items[6])
        SummMatchId = checkSummMatch(SummonerFk,matchID)
        if SummMatchId == None:
            try:
                SummMatch = insertSummMatch(SummonerFk,matchID,champId)
                insertMatchStats(SummMatch,cs,physicalDamageDealtToChampions,physicalDamageTaken,turretDmg,
                GoldPerMin,role,win,Items[0],Items[1],Items[2],Items[3],Items[4],Items[5],k,d,a,KeyStone1[0],KeyStone1[1],KeyStone1[2],KeyStone1[3],
                KeyStone2[0],KeyStone2[1],summSpell1,summSpell2,masteryScore,enemyChampion,dragonKills,baronKills)
            except:
                pass
        else:
            pass
       
    #### stores temp data arrays into a list
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
    #### 
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
        'turretKills':0,
        'deaths': 0,
        'assists': 0,
        'cs':0,
        'goldEarned':0
    }
    i = 0
    while i < len(dataList): # Less than x games
        AvgStats['kills'] += dataList[i]['kills']
        AvgStats['baronKills'] += dataList[i]['baronKills']
        AvgStats['riftHeraldKills'] += dataList[i]['teamRiftHeraldKills']
        AvgStats['dragonKills'] += dataList[i]['dragonKills']
        AvgStats['turretKills'] += dataList[i]['TowerDamageDealt']
        AvgStats['deaths'] += dataList[i]['deaths']
        AvgStats['assists'] += dataList[i]['assists']
        AvgStats['cs'] += dataList[i]['cs']
        AvgStats['goldEarned'] += dataList[i]['goldEarned']
        i = i + 1

    for keys in AvgStats: #Divide by number of games
        AvgStats[keys] = AvgStats[keys] / i
        AvgStats[keys] = (AvgStats[keys])
        
    return AvgStats # Returns Avg Dataset for ml Model predictions

#calculate avgTeam Statistics over x games
def calculateAvgTeamStats(Team,Region):
    list = []
    ###Tempory Rank Store (Run out of requests)
    RankedDetails = [{"queueType":"RANKED_SOLO_5x5","tier":"unranked","rank":"II","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}]
    for item in Team:
        summName = item
        SummonerInfo = getSummonerDetails("EUW1",summName)
        SummId = SummonerInfo['id']
        data = getMatchData5Matches(Region, SummId, SummonerInfo, RankedDetails)
        avg = avgStatsTeam(data) 
        list.append(avg)

    TeamData = {
        'kills':0,
        'baronKills':0,
        'riftHeraldKills':0,
        'dragonKills':0,
        'turretKills':0,
        'deaths': 0,
        'assists': 0,
        'cs':0,
        'goldEarned':0
    }
    for item in list:
        TeamData['kills'] += item['kills']
        TeamData['baronKills'] += item['baronKills']
        TeamData['riftHeraldKills'] += item['riftHeraldKills']
        TeamData['dragonKills'] += item['dragonKills']
        TeamData['turretKills'] += item['turretKills']
        TeamData['deaths'] += item['deaths']
        TeamData['assists'] += item['assists']
        TeamData['cs'] += item['cs']
        TeamData['goldEarned'] += item['goldEarned']
        
    return TeamData
    

def calculateAvgLiveTeamStats(Team,Region):
    list = []
    RankedDetails = [{"queueType":"RANKED_SOLO_5x5","tier":"GOLD","rank":"II","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}]
    i = 0
    print(Team)
    while i < 5:
        summName = Team[i]['Name']
        SummonerInfo = getSummonerDetails("EUW1",summName)
        SummId = SummonerInfo['id']
        data = getMatchData5Matches(Region, SummId, SummonerInfo, RankedDetails)
        avg = avgStatsTeam(data) 
        list.append(avg)
        Team[i]['kills'] = avg['kills']
        Team[i]['baronKills'] = avg['baronKills']
        Team[i]['riftHeraldKills'] = avg['riftHeraldKills']
        Team[i]['dragonKills'] = avg['dragonKills']
        Team[i]['turretKills'] = avg['turretKills']
        Team[i]['deaths'] = avg['deaths']
        Team[i]['assists'] = avg['assists']
        Team[i]['cs'] = avg['cs']
        Team[i]['goldEarned'] = avg['goldEarned']
        i = i + 1


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

    return TeamData
    
### Creates the dataset of to be returned to the /teamData endpoint
### Dictionary object
### Before being ran through the machine learning algorithm
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

### Gets the timeline of the Match
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

### Gets all statistics for every summoner in a given users game
def SummonerInGame(LiveGame,region):
    LiveGame = LiveGame['participants']
    i = 0
    summonerIds = []

    while i < 10:
        Summoner = {
            'Name': None,
            'Champion':None,
            'profileIconId':None,
        }
        Summoner['Name'] = LiveGame[i]['summonerName']
        Summoner['Champion'] = LiveGame[i]['championId']
        Summoner['profileIconId'] = LiveGame[i]['profileIconId']
        temp = Summoner
        del Summoner

        summonerIds.append(temp)
        i = i + 1
    print(summonerIds)
    return summonerIds
    
#Checks if user is .,
def summonerInGameCheck(region,summonerId):
    LiveGame = requests.get("https://"+ region + ".api.riotgames.com/lol/spectator/v4/active-games/by-summoner/" + summonerId + "?api_key=" + api_key)
    LiveGame = LiveGame.json()
    if LiveGame == 404:
        return 404
    else:
        Summoners = SummonerInGame(LiveGame,region)
        return Summoners

### Gets Images for Roles
### Carry == Bottom
### Support == Utility
### Solo == Middle
def getRoleImages(data):
    role = data['role'].lower()
    print(role)
    if str(role) == "carry":
        role == "bottom"
    if str(role) == "support":
        role = "utility"
    if str(role) == "solo":
        role = "middle"

    data['role'] = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-"+ role +".png"
    return data

### Gets All Roles 
### Displayed for UI ---> soloPredict endpoint
def getRoles():
    list = [["0","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-top.png"],
        ["1","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png"],
        ["2","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-middle.png"],
        ["3","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-bottom.png"],
        ["4","https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-utility.png"]]
    RoleList = []

    i = 0
    # Each role has an ID and Link to role Image
    while i < 5:
        roleImages = {
            "RoleId":int(list[i][0]),
            'RoleLink':list[i][1]
        }
        RoleList.append(roleImages)
        i = i +1
    
    return RoleList