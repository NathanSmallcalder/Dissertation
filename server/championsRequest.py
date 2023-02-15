import requests


#Gets Champion base stats
def getChampDetails(champion):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data'][champion]
    DDRAGON['imageLink'] = "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/" + str(DDRAGON['name']) + ".png"
    print(DDRAGON['imageLink'])
    print(DDRAGON)
    return DDRAGON

def getChampAbilities(champion):
    key = champion['key']
    data = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/" + key + ".json")
    data = data.json()
    
    data['passive']['abilityVideoPath'] = "https://d28xe8vt774jo5.cloudfront.net/" + data['passive']['abilityVideoPath'] 
    for spells in data['spells']:
        spell = spells['abilityVideoPath']
        spells['abilityVideoPath'] = "https://d28xe8vt774jo5.cloudfront.net/"  + spell
    return data



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

#Gets ChampionImage URLS for ChampionTable
def getChampImagesSingle(ChampId):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data']
    for item in DDRAGON:
        temp = DDRAGON.get(item)
        for champs in ChampId:
            if int(temp['key']) == (champs[0]):
                champs[0] = "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/" + temp['id'] +".png"


