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
import databaseQuries
import mlAlgorithms
from mlAlgorithms import randomForest
from databaseQuries import *

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
    print(data[0]['ItemImages'][0])
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
    champName = request.args.get('champion')
    championStats = getChampDetails(champName)
    ChampionAbilities = getChampAbilities(championStats)
    getChampSpellImages(ChampionAbilities)

    TotalGames = totalGames(int(championStats['key']))
    ChampWins = champWins(int(championStats['key']))
    ChampKills = champKills(int(championStats['key']))
    #winRate = ChampWins / TotalGames * 100
    AvgMinions = avgMinions(int(championStats['key']))

    DmgTakenAvg = avgDmgTaken(int(championStats['key']))
    DmgDealtAvg = avgDmgDealt(int(championStats['key']))

    BestItems = bestItems(int(championStats['key']))
    CommonItems = commonItems(int(championStats['key']))

    CommonRunes = commonRunes(int(championStats['key']))
    BestRunes = bestRunes(int(championStats['key']))

    SecondaryCommonRunes = commonSecondaryRunes((int(championStats['key'])))
    SecondaryBestRunes = bestSecondaryRunes((int(championStats['key'])))
    position = laneFromDatabase(int(championStats['key']))
    kda = kdaFromDatabase(int(championStats['key']))
   

    print(CommonRunes)
    
    Rank = []
    print(BestItems[0])
    for data in AvgMinions:
        Rank.append(data['Rank'])
 
    return render_template('championData.html',championStats = championStats, 
                            ChampionAbilities = ChampionAbilities,wins = ChampWins,
                            totalGames = TotalGames,
                            champKills = ChampKills,
                            Rank = Rank, 
                            position = position,#winRate = winRate,
                            CommonItems = CommonItems,
                            runes = CommonRunes, SecondRunes = SecondaryCommonRunes, 
                            BestRunes = BestRunes, BestSecondRunes = SecondaryBestRunes, 
                            BestItems = BestItems, kda = kda)

@app.route('/summoner/champion' , methods=['GET','POST'])
def SummonerChampionStats():
    SummonerName = request.args.get('summoner')
    champName = request.args.get('champion')

    championStats = getChampDetails(champName)
    ChampionAbilities = getChampAbilities(championStats)
    getChampSpellImages(ChampionAbilities)
    SummID =  getSummonerIdFromDatabase(SummonerName)
    TotalGames = totalGamesSummoner(int(championStats['key']), SummID)
    ChampWins = champWinsSummoner(int(championStats['key']),SummID)
    AvgMinions = avgMinionsSummoner(int(championStats['key']),SummID)
    AvgDmgTaken = avgDmgTakenSummoner(int(championStats['key']), SummID)
    AvgDmgDealt = avgDmgDealtSummoner(int(championStats['key']), SummID)
    TotalGold = avgGoldSummoner(int(championStats['key']),SummID)
    position = laneFromDatabaseSummoner(int(championStats['key']), SummID)
    kda = kdaFromDatabaseSummoner(int(championStats['key']),SummID)

    return render_template('summonerChampion.html',championStats = championStats, 
                            ChampionAbilities = ChampionAbilities,wins = ChampWins,totalGames = TotalGames,
                            champKills = ChampKills,
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
    print(champ)
   
   

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