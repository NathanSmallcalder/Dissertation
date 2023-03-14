import sys
sys.path.append('..')
from config import *
from RiotApiCalls import *

import mysql.connector
import json
   
def Normalise(stri):
    stri = str(stri)
    stri = stri.replace('[', '')
    stri = stri.replace(']', '')
    stri = stri.replace("'", '')
    stri = stri.replace('(', '')
    stri = stri.replace(')', '')
    stri = stri.replace(",", '')
    return stri
   
connection = mysql.connector.connect(user=sql_user, password=sql_password, host=host, database='o1gbu42_StatTracker')
cursor = connection.cursor(buffered=True)
     
Region = "EUW1"
summonerName = "Zara zjem myszke"
connection.autocommit = True
db_Info = connection.get_server_info()

SummonerInfo = getSummonerDetails(Region,summonerName)
SummId = SummonerInfo['id']
Name = SummonerInfo['name']

matchIds = getMatchIds(Region,SummonerInfo['puuid'])

for matchId in matchIds:     
        MatchData = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchId +"?api_key=" + api_key)
        MatchData = MatchData.json()
        print("https://europe.api.riotgames.com/lol/match/v5/matches/"+ matchId +"?api_key=" + api_key)

        i = 0
        #Gets Champs (0-4 Team 1) , (5-9 Team 2)
        champList = []
        while i < 10:
                champion = MatchData['info']['participants'][i]['championName']
                cursor.execute("SELECT `ChampionId` FROM `ChampionTbl` WHERE `ChampionName` = (%s)", (champion, ))
                Champion = cursor.fetchall()
                Champion = Normalise(Champion)
                print("Champion", Champion, champion)
                champList.append(Champion)
                i = i + 1

        #100 or 0 blue team 
        BaronKillsBlue = int(MatchData['info']['teams'][0]['objectives']['baron']['kills'])
        ChampionKillsBlue = int(MatchData['info']['teams'][0]['objectives']['champion']['kills'])
        DragonKillsBlue = int(MatchData['info']['teams'][0]['objectives']['dragon']['kills'])
        BlueRiftKills = int(MatchData['info']['teams'][0]['objectives']['riftHerald']['kills'])
        ChampionKillsBlue = int(MatchData['info']['teams'][0]['objectives']['champion']['kills'])
        towerKillsBlue = int(MatchData['info']['teams'][0]['objectives']['tower']['kills'])
        BlueWin = int(MatchData['info']['teams'][0]['win'])
        
        #200 or 1 red team
        BaronKillsRed = int(MatchData['info']['teams'][1]['objectives']['baron']['kills'])
        ChampionKillsRed = int(MatchData['info']['teams'][1]['objectives']['champion']['kills'])
        DragonKillsRed  = int(MatchData['info']['teams'][1]['objectives']['dragon']['kills'])
        RedRiftKills = int(MatchData['info']['teams'][1]['objectives']['riftHerald']['kills'])
        ChampionKillsRed  = int(MatchData['info']['teams'][1]['objectives']['champion']['kills'])
        towerKillsRed  = int(MatchData['info']['teams'][1]['objectives']['tower']['kills'])
        RedWin = int(MatchData['info']['teams'][1]['win'])

        cursor.execute("SELECT `MatchFk` FROM `TeamMatchTbl` WHERE `MatchFk` = (%s)", (str(matchId) ,))
        matchCheck = cursor.fetchone()
        print(matchCheck)
        if matchCheck is None:
            cursor.execute("INSERT INTO `TeamMatchTbl`(`MatchFk`, `B1Champ`, `B2Champ`, `B3Champ`, `B4Champ`, `B5Champ`, `R1Champ`, `R2Champ`, `R3Champ`, `R4Champ`, `R5Champ`, `BlueBaronKills`, `BlueRiftHeraldKills`, `BlueDragonKills`, `BlueTowerKills`, `BlueKills`, `RedBaronKills`, `RedRiftHeraldKills`, `RedDragonKills`, `RedTowerKills`, `RedKills`, `RedWin`, `BlueWin`)VALUES (%s , %s , %s, %s,%s , %s , %s, %s,%s , %s , %s, %s,%s , %s , %s, %s,%s , %s , %s,  %s, %s, %s, %s)",(matchId,champList[0],champList[1],champList[2],champList[3],champList[4],champList[5],champList[6],champList[7],champList[8],champList[9],BaronKillsBlue,BlueRiftKills,DragonKillsBlue,towerKillsBlue,ChampionKillsBlue,BaronKillsRed,RedRiftKills,DragonKillsRed,towerKillsRed,ChampionKillsRed,RedWin,BlueWin,))
            connection.commit()
