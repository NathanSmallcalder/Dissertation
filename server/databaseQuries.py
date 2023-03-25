import sys

from championsRequest import *
from config import *
from RiotApiCalls import *

import mysql.connector
import json
import pymysql
#Creates a connection to database
def create_connection():
    return pymysql.connect(
        host=host,
        db='o1gbu42_StatTracker',
        user=sql_user,
        password=sql_password,
        cursorclass=pymysql.cursors.DictCursor
    )

#Gets Count of Total Games from a given championId
#e.g {'COUNT(`MatchStatsTbl`.Win)': 500}
def totalGames(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    TotalGames = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s", (champId), )
    TotalGames = cursor.fetchone()
    TotalGames = TotalGames['COUNT(`MatchStatsTbl`.Win)']
    return TotalGames

#Gets Count of Total Games from a given championId and SummonerId
#e.g {'COUNT(`MatchStatsTbl`.Win)': 500}
def totalGamesSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    TotalGames = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s", (champId, int(SummonerFk)))
    TotalGames = cursor.fetchall()
    TotalGames = TotalGames[0]
    return TotalGames

#Gets Count of Wins  from a given championId by rank
#e.g {'COUNT(`MatchStatsTbl`.Win)': 500}
def champWins(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    ChampWins = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `MatchStatsTbl`.Win = 1 and `SummonerMatchTbl`.`ChampionFk` = % s", (champId, ))
    ChampWins = cursor.fetchone()
    ChampWins = ChampWins['COUNT(`MatchStatsTbl`.Win)']
    return ChampWins

#Gets Count of Wins from a given championId and SummonerId
#e.g {'COUNT(`MatchStatsTbl`.Win)': 500}
def champWinsSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    ChampWins = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `MatchStatsTbl`.Win = 1 and `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s", (champId, int(SummonerFk)))
    ChampWins = cursor.fetchall()
    return ChampWins

#Gets Sum of Kills from a given championId by rank
#e.g {'SUM(`MatchStatsTbl`.kills)': 500}
def champKills(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    ChampKills = cursor.execute("SELECT SUM(`MatchStatsTbl`.kills) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s", (champId))
    ChampKills = cursor.fetchone()
    ChampKills = ChampKills['SUM(`MatchStatsTbl`.kills)']
    return ChampKills

#Gets average Avg Minions of champion from a given championId by rank
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`MinionsKilled`)': 500}
def avgMinions(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    MinionsAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`MinionsKilled`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(champId))
    MinionsAvg = cursor.fetchall()
    return MinionsAvg

#Gets average Avg Minions of champion from a given championId and SummonerId
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`MinionsKilled`)': 500}
def avgMinionsSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    MinionsAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`MinionsKilled`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s  and SummonerMatchTbl.SummonerFk = % s GROUP by `MatchTbl`.`RankFk`", (champId, int(SummonerFk)))
    MinionsAvg = cursor.fetchall()
   
    return MinionsAvg

#Gets average Damage Taken of champion from a given championId by rank
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`DmgTaken`)': 500}
def avgDmgTaken(champId):
    connection = create_connection()
    cursor =  connection.cursor()
    DmgTakenAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgTaken`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(champId))
    DmgTakenAvg = cursor.fetchall()
    return DmgTakenAvg

#Gets average Damage Taken of champion from a given championId and SummonerId
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`DmgTaken`)': 500}
def avgDmgTakenSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    DmgTakenAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgTaken`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s  GROUP by `MatchTbl`.`RankFk`", (champId, int(SummonerFk)))
    DmgTakenAvg = cursor.fetchall()
    return DmgTakenAvg

#Gets average Damage Dealt of champion from a given championId by rank
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`DmgDealt`)': 500}
def avgDmgDealt(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    DmgDealtAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgDealt`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(champId))
    DmgDealtAvg = cursor.fetchall()
    return DmgDealtAvg

#Gets average Damage Dealt of champion from a given championId by rank
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`DmgDealt`)': 500}
def avgDmgDealtSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    DmgDealtAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgDealt`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s  and SummonerMatchTbl.SummonerFk = % s  GROUP by `MatchTbl`.`RankFk`", (champId, int(SummonerFk)))
    DmgDealtAvg = cursor.fetchall()
    return DmgDealtAvg

#Gets average gold of champion from a given championId by rank
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`TotalGold`)': 500}
def avgGold(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    TotalGoldAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`TotalGold`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(champId))
    TotalGoldAvg = cursor.fetchall()
    return TotalGoldAvg
  

#Gets average gold of champion from a given championId and SummonerIDd
#e.g {'Rank':'unranked' , 'AVG(`MatchStatsTbl`.`TotalGold`)': 500}
def avgGoldSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    TotalGoldAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`TotalGold`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s  GROUP by `MatchTbl`.`RankFk`", (champId, int(SummonerFk)))
    TotalGoldAvg = cursor.fetchall()
    return TotalGoldAvg


#Gets Best (Most Wins) Items
#Passes value to getItemDescriptions
def commonItems(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    commonItems = cursor.execute("SELECT item1, COUNT(item1) ,item2 , COUNT(item2) ,item3 , COUNT(item3) ,item4 , COUNT(item4),item5 , COUNT(item5),item6 , COUNT(item6) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s",(champId))
    commonItems = cursor.fetchone()
    
    commonItems = getItemDescriptions(commonItems)
    return commonItems

#Gets Best (Most Wins) Items
#Passes value to getItemDescriptions
def bestItems(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    bestItems = cursor.execute("SELECT item1, COUNT(item1) ,item2 , COUNT(item2) ,item3 , COUNT(item3) ,item4 , COUNT(item4),item5 , COUNT(item5),item6 , COUNT(item6) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s AND win = 1 GROUP BY item2 ORDER BY `COUNT(item2)` DESC LIMIT 1 ",(champId))
    bestItems = cursor.fetchone()
    from championsRequest import getItemDescriptions
    bestItems = getItemDescriptions(bestItems)
    return bestItems

#Gets Common (Most Occurences) Primary Runes
#Passes value to runeImagesFromDatabase
def commonRunes(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    Runes = cursor.execute("SELECT PrimaryKeyStone, COUNT(PrimaryKeyStone), PrimarySlot1 , COUNT(PrimarySlot1) ,PrimarySlot2 , COUNT(PrimarySlot2) ,PrimarySlot3 , COUNT(PrimarySlot3) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY PrimaryKeyStone ORDER BY PrimaryKeyStone DESC LIMIT 1 ",(champId))
    Runes = cursor.fetchone()
    runeList = runeImagesFromDatabase(Runes)
    return runeList

#Gets Best (Most Wins) Primary runes
#Passes value to runeImagesFromDatabase
def bestRunes(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    bestRunes = cursor.execute("SELECT PrimaryKeyStone, COUNT(PrimaryKeyStone), PrimarySlot1 , COUNT(PrimarySlot1) ,PrimarySlot2 , COUNT(PrimarySlot2) ,PrimarySlot3 , COUNT(PrimarySlot3) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId AND Win = 1 WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY PrimaryKeyStone ORDER BY PrimaryKeyStone DESC LIMIT 1",(champId))
    bestRunes = cursor.fetchone()
    bestRuneList = runeImagesFromDatabase(bestRunes)
    return bestRuneList

#Gets Common (Most Occurences) secondary runes
#Passes value to runeImagesFromDatabase
def commonSecondaryRunes(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    SecondRunes =  cursor.execute("SELECT SecondarySlot1, COUNT(SecondarySlot1), SecondarySlot2 , COUNT(SecondarySlot2) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY SecondarySlot1 ORDER BY `COUNT(SecondarySlot1)` DESC LIMIT 1",(champId))
    SecondRunes = cursor.fetchone()
    SecondRunes = runeImagesFromDatabase(SecondRunes)
    return SecondRunes

#Gets Best (Most Wins) secondary runes
#Passes value to runeImagesFromDatabase
def bestSecondaryRunes(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    bestSecondRunes = cursor.execute("SELECT SecondarySlot1, COUNT(SecondarySlot1), SecondarySlot2 , COUNT(SecondarySlot2) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s AND Win = 1 GROUP BY SecondarySlot1 ORDER BY `COUNT(SecondarySlot1)` DESC LIMIT 1",(champId))
    bestSecondRunes = cursor.fetchone()
    bestSecondRunes = runeImagesFromDatabase(bestSecondRunes)
    return bestSecondRunes

#Pass runes from database into a dictionary containing RuneName,RuneLink and Description 
#Returns a List of Dictionary of runes
def runeImagesFromDatabase(runes): 
    RuneList = []
    tempRunes = []
    for key in runes:
        if "COUNT" in key:
            count = runes[key]
        else:
            tempRunes.append(runes[key])
    MainRune = None
    runes = list(runes)
    runes = list(filter(lambda a: a != count, runes))
    for val in tempRunes:
            rune,MainRune = getRunesImages(val)
            RuneList.append(rune)
            MainRune = MainRune
    RuneList.insert(0, MainRune)

    return RuneList

#Gets the KDA of a given champion by champId
#e.g {' AVG(kills)':5 , 'AVG(deaths)': 7,AVG(assists): 2}
#Returns a String 5/7/2
def kdaFromDatabase(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    kda = cursor.execute("SELECT AVG(kills), AVG(deaths), AVG(assists) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s",(champId))
    kda = cursor.fetchone()
    print(kda)
    kda = str(int(kda['AVG(kills)'])) + "/" + str(int(kda['AVG(deaths)'])) + "/" + str(int(kda['AVG(assists)']))
    return kda

#Gets the KDA of a given champion by champId and SummonerId
#e.g {' AVG(kills)':5 , 'AVG(deaths)': 7,AVG(assists): 2}
#Returns a String 5/7/2
def kdaFromDatabaseSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    kda = cursor.execute("SELECT AVG(kills), AVG(deaths), AVG(assists) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s and SummonerMatchTbl.SummonerFk = % s", (champId, int(SummonerFk)))
    kda = cursor.fetchall()
    kda = str(int(kda[0]['AVG(kills)'])) + "/" + str(int(kda[0]['AVG(deaths)'])) + "/" + str(int(kda[0]['AVG(assists)']))
    return kda

#Gets the most frequently played lane of a given champion by champId
def laneFromDatabase(champId): 
    connection = create_connection()
    cursor =  connection.cursor()
    position = cursor.execute("SELECT Lane, COUNT(Lane) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s", (champId))
    position = cursor.fetchone()
    position = position['Lane']
    return position

#Gets most played Position of champion from a given championId and SummonerId
#e.g {'Lane':'MIDDLE' , 'COUNT(Lane)': 500}
def laneFromDatabaseSummoner(champId,SummonerFk): 
    connection = create_connection()
    cursor =  connection.cursor()
    position = cursor.execute("SELECT Lane, COUNT(Lane) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s and SummonerMatchTbl.SummonerFk = % s GROUP BY Lane ORDER BY PrimaryKeyStone DESC ", (champId, int(SummonerFk)))
    position = cursor.fetchone()
    position = position['Lane']
    print(position)
    return position

#Gets the SummonerId from a given SummonerName
def getSummonerIdFromDatabase(SummonerName): 
    connection = create_connection()
    cursor =  connection.cursor()
    SummonerFk = cursor.execute("SELECT SummonerUserTbl.SummonerID from SummonerUserTbl where SummonerName = % s", (SummonerName, ))
    SummonerFk = cursor.fetchall()
    SummonerFk = SummonerFk[0]['SummonerID']
    print(SummonerFk)
    return SummonerFk

def getItemLink(id): 
    connection = create_connection()
    cursor =  connection.cursor()
    Link = cursor.execute("SELECT `ItemLink` FROM `ItemTbl` WHERE ItemID = % s", (id))
    Link = cursor.fetchone()
    Link = Link['ItemLink']
    return Link

#Gets All Champions
def getAllChampions(): 
    connection = create_connection()
    cursor =  connection.cursor()
    champ = cursor.execute("SELECT * FROM `ChampionTbl`")
    champ = cursor.fetchall()
    return champ

#Gets the Top players by wins from database
def getBestPlayers():
    connection = create_connection()
    cursor =  connection.cursor()
    players = cursor.execute("SELECT DISTINCT SummonerName, COUNT(MatchStatsTbl.Win), AVG(MatchStatsTbl.kills),AVG(MatchStatsTbl.assists), AVG(MatchStatsTbl.deaths), AVG(MatchStatsTbl.BaronKills), AVG(MatchStatsTbl.DragonKills) FROM `SummonerUserTbl` JOIN SummonerMatchTbl on SummonerID = SummonerMatchTbl.SummonerFk JOIN MatchStatsTbl on SummonerMatchTbl.SummonerMatchId = MatchStatsTbl.SummonerMatchFk WHERE MatchStatsTbl.Win = 1 GROUP BY SummonerName ORDER by COUNT(MatchStatsTbl.Win) DESC LIMIT 15")
    players = cursor.fetchall()
    return players

#Gets Champion table
def getChampionAverages():
    connection = create_connection()
    cursor =  connection.cursor()
    query = ('SELECT `ChampionTbl`.`ChampionName`, AVG(`MatchStatsTbl`.`kills`),AVG(`MatchStatsTbl`.`deaths`),AVG(`MatchStatsTbl`.`assists`), AVG(`MatchStatsTbl`.`Win`), AVG(`MatchTbl`.`GameDuration`) FROM `SummonerMatchTbl`   JOIN `MatchStatsTbl` ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId   JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk`  JOIN `ChampionTbl` ON  `SummonerMatchTbl`.`ChampionFk` = `ChampionTbl`.`ChampionId`   WHERE `MatchTbl`.`QueueType` = "CLASSIC"  GROUP BY `ChampionTbl`.`ChampionId`')
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getChampionBestPlayers(ChampId):
    connection = create_connection()
    cursor =  connection.cursor()
    query = ("SELECT DISTINCT SummonerName, COUNT(MatchStatsTbl.Win), AVG(MatchStatsTbl.kills),AVG(MatchStatsTbl.assists), AVG(MatchStatsTbl.deaths), AVG(MatchStatsTbl.BaronKills), AVG(MatchStatsTbl.DragonKills) FROM `SummonerUserTbl` JOIN SummonerMatchTbl on SummonerID = SummonerMatchTbl.SummonerFk JOIN MatchStatsTbl on SummonerMatchTbl.SummonerMatchId = MatchStatsTbl.SummonerMatchFk WHERE MatchStatsTbl.Win = 1 and SummonerMatchTbl.ChampionFk = %s GROUP BY SummonerName ORDER by COUNT(MatchStatsTbl.Win) DESC LIMIT 15 ")
    cursor.execute(query, (ChampId,))
    data = cursor.fetchall()
    return data
