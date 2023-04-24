import requests
import requests
from config import *
import pandas as pd
import time
from RiotApiCalls import *


#Gets Champion base stats
def getChampDetails(champion):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/13.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data'][champion]
    DDRAGON['imageLink'] = "https://ddragon.leagueoflegends.com/cdn/13.6.1/img/champion/" + str(DDRAGON['id']) + ".png"
    DDRAGON['full'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/" + str(DDRAGON['key']) + "/" +str(DDRAGON['key']) +"000" + ".jpg"
    return DDRAGON

#Gets Champion ability videos
def getChampAbilities(champion): #
    key = champion['key']
    data = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/" + key + ".json")
    data = data.json()
    
    data['passive']['abilityVideoPath'] = "https://d28xe8vt774jo5.cloudfront.net/" + data['passive']['abilityVideoPath'] 
    for spells in data['spells']:
        spell = spells['abilityVideoPath']
        spells['abilityVideoPath'] = "https://d28xe8vt774jo5.cloudfront.net/"  + spell
    return data

#Gets ChampionImage URLS into masteryScore JSON file
def getChampImages(masteryScore):#
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/13.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data']
    for item in DDRAGON:
        temp = DDRAGON.get(item)
        for mastery in masteryScore:
            if int(temp['key']) == int(mastery['championId']):
                mastery['name'] = temp['id']
                mastery['link'] = "https://ddragon.leagueoflegends.com/cdn/13.6.1/img/champion/" + temp['id'] +".png"


#Gets ChampionImage URLS for ChampionTable
def getChampImagesSingle(ChampId): # 
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/13.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data']
  
    for item in DDRAGON:
        temp = DDRAGON.get(item)
        if int(temp['key']) == (int(ChampId)):
            ChampId = "https://ddragon.leagueoflegends.com/cdn/13.6.1/img/champion/" + temp['id'] +".png"
            return ChampId

### Gets Champion Spell Images for /champion?champion="" directory
### passes champion back by reference
def getChampSpellImages(champion): #
    n = 29
    passive = champion['passive']['abilityIconPath'] 
    champion['passive']['abilityIconPath'] = "https://raw.communitydragon.org/latest/game/assets/" + passive[n:].lower()
    
    for spells in champion['spells']:
        spell = spells['abilityIconPath']
        spell = str(spell)

        spell = spell[n:]
        spell = "https://raw.communitydragon.org/latest/game/assets/" + spell.lower()
        spells['abilityIconPath'] = spell
    
### Gets Rune images and Description
def getRunesImages(runesList): 
    runesLinksList = []

    data = requests.get("http://ddragon.leagueoflegends.com/cdn/13.6.1/data/en_US/runesReforged.json")
    data = data.json()
    try:
        for runes in data:
            for data in runes['slots']:   
                for data in data['runes']:
                        if int(runesList) == int(data['id']):
                            MainRunes = runes
                            runesLinks = {
                                    'Name': None,
                                    'Desc':None,
                                    'LinkRef':None
                            }
                            runesLinks['LinkRef'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/" + data['icon'].lower()
                            runesLinks['Name'] = data['name']
                            runesLinks['Desc'] = data['longDesc']
                            
                            MainRune = {
                                'Name': None,
                                'Desc':None,
                                'LinkRef':None
                            }
                            
                            MainRune['LinkRef'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/" + MainRunes['icon'].lower()
                            MainRune['Name'] = MainRunes['name']
                        
                            return runesLinks, MainRune
    except:
        pass

### Gets Rune images and Description
def getRunesImagesList(runesList): 
    runesLinksList = []
    data = requests.get("http://ddragon.leagueoflegends.com/cdn/13.6.1/data/en_US/runesReforged.json")
    data = data.json()
    try:
        for runes in data:
            for data in runes['slots']:   
                for data in data['runes']:
                    for rune in runesList:
                        if int(rune) == int(data['id']):
                            MainRunes = runes
                            runesLinks = {
                                    'Name': None,
                                    'Desc':None,
                                    'LinkRef':None
                            }
                            runesLinks['LinkRef'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/" + data['icon'].lower()
                            runesLinks['Name'] = data['name']
                            runesLinks['Desc'] = data['longDesc']
                            
                            MainRune = {
                                'Name': None,
                                'Desc':None,
                                'LinkRef':None
                            }
                            
                            MainRune['LinkRef'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/" + MainRunes['icon'].lower()
                            MainRune['Name'] = MainRunes['name']
                        
                            return runesLinks, MainRune
    except:
        pass
    
    #https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1

#Passing ItemIds to get a dictionary of ItemName, Description and Image Link
def getItemDescriptions(itemList):
    from databaseQuries import getItemLink
    data = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/en_gb/v1/items.json")
    data = data.json()
    ItemLinksList = []
    for item in itemList:
        ItemLinks = {
                            'ItemName': None,
                            'Desc':None,
                            'Link':None
                        }

        for items in data:
            if(int(itemList[item]) == int(items['id'])):
                if "SUM" not in item:
                        ItemLinks['ItemName'] = items['name']
                        ItemLinks['Desc'] = items['description']
                        link = getItemLink(int(itemList[item]))
                        ItemLinks['Link'] = link
                        temp = dict(ItemLinks)
                        ItemLinksList.append(temp)
                        del ItemLinks
    
    return ItemLinksList


   

