from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import secrets
from config import *
from RiotApiCalls import *
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import warnings
from championsRequest import *

warnings.filterwarnings('ignore')

app = Flask(__name__)
key = secrets.token_urlsafe(16)
key = secrets.token_hex(16)

app.config['SECRET_KEY'] = 'key'
app.config['MYSQL_HOST'] = host 
app.config['MYSQL_USER'] = sql_user
app.config['MYSQL_PASSWORD'] = sql_password
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def create_connection():
    return pymysql.connect(
        host=host,
        db='o1gbu42_StatTracker',
        user=sql_user,
        password=sql_password,
        cursorclass=pymysql.cursors.DictCursor
    )

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
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password'  in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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

@app.route('/summoner/in-game',methods=['GET','POST'])
def SummonerInGame():
    SummonerName = request.args.get('summoner')
    Region = request.args.get('region')
    Summoners = summonerInGameCheck(Region,SummonerName)
    return render_template('summonerInGame.html', Summoners = Summoners)

@app.route('/champions', methods=['GET','POST'])
def ChampionTablePage():
    query = ('SELECT `ChampionTbl`.`ChampionName`, AVG(`MatchStatsTbl`.`kills`),AVG(`MatchStatsTbl`.`deaths`),AVG(`MatchStatsTbl`.`assists`), AVG(`MatchStatsTbl`.`Win`), AVG(`MatchTbl`.`GameDuration`) FROM `SummonerMatchTbl`   JOIN `MatchStatsTbl` ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId   JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk`  JOIN `ChampionTbl` ON  `SummonerMatchTbl`.`ChampionFk` = `ChampionTbl`.`ChampionId`   WHERE `MatchTbl`.`QueueType` = "CLASSIC"  GROUP BY `ChampionTbl`.`ChampionId`;')
    cursor.execute(query)
    data = cursor.fetchall()

  
    #columns = ['ChampionFk', 'kills', 'deaths','assists', 'Win', 'GameDuration']
    
    return render_template('champions.html',data=  data)


#InDepth Champion Stats
@app.route('/champion' , methods=['GET','POST'])
def championData():
    champName = request.args.get('Champion')
    championStats = getChampDetails(champName)
    print(championStats)
    ChampionAbilities = getChampAbilities(championStats)
    print(ChampionAbilities)
    getChampSpellImages(ChampionAbilities)

    TotalGames = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s", (int(championStats['key']), ))
    TotalGames = cursor.fetchall()

    ChampWins = cursor.execute("SELECT COUNT(`MatchStatsTbl`.Win) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `MatchStatsTbl`.Win = 1 and `SummonerMatchTbl`.`ChampionFk` = % s", (int(championStats['key']), ))
    ChampWins = cursor.fetchall()

    ChampKills = cursor.execute("SELECT SUM(`MatchStatsTbl`.kills) FROM `MatchStatsTbl` JOIN `SummonerMatchTbl` on `MatchStatsTbl`.MatchStatsId = `SummonerMatchTbl`.`SummonerMatchId` JOIN `MatchTbl` on `SummonerMatchTbl`.`MatchFk` = `MatchTbl`.`MatchId` WHERE `SummonerMatchTbl`.`ChampionFk` = % s", (int(championStats['key']), ))
    ChampKills = cursor.fetchall()
    
    return render_template('championData.html',championStats = championStats, ChampionAbilities = ChampionAbilities,wins = ChampWins,totalGames = TotalGames,champKills = ChampKills)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(ssl_context='adhoc')