import requests
import requests
from config import *
import pandas as pd
import time
import pymysql


db = pymysql.connect(host=host,user='o1gbu42_StatTracker',passwd=sql_password,database =sql_user)
cursor = db.cursor()

#Gets Champion base stats
def getChampDetails(champion):
    DDRAGON = requests.get("http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json")
    DDRAGON = DDRAGON.json()
    DDRAGON = DDRAGON['data'][champion]
    DDRAGON['imageLink'] = "https://ddragon.leagueoflegends.com/cdn/12.6.1/img/champion/" + str(DDRAGON['id']) + ".png"
    DDRAGON['full'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/" + str(DDRAGON['key']) + "/" +str(DDRAGON['key']) +"000" + ".jpg"
    print(DDRAGON['full'])
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

def getChampSpellImages(champion):
    n = 29
    passive = champion['passive']['abilityIconPath'] 
    champion['passive']['abilityIconPath'] = "https://raw.communitydragon.org/latest/game/assets/" + passive[n:].lower()
    print(champion['passive']['abilityIconPath'])
    for spells in champion['spells']:
        spell = spells['abilityIconPath']
        spell = str(spell)

        spell = spell[n:]
        spell = "https://raw.communitydragon.org/latest/game/assets/" + spell.lower()
        spells['abilityIconPath'] = spell
   
def getRunesImages(runes):
    runesLinksList = []
    data = requests.get("http://ddragon.leagueoflegends.com/cdn/12.16.1/data/en_US/runesReforged.json")
    data = data.json()
    MainRune = None
    for rune in runes:
            for runes in data:
           
                for data in runes['slots']:   
                        for data in data['runes']:
                                for r in rune:
                                    if(int(r) == int(data['id'])):
                                            MainRune = runes
                                            runesLinks = {
                                            'Name': None,
                                            'Desc':None,
                                            'LinkRef':None
                                            }
                                            runesLinks['LinkRef'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/" + data['icon'].lower()
                                            runesLinks['Name'] = data['name']
                                            runesLinks['Desc'] = data['longDesc']
                                            
                                            temp = dict(runesLinks)
                                            runesLinksList.append(temp)
                                            del runesLinks
    

    runesLinks = {
        'Name': None,
        'Desc':None,
        'LinkRef':None
    }
    runesLinks['LinkRef'] = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/" + MainRune['icon'].lower()
    runesLinks['Name'] = MainRune['name']

                                            
    temp = dict(runesLinks)
    runesLinksList.append(temp)
    del runesLinks
    return runesLinksList
    #https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1


def getItemDescriptions(itemList):
    data = requests.get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/en_gb/v1/items.json")
    data = data.json()
    ItemLinksList = []

    for item in itemList:
        for i in item:
            ItemLinks = {
                            'ItemName': None,
                            'Desc':None,
                            'Link':None
                        }
            print(i)
            for items in data: 
                if(int(i) == int(items['id'])):
                        ItemLinks['ItemName'] = items['name']
                        ItemLinks['Desc'] = items['description']
                        Link = cursor.execute("SELECT `ItemLink` FROM `ItemTbl` WHERE ItemID = % s", (i,))
                        link = cursor.fetchone()
                        ItemLinks['Link'] = Normalise(link)
                        temp = dict(ItemLinks)
                        ItemLinksList.append(temp)
                        del ItemLinks

    print(ItemLinksList)
    return ItemLinksList

def Normalise(stri):
    stri = str(stri)
    stri = stri.replace('[', '')
    stri = stri.replace(']', '')
    stri = stri.replace("'", '')
    stri = stri.replace('(', '')
    stri = stri.replace(')', '')
    stri = stri.replace(",", '')
    return stri
   