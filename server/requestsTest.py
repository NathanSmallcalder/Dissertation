import requests
import pandas as pd

API =  ""
Region = "EUW1"
summonerName = "Mealsz"

SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
#print(SummonerInfo.json())
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

MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=10&api_key=" + API)
MatchIDs = MatchIDs.json()




data = {
        'champion': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': []
}

for matchID in MatchIDs:
    MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=RGAPI-49316441-6393-4a47-b249-d06ceb6fc9fe")
    #print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchID +"?api_key=RGAPI-49316441-6393-4a47-b249-d06ceb6fc9fe")
    MatchData = MatchData.json()
    # A list of all the participants puuids
    participants = MatchData['metadata']['participants']
    # Now, find where in the data our players puuid is found
    
    player_index = participants.index(SummonerInfo['puuid'])
    #print(MatchData['info']['participants'][player_index])

    player_data = MatchData['info']['participants'][player_index]
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


df = pd.DataFrame(data)
df['win'] = df['win'].astype(int)

print(df.groupby('champion').mean())
