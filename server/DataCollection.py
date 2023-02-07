from RiotApiCalls import *
from config import *
import mysql.connector
   
   
def Normalise(stri):
    stri = str(stri)
    stri = stri.replace('[', '')
    stri = stri.replace(']', '')
    stri = stri.replace("'", '')
    stri = stri.replace('(', '')
    stri = stri.replace(')', '')
    stri = stri.replace(",", '')
    return stri
   
connection = mysql.connector.connect(host=host,
                                     database= sql_user,
                                     user=sql_user,
                                     password=sql_password)
                                
Region = "EUW1"
summonerName = "Gwurie"

db_Info = connection.get_server_info()
print("Connected to MySQL Server version ", db_Info)
cursor = connection.cursor()

SummonerInfo = getSummonerDetails(Region,summonerName)
SummId = SummonerInfo['id']
RankedDetails = getRankedStats(Region,SummId)
Name = SummonerInfo['name']

#cursor.execute("INSERT INTO `SummonerTbl`(`SummonerName`) VALUES (%s )", (SummonerInfo['name'],))
#connection.commit()

MatchIDs = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=10&api_key=" + API)
MatchIDs = MatchIDs.json()

matchData = getMatches("euw1" ,MatchIDs,SummonerInfo)


matchData2 = getsMatchData()


Match = matchData2[1]['MatchIDS']
Match = Normalise(Match)


i = 0
for MatchId in MatchIDs:
    #MatchData
    Match = matchData2[i]['MatchIDS']
    Rank = matchData2[i]['Rank']
    GameType = matchData2[i]['GameType']

    Match = Normalise(Match)
    GameType = Normalise(GameType)
    Rank = Normalise(Rank)
    print(Rank)
    cursor.execute("SELECT `RankId` FROM `RankTbl` WHERE `Rank` = (%s)", (Rank ,))
    RankId = cursor.fetchone()
    RankId = int(Normalise(RankId))
   
    #PlayerMatchData
    cursor.execute("SELECT `SummonerId` FROM `SummonerTbl` WHERE `SummonerName` = (%s)", (Name ,))
    SummonerID = cursor.fetchone()
    SummonerID = int(Normalise(SummonerID))

    champion = matchData[i]['champion']
    print(champion)
    cursor.execute("SELECT `ChampionId` FROM `ChampionTbl` WHERE `ChampionName` = (%s)", (champion, ))
    Champion = cursor.fetchone()
    Champion = Normalise(Champion)
    
    cursor.execute("SELECT `MatchId` FROM `MatchTbl` WHERE `MatchId` = (%s)", (str(Match) ,))
    MatchVerify = cursor.fetchone()
    MatchVerify = Normalise(MatchVerify)
    print(MatchVerify)
   

    if MatchVerify == "None":
        cursor.execute("INSERT INTO `MatchTbl`(`MatchId`, `QueueType`, `RankFk`) VALUES (%s , %s , %s)", (Match,GameType,RankId))
        connection.commit()
        cursor.execute("SELECT `MatchId` FROM `MatchTbl` WHERE `MatchId` = (%s)", (str(Match) ,))
        MatchVerify = cursor.fetchone()
        MatchVerify = Normalise(MatchVerify)
        print(MatchVerify)
    else:
        print("Pass")
        pass

    cursor.execute("INSERT INTO `SummonerMatchTbl`(`SummonerFk`, `MatchFk`, `ChampionFk`) VALUES (%s , %s , %s)", (SummonerID,MatchVerify,Champion))
    cursor.execute("SELECT `SummonerMatchId` FROM `SummonerMatchTbl` WHERE `MatchFk` = (%s) AND `SummonerFk` = (%s)", (str(Match) ,SummonerID))
    SummMatchId = cursor.fetchone()
    SummMatchId = Normalise(SummMatchId)
    print("SummMatchID = " , SummMatchId)

    cs = matchData[i]['cs']
    dmgDealt = matchData[i]['physicalDamageDealtToChampions']
    dmgTaken = matchData[i]['physicalDamageTaken']

    GameDuration = matchData[i]['GameDuration']
    TurretDmgDealt = matchData[i]['TowerDamageDealt']
    goldEarned = matchData[i]['goldEarned']
    Role= matchData[i]['Role']
    win = matchData[i]['win']
    Item1 = matchData[i]['Items'][0]
    Item2 = matchData[i]['Items'][1]
    Item3 = matchData[i]['Items'][2]
    Item4 = matchData[i]['Items'][3]
    Item5 = matchData[i]['Items'][4]
    Item6 = matchData[i]['Items'][5]
    kills = matchData[i]['kills']
    deaths = matchData[i]['deaths']
    asssts = matchData[i]['assists']
    PK1 = matchData[i]['PrimaryKeyStone'][0]
    PK2 = matchData[i]['PrimaryKeyStone'][1]
    PK3 = matchData[i]['PrimaryKeyStone'][2]
    PK4 = matchData[i]['PrimaryKeyStone'][3]
    SK1 = matchData[i]['SecondaryKeyStone'][0]
    SK2 = matchData[i]['SecondaryKeyStone'][1]
    EmemyLane = matchData[i]['EnemyChamp']
    cursor.execute("SELECT `ChampionId` FROM `ChampionTbl` WHERE `ChampionName` = (%s)", (EmemyLane, ))
    Enemy = cursor.fetchone()
    Enemy = Normalise(Enemy)
    
    if(Enemy == "None"):
        Enemy = 0




    cursor.execute("INSERT INTO `MatchStatsTbl`(`SummonerMatchFk`, `MinionsKilled`, `DmgDealt`, `DmgTaken`, `MatchDuration`, `TurretDmgDealt`, `TotalGold`, `Lane`, `Win`, `item1`, `item2`, `item3`, `item4`, `item5`, `item6`, `kills`, `deaths`, `assists`, `PrimaryKeyStone`, `PrimarySlot1`, `PrimarySlot2`, `PrimarySlot3`, `SecondarySlot1`, `SecondarySlot2`, `EnemyChampionFk`)VALUES(%s , %s , %s ,%s , %s , %s, %s , %s , %s ,%s , %s , %s,%s , %s , %s ,%s , %s , %s,%s , %s , %s ,%s , %s , %s, %s)", (str(SummMatchId), cs ,dmgDealt,dmgTaken,GameDuration,TurretDmgDealt,goldEarned,Role,win,Item1 ,Item2,Item3,Item4,Item5,Item6,kills,deaths,asssts,PK1,PK2,PK3,PK4,SK1,SK2,Enemy))
    connection.commit()
    i = i + 1


