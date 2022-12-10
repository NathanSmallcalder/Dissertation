import pytest

def getImages():
    SummonerInfo = requests.get("https://" + Region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + API)
    SummonerInfo = SummonerInfo.json()
    id =  SummonerInfo['id'] 
    masteryScore = requests.get("https://" + Region + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + "?api_key=" + API)
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
                responseCode = request.get(mastery['link'])
                if(responseCode == 200):
                    pass
                else:
                    pytest.fail()
    
assert responseCode == 200