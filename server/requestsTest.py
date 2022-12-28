import requests
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

API =  "RGAPI-546ff69b-0cba-44ac-b79d-be1472f09bc1"
Region = "EUW1"
summonerName = "Ehhhh"

SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
print(SummonerInfo.json())
SummonerInfo = SummonerInfo.json()
id =  SummonerInfo['id'] 
RankedMatches = requests.get("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key=" + API)
Ranked = RankedMatches.json()
print("https://" + Region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + "?api_key=" + API)
#print(RankedMatches)
rankee = Ranked[0]
#print(rankee)
masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
#print(masteryScore.json())

masteryScore = masteryScore.json()
sortedScore = sorted(masteryScore, key=lambda k: k['championPoints'], reverse=True)

MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=5&api_key=" + API)
count = 5
MatchIDs = MatchIDs.json()

print(MatchIDs)


data = {
        'GameDuration':[],
        'champion': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': []
}


for matchID in MatchIDs:
    MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=")
    #print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=RGAPI-49316441-6393-4a47-b249-d06ceb6fc9fe")
    MatchData = MatchData.json()
    # A list of all the participants puuids
    participants = MatchData['metadata']['participants']
    # Now, find where in the data our players puuid is found
    player_index = participants.index(SummonerInfo['puuid'])
    #print(MatchData['info']['participants'][player_index])

    player_data = MatchData['info']['participants'][player_index]
    gameMins = MatchData['info']['gameDuration']
    champion = player_data['championName']
    k = player_data['kills']
    d = player_data['deaths']
    a = player_data['assists']
    win = player_data['win']        # add them to our dataset
    data['champion'].append(champion)
    data['kills'].append(k)
    data['deaths'].append(d)
    data['assists'].append(a)
    data['win'].append(win)    
    data['GameDuration'].append(gameMins)



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

        MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"/timeline?api_key=")
        print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"/timeline?api_key=RGAPI-546ff69b-0cba-44ac-b79d-be1472f09bc1")
        MatchData = MatchData.json()
        participants = MatchData['metadata']['participants']
        # Now, find where in the data our players puuid is found
        player_index = participants.index(SummonerInfo['puuid'])
        player_index = str(player_index)
        matchData = MatchData['info']['frames']

        i = 0
        matchL = data['GameDuration'][ie] /60 + 1
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
        print(ListS)
        print("==============================")



i = 0
counter = 0
mean = 0

while i < 21:
        for line in ListS:
                dmgTaken = line['totalDamageTaken'][i]
                mean =+ dmgTaken
                count=count +1
        
        mean = mean / count
        count=0
        MeanData['totalDamageTakenPerMin'].append(mean)
        i = i + 1
                


print(MeanData)


gameTime = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
plt.plot(gameTime,MeanData['totalDamageTakenPerMin'])
plt.title("Total Damage Taken Per Min (Last 20 Games)")
plt.show()
plt.savefig('DmgTaken.png',transparent=True)
plt.clf()

gameTime = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
plt.plot(gameTime,MeanData['avgGoldPerMin'])
plt.title("Total Gold Earnt Per Min (Last 20 Games)")
plt.show()
plt.savefig('avgGoldPerMin.png',transparent=True)
plt.clf()
gameTime = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
plt.plot(gameTime,MeanData['creepScore'])
plt.title("Total Minions Killed Per Min (Last 20 Games)")
plt.show()
plt.savefig('creepScore.png',transparent=True)
plt.clf()
gameTime = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
plt.plot(gameTime,MeanData['totalDamageDonePerMin'])
plt.title("Total Damage Given Per Min (Last 20 Games)")
plt.show()
plt.savefig('totalDamageDonePerMin.png',transparent=True)
plt.clf()
#df = pd.DataFrame(data)    
#df['win'] = df['win'].astype(int) 


#print(df)