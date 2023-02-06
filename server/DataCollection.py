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
summonerName = "Mealsz"

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
print("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+ SummonerInfo['puuid'] +  "/ids?start=0&count=10&api_key=" + API)
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

    cursor.execute("SELECT `RankId` FROM `RankTbl` WHERE `Rank` = (%s)", (Rank ,))
    RankId = cursor.fetchone()
    RankId = int(Normalise(RankId))

    #cursor.execute("INSERT INTO `MatchTbl`(`MatchId`, `QueueType`, `RankFk`) VALUES (%s , %s , %s)", (Match,GameType,RankId))
   
    #PlayerMatchData
    cursor.execute("SELECT `SummonerId` FROM `SummonerTbl` WHERE `SummonerName` = (%s)", (Name ,))
    SummonerID = cursor.fetchone()
    SummonerID = int(Normalise(SummonerID))
    champion = matchData[i]['champion']
    print(champion)
    cursor.execute("SELECT `ChampionId` FROM `ChampionTbl` WHERE `ChampionName` = (%s)", (champion, ))
    Champion = cursor.fetchone()
    Champion = Normalise(Champion)
    print(Champion)

    #cursor.execute("INSERT INTO `SummonerMatchTbl`(`SummonerFk`, `MatchFk`, `ChampionFk`) VALUES (%s , %s , %s)", (SummonerID,Match,Champion))








    
    connection.commit()

