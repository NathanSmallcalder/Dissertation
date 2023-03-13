from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import requests
import secrets
from config import *
from RiotApiCalls import *
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import warnings
from championsRequest import *
import sys
import json

import mlAlgorithms
from mlAlgorithms import randomForest

warnings.filterwarnings('ignore')

app = Flask(__name__)
key = secrets.token_urlsafe(16)
key = secrets.token_hex(16)

#Config
app.config['SECRET_KEY'] = 'key'
app.config['MYSQL_HOST'] = host 
app.config['MYSQL_USER'] = sql_user
app.config['MYSQL_PASSWORD'] = sql_password
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#Login
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM Account WHERE AccountName = % s AND Password = % s', (username, password, ))
        
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['AccountName'] = account['AccountName']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
        
    return render_template('Login.html', msg = msg)

#Register
@app.route('/register', methods =['GET', 'POST'])
def register():
    connection = create_connection()
    cursor =  connection.cursor()
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password'  in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM Account WHERE AccountName = % s', (username,))

        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute("INSERT INTO `Account`(`AccountName`, `Password`) VALUES (%s , %s)", (username, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    return render_template('signup.html', msg = msg)

#Summoner Routing
@app.route('/summoner',methods=['GET','POST'])
def getSummoner():
    connection = create_connection()
    cursor =  connection.cursor()

    summonerName = request.args.get('summoner')
    Region = request.args.get('region')
    SummonerInfo = getSummonerDetails(Region,summonerName)
    SummId = SummonerInfo['id']
    RankedDetails = getRankedStats(Region,SummId)
    try:
        SOLO = RankedDetails[1]
        FLEX = RankedDetails[0]
        CalcWinRate(FLEX)
        CalcWinRate(SOLO)
        RankedImages(FLEX)
        RankedImages(SOLO)
    except:
        FLEX = {"queueType":"RANKED_SOLO_5x5","tier":"GOLD","rank":"II","summonerName":"Frycks","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}
        SOLO = {"queueType":"RANKED_SOLO_5x5","tier":"GOLD","rank":"II","summonerName":"Frycks","leaguePoints":0,"wins":0,"losses":0,
        "ImageUrl":'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/unranked.png',"WinRate":"0%"}

    getImageLink(SummonerInfo)
    masteryScore = getMasteryStats(Region,SummId)
    data = getMatchData(Region, SummId, SummonerInfo)
    participants = getGameParticipantsList()
    MeanData = getMatchTimeline(Region, SummId, SummonerInfo['puuid'],data)
    fullMatch = getPlayerMatchData()
    
    stri = "https://5000-nathansmall-dissertatio-8z3sdftfozh.ws-eu84.gitpod.io/summoner?summoner=Mealsz&region=EUW1"
    s = stri.split('/s', 1)[0]

    return render_template('summonerPage.html', SummonerInfo = SummonerInfo,
    soloRanked = SOLO,flexRanked = FLEX,masteryScore = masteryScore,data=data, 
    MeanData = MeanData, fullMatch = fullMatch,participants = participants,summonerName = summonerName,Region = Region, weblink = s)

#Summoner in Game Screen
@app.route('/summoner/in-game',methods=['GET','POST'])
def SummonerInGame():
    connection = create_connection()
    cursor =  connection.cursor()
    SummonerName = request.args.get('summoner')
    Region = request.args.get('region')
    Summoners = summonerInGameCheck(Region,SummonerName)
    return render_template('summonerInGame.html', Summoners = Summoners)

#Champion Stats - From Database
@app.route('/champions', methods=['GET','POST'])
def ChampionTablePage():
    connection = create_connection()
    cursor =  connection.cursor()
    query = ('SELECT `ChampionTbl`.`ChampionName`, AVG(`MatchStatsTbl`.`kills`),AVG(`MatchStatsTbl`.`deaths`),AVG(`MatchStatsTbl`.`assists`), AVG(`MatchStatsTbl`.`Win`), AVG(`MatchTbl`.`GameDuration`) FROM `SummonerMatchTbl`   JOIN `MatchStatsTbl` ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId   JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk`  JOIN `ChampionTbl` ON  `SummonerMatchTbl`.`ChampionFk` = `ChampionTbl`.`ChampionId`   WHERE `MatchTbl`.`QueueType` = "CLASSIC"  GROUP BY `ChampionTbl`.`ChampionId`;')
    cursor.execute(query)
    data = cursor.fetchall()
   

    #columns = ['ChampionFk', 'kills', 'deaths','assists', 'Win', 'GameDuration']
    
    return render_template('champions.html',data=  data)


#InDepth Champion Stats
@app.route('/champion' , methods=['GET','POST'])
def championData():
    connection = create_connection()
    champName = request.args.get('champion')
    championStats = getChampDetails(champName)
    
    ChampionAbilities = getChampAbilities(championStats)
    getChampSpellImages(ChampionAbilities)

    TotalGames = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s", (int(championStats['key']), ))
    TotalGames = cursor.fetchall()

    ChampWins = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `MatchStatsTbl`.Win = 1 and `SummonerMatchTbl`.`ChampionFk` = % s", (int(championStats['key']), ))
    ChampWins = cursor.fetchall()

    ChampKills = cursor.execute("SELECT SUM(`MatchStatsTbl`.kills) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s", (int(championStats['key']), ))
    ChampKills = cursor.fetchall()

    ChampKills = str(ChampKills[0][0])
    TotalGames = str(TotalGames[0][0])

    #winRate = ChampWins / TotalGames * 100

    MinionsAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`MinionsKilled`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(int(championStats['key']),))
    MinionsAvg = cursor.fetchall()

    DmgTakenAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgTaken`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(int(championStats['key']),))
    DmgTakenAvg = cursor.fetchall()

    TotalGoldAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`TotalGold`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(int(championStats['key']),))
    TotalGoldAvg = cursor.fetchall()

    DmgDealtAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgDealt`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s GROUP by `MatchTbl`.`RankFk`",(int(championStats['key']),))
    DmgDealtAvg = cursor.fetchall()

    commonItems = cursor.execute("SELECT item1, COUNT(item1) ,item2 , COUNT(item2) ,item3 , COUNT(item3) ,item4 , COUNT(item4),item5 , COUNT(item5),item6 , COUNT(item6) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk =% s GROUP BY item2 ORDER BY `COUNT(item2)` DESC LIMIT 1",(int(championStats['key']),))
    commonItems = cursor.fetchall()
    Items = getItemDescriptions(commonItems)
    Rank = []

    bestItems = cursor.execute("SELECT item1, COUNT(item1) ,item2 , COUNT(item2) ,item3 , COUNT(item3) ,item4 , COUNT(item4),item5 , COUNT(item5),item6 , COUNT(item6) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s AND win = 1 GROUP BY item2 ORDER BY `COUNT(item2)` DESC LIMIT 1 ",(int(championStats['key']),))
    bestItems = cursor.fetchall()
    bestItems = getItemDescriptions(bestItems)

    Runes = cursor.execute("SELECT PrimaryKeyStone, COUNT(PrimaryKeyStone), PrimarySlot1 , COUNT(PrimarySlot1) ,PrimarySlot2 , COUNT(PrimarySlot2) ,PrimarySlot3 , COUNT(PrimarySlot3) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY PrimaryKeyStone ORDER BY PrimaryKeyStone DESC LIMIT 1 ",(int(championStats['key']),))
    Runes = cursor.fetchall()
    runes = getRunesImages(Runes)

    kda = cursor.execute("SELECT AVG(kills), AVG(deaths), AVG(assists) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s",(int(championStats['key']),))
    kda = cursor.fetchall()
    print(kda[0][1])

    position = cursor.execute("SELECT Lane, COUNT(Lane) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s", (int(championStats['key']),))
    position = cursor.fetchone()
    position = position[0]
    position = Normalise(position)


    bestRunes = cursor.execute("SELECT PrimaryKeyStone, COUNT(PrimaryKeyStone), PrimarySlot1 , COUNT(PrimarySlot1) ,PrimarySlot2 , COUNT(PrimarySlot2) ,PrimarySlot3 , COUNT(PrimarySlot3) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId AND Win = 1 WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY PrimaryKeyStone ORDER BY PrimaryKeyStone DESC LIMIT 1",(int(championStats['key']),))
    bestRunes = cursor.fetchall()
    bestRunes = getRunesImages(bestRunes)

    SecondRunes =  cursor.execute("SELECT SecondarySlot1, COUNT(SecondarySlot1), SecondarySlot2 , COUNT(SecondarySlot2) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s GROUP BY SecondarySlot1 ORDER BY `COUNT(SecondarySlot1)` DESC LIMIT 1",(int(championStats['key']),))
    SecondRunes = cursor.fetchall()
    SecondRunes = getRunesImages(SecondRunes)
    
    bestSecondRunes = cursor.execute("SELECT SecondarySlot1, COUNT(SecondarySlot1), SecondarySlot2 , COUNT(SecondarySlot2) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s AND Win = 1 GROUP BY SecondarySlot1 ORDER BY `COUNT(SecondarySlot1)` DESC LIMIT 1",(int(championStats['key']),))
    bestSecondRunes = cursor.fetchall()
    bestSecondRunes = getRunesImages(bestSecondRunes)


    AvgMinionsRanked = []
    AvgDmgTakenRanked = []
    AvgDmgDealtRanked = []
    TotalGoldAvgRanked = []

    for data in MinionsAvg:
        Rank.append(data[0])
 
    TableInit(MinionsAvg, AvgMinionsRanked)
    TableInit(DmgTakenAvg, AvgDmgTakenRanked)
    TableInit(TotalGoldAvg, TotalGoldAvgRanked)
    TableInit(DmgDealtAvg, AvgDmgDealtRanked)


    return render_template('championData.html',championStats = championStats, 
                            ChampionAbilities = ChampionAbilities,wins = Normalise(ChampWins),totalGames = Normalise(TotalGames),
                            champKills = Normalise(ChampKills),
                            AvgMinions = AvgMinionsRanked,
                            Rank = Rank, 
                            position = position,#winRate = winRate,
                            TotalGoldAvg = TotalGoldAvgRanked,
                            DmgDealtAvg = AvgDmgDealtRanked,
                            DmgTakenAvg = AvgDmgTakenRanked, commonItems = Items,
                            runes = runes, SecondRunes = SecondRunes, BestRunes = bestRunes, BestSecondRunes = bestSecondRunes, bestItems = bestItems, kda = kda)

def TableInit(arr,arr2):
    for data in arr:
        arr2.append(data[1])

@app.route('/summoner/champion' , methods=['GET','POST'])
def SummonerChampionStats():
    connection = create_connection()
    cursor =  connection.cursor()
    SummonerName = request.args.get('summoner')
    champName = request.args.get('champion')
    championStats = getChampDetails(champName)
    
    ChampionAbilities = getChampAbilities(championStats)
    getChampSpellImages(ChampionAbilities)


    SummonerFk = cursor.execute("SELECT SummonerTbl.SummonerId from SummonerTbl where SummonerName = % s", (SummonerName, ))
    SummonerFk = cursor.fetchall()

    SummonerFk = SummonerFk[0]['SummonerId']

    TotalGames = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s", (int(championStats['key']), int(SummonerFk)))
    TotalGames = cursor.fetchall()

    ChampWins = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `MatchStatsTbl`.Win = 1 and `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s", (int(championStats['key']), int(SummonerFk)))
    ChampWins = cursor.fetchall()

    ChampKills = cursor.execute("SELECT SUM(`MatchStatsTbl`.kills) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s", (int(championStats['key']), int(SummonerFk)))
    ChampKills = cursor.fetchall()

    ChampWins = ChampWins[0]['COUNT(`MatchStatsTbl`.Win)']
    ChampKills = str(ChampKills[0]['SUM(`MatchStatsTbl`.kills)'])
    TotalGames = str(TotalGames[0]['COUNT(`MatchStatsTbl`.Win)'])


    #winRate = ChampWins / TotalGames * 100

    MinionsAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`MinionsKilled`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s  and SummonerMatchTbl.SummonerFk = % s GROUP by `MatchTbl`.`RankFk", (int(championStats['key']), int(SummonerFk)))
    MinionsAvg = cursor.fetchall()

    DmgTakenAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgTaken`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s  GROUP by `MatchTbl`.`RankFk`", (int(championStats['key']), int(SummonerFk)))
    DmgTakenAvg = cursor.fetchall()

    TotalGoldAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`TotalGold`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s and SummonerMatchTbl.SummonerFk = % s  GROUP by `MatchTbl`.`RankFk`", (int(championStats['key']), int(SummonerFk)))
    TotalGoldAvg = cursor.fetchall()

    DmgDealtAvg = cursor.execute("SELECT `RankTbl`.`Rank` , AVG(`MatchStatsTbl`.`DmgDealt`) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` JOIN `RankTbl` on `RankTbl`.`RankId` = `MatchTbl`.`RankFk` WHERE `MatchTbl`.QueueType = 'CLASSIC' AND `SummonerMatchTbl`.`ChampionFk` = % s  and SummonerMatchTbl.SummonerFk = % s  GROUP by `MatchTbl`.`RankFk`", (int(championStats['key']), int(SummonerFk)))
    DmgDealtAvg = cursor.fetchall()

    position = cursor.execute("SELECT Lane, COUNT(Lane) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s and SummonerMatchTbl.SummonerFk = % s GROUP BY Lane ORDER BY PrimaryKeyStone DESC ", (int(championStats['key']), int(SummonerFk)))
    position = cursor.fetchone()
    position = position
   
    position = Normalise(position)

    kda = cursor.execute("SELECT AVG(kills), AVG(deaths), AVG(assists) FROM MatchStatsTbl JOIN SummonerMatchTbl on SummonerMatchFk = SummonerMatchTbl.SummonerMatchId WHERE SummonerMatchTbl.ChampionFk = % s and SummonerMatchTbl.SummonerFk = % s", (int(championStats['key']), int(SummonerFk)))
    kda = cursor.fetchall()
  

    AvgMinionsRanked = []
    AvgDmgTakenRanked = []
    AvgDmgDealtRanked = []
    TotalGoldAvgRanked = []
    Rank = []

    for data in MinionsAvg:
        Rank.append(data[0])
 
    TableInit(MinionsAvg, AvgMinionsRanked)
    TableInit(DmgTakenAvg, AvgDmgTakenRanked)
    TableInit(TotalGoldAvg, TotalGoldAvgRanked)
    TableInit(DmgDealtAvg, AvgDmgDealtRanked)


    return render_template('summonerChampion.html',championStats = championStats, 
                            ChampionAbilities = ChampionAbilities,wins = Normalise(ChampWins),totalGames = Normalise(TotalGames),
                            champKills = Normalise(ChampKills),
                            AvgMinions = AvgMinionsRanked,
                            position = position,#winRate = winRate,
                            Rank = Rank,
                            TotalGoldAvg = TotalGoldAvgRanked,
                            DmgDealtAvg = AvgDmgDealtRanked,
                            DmgTakenAvg = AvgDmgTakenRanked,
                            kda = kda)



@app.route('/post_json',methods=['POST','GET'])
def predict():
    connection = create_connection()
    cursor =  connection.cursor()
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
     
        data = json.loads(request.data)    
       
        rf = randomForest.randomForestRun()
        rf = randomForest.randomForestPredict(rf,data['ChampionFk'],data['MinionsKilled'],data['kills'],data['deaths'],data['assists'],data['lane'], data['masteryPoints'],
                                            data['DmgDealt'],data['DmgTaken'],data['TurretDmgDealt'],data['TotalGold'],data['EnemyChampionFk'],
                                            data['GameDuration'],data['DragonKills'],data['BaronKills'])
        Prediction = {
            "pred": str(rf)
        }
        print(Prediction)

        return jsonify(Prediction), 200
    else:
        return "Content type is not supported."

    
@app.route('/matchPredict', methods = ['GET','POST'])
def matchPredict():
    connection = create_connection()
    cursor =  connection.cursor()
    champ = cursor.execute("SELECT * FROM `ChampionTbl`")
    champ = cursor.fetchall()

    RoleImages = getRoles()

    #Velkoz
    #Dr. Mundo == DrMundo
    return render_template('matchPrediction.html', Champions = champ, RoleSelect = RoleImages)
    

@app.route('/summData', methods = ['GET'])
def summData():
    summonerName = request.args.get('summoner')
    Region = request.args.get('region')
    champ = request.args.get('champ')
    enemyChamp = request.args.get('enemyChamp')
    lane = request.args.get('lane')
    SummonerInfo = getSummonerDetails(Region,summonerName)
    SummId = SummonerInfo['id']
    data = getMatchData(Region, SummId, SummonerInfo)
    mastery = getMasteryStats(Region, SummId)
    mastery = getSingleMasteryScore(champ, mastery)
    avg = AvgStats(data)
    avg['ChampId'] = champ
    avg['masteryPoints'] = mastery
    avg['enemyChamp'] = enemyChamp
    avg['lane'] = lane
    print(avg)
    return jsonify(avg), 200


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()