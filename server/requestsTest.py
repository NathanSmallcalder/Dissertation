import requests

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
print(RankedMatches)
print(Ranked[0])
masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
#print(masteryScore.json())

masteryScore = masteryScore.json()
sortedScore = sorted(masteryScore, key=lambda k: k['championPoints'], reverse=True)

DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/9.18.1/data/en_US/champion.json")
DDRAGON = DDRAGON.json()

DDRAGON = DDRAGON['data']

for item in DDRAGON:
    temp = DDRAGON.get(item)
    for mastery in masteryScore:
        if int(temp['key']) == int(mastery['championId']):
            mastery['link'] = "https://ddragon.leagueoflegends.com/cdn/12.4.1/img/champion/" + temp['id'] +".png"
            
print(masteryScore)