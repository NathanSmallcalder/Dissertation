import requests
from config import api_key
import pandas as pd

API = api_key
MatchIDG = []

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
    
#Gets Profile Image
def getImageLink(SummonerInfo):
    profileIcon = str(SummonerInfo['profileIconId'])
    SummonerInfo['profileIconId'] = 'http://ddragon.leagueoflegends.com/cdn/12.6.1/img/profileicon/' + profileIcon +'.png'
   
def getSummonerDetails(Region,summonerName):
    print("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    
    SummonerInfo = SummonerInfo.json()
    return SummonerInfo

def getRankedStats(Region,id):
    RankedMatches = requests.get("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key="+API)

    Ranked = RankedMatches.json()
    return Ranked

def getMasteryStats(Region,id):
    masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
    print("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
    masteryScore = masteryScore.json()
    getChampImages(masteryScore)
    return masteryScore

def getMatchData(region,id,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=5&api_key=" + API)
    print("https://"+ region + ".api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=5&api_key=" + API)
    MatchIDs = MatchIDs.json()
    data = getMatches("europe", MatchIDs, puuid)
    return data

def getMatchIds(region,id,puuid):
    MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=5&api_key=" + API)
    print("https://"+ region + ".api.riotgames.com/lol/match/v5/matches/by-puuid/"+ puuid +  "/ids?start=0&count=5&api_key=" + API)
    MatchIDs = MatchIDs.json()
    return MatchIDs


def getMatches(region,MatchIDs,puuid):
    dataList = []
    for matchID in MatchIDs:
        data = {
                'GameDuration':[], 
                'champion': [],
                'kills':[] ,
                'deaths': [],
                'assists': [],
                'win': [],
        }
        MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
        print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=" + api_key)
            
        MatchData = MatchData.json()
        participants = MatchData['metadata']['participants']
        player_index = participants.index(puuid)

        player_data = MatchData['info']['participants'][player_index]
        gameMins = MatchData['info']['gameDuration']
        champion = player_data['championName']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        win = player_data['win']
        data['champion'].append(champion)
        data['kills'].append(k)
        data['deaths'].append(d)
        data['assists'].append(a)
        data['win'].append(win)    
        data['GameDuration'].append(gameMins)
        df = pd.DataFrame(data)    
        df['win'] = df['win'].astype(int) 
        print(data)
        dataList.append(data)
    return dataList

def getMatchTimeline(region,id,puuid,data):
    print(data[1]['GameDuration'])
    MatchIDs = getMatchIds(region,id,puuid)
    print(MatchIDs)
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


            MeanData = {
                    'avgGoldPerMin': [],
                    'creepScore': [],
                    'totalDamageDonePerMin': [],
                    'totalDamageTakenPerMin': []
            }
            MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"/timeline?api_key=RGAPI-546ff69b-0cba-44ac-b79d-be1472f09bc1")
            MatchData = MatchData.json()
            participants = MatchData['metadata']['participants']
            # Now, find where in the data our players puuid is found
            player_index = participants.index(puuid)
            player_index = str(player_index)
            matchData = MatchData['info']['frames']

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
            print("==============================")
    i = 0
    count = 0
    mean = 0

    while i < 10:
            for line in ListS:
                    print(line['totalDamageTaken'][0])
                    dmgTaken = line['totalDamageTaken'][i]
                    mean =+ dmgTaken
                    count=count +1
            
            mean = mean / count
            count=0
            MeanData['totalDamageTakenPerMin'].append(mean)
            i = i + 1
                    


    print(MeanData)
    gameTime = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]


    return MeanData
