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
from mlAlgorithms import *
sys.path.append('mlAlgorithms')
from SoloPredictor import randomForestSolo
from TeamPredictor import randomForest
from databaseQuries import *


stri = "https://5000-nathansmall-dissertatio-8z3sdftfozh.ws-eu84.gitpod.io/summoner?summoner=Mealsz&region=EUW1"
s = stri.split('/s', 1)[0]

warnings.filterwarnings('ignore')

app = Flask(__name__)

#Config For Database
app.config['SECRET_KEY'] = 'key'
app.config['MYSQL_HOST'] = host 
app.config['MYSQL_USER'] = sql_user
app.config['MYSQL_PASSWORD'] = sql_password
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

#Summoner Routing for Summoner Stats Page
@app.route('/summoner',methods=['GET','POST'])
def getSummoner():
    #Gets Region, SummonerName
    summonerName = request.args.get('summoner')
    Region = request.args.get('region')
    #Gets basic Summoner Information
    SummonerInfo = getSummonerDetails(Region,summonerName)
    SummId = SummonerInfo['id']
    #Ranked Stats
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

    #Profile Image
    getImageLink(SummonerInfo)
    #Mastery Score
    masteryScore = getMasteryStats(Region,SummId)

    #Gets Matches
    data = getMatchData(Region, SummId, SummonerInfo)
    participants = getGameParticipantsList()
    MeanData = getMatchTimeline(Region, SummId, SummonerInfo['puuid'],data)
    fullMatch = getPlayerMatchData()

    #Gets Statistics from Database (Graphs)
    summIdDatabase = getSummonerIdFromDatabase(summonerName)
    avgMinionsStatsSummoner = avgMinionsSummonerAll(summIdDatabase)
    avgMinions = avgMinionsAll()
    avgDamageTaken = avgDmgTakenAll()
    avgDamageTakenStatsSummoner = avgDmgTakenSummonerAll(summIdDatabase)
    avgDamageDealt = avgDmgDealtAll()
    avgDamageDealtStatsSummoner = avgDmgDealtSummonerAll(summIdDatabase)
    avgGoldEarnt = avgGoldAll()
    avgGoldEarntSummoner = avgGoldSummonerAll(summIdDatabase)


    #Returns HTML and Variables
    return render_template('summonerPage.html', SummonerInfo = SummonerInfo,
    soloRanked = SOLO,flexRanked = FLEX,masteryScore = masteryScore,data=data, 
    MeanData = MeanData, fullMatch = fullMatch,participants = participants,summonerName = summonerName,Region = Region,
    avgMinionsStatsSummoner = avgMinionsStatsSummoner, AvgMinions = avgMinions,
    avgDamageTaken = avgDamageTaken, avgDamageTakenStatsSummoner = avgDamageTakenStatsSummoner,
    DmgDealtAvg = avgDamageDealt, avgDamageDealtStatsSummoner = avgDamageDealtStatsSummoner,
    AvgGold = avgGoldEarnt, avgGoldEarntSummoner = avgGoldEarntSummoner)

### Summoner in Game Screen
@app.route('/summoner/in-game',methods=['GET','POST'])
def SummonerInGame():
    #Gets Summoner and Region
    SummonerName = request.args.get('summoner')
    Region = request.args.get('region')
    #Checks if summoner in game
    Summoners = summonerInGameCheck(Region,SummonerName)
    return render_template('summonerInGame.html', Summoners = Summoners)

#Champion Stats - From Database
@app.route('/champions', methods=['GET','POST'])
def ChampionTablePage():
    #Gets Champion Win,KDA,Dragon/Baron AVG for table
    data = getChampionAverages()
    #Gets Players Win,KDA,Dragon/Baron AVG for table
    players = getBestPlayers()
    print(players)
    return render_template('champions.html',data=  data,players = players)


### InDepth Champion Stats
@app.route('/champion' , methods=['GET','POST'])
def championData():
    #Gets champion name
    champName = request.args.get('champion')

    #Gets Champion Abilities and Videos
    championStats = getChampDetails(champName)
    ChampionAbilities = getChampAbilities(championStats)
    getChampSpellImages(ChampionAbilities)

    #Champion stats
    TotalGames = totalGames(int(championStats['key']))
    ChampWins = champWins(int(championStats['key']))
    ChampKills = champKills(int(championStats['key']))
    #winRate = ChampWins / TotalGames * 100
    AvgMinions = avgMinions(int(championStats['key']))
    DmgTakenAvg = avgDmgTaken(int(championStats['key']))
    DmgDealtAvg = avgDmgDealt(int(championStats['key']))
    AvgGold = avgGold(int(championStats['key']))
    BestItems = bestItems(int(championStats['key']))
    CommonItems = commonItems(int(championStats['key']))
    CommonRunes = commonRunes(int(championStats['key']))
    BestRunes = bestRunes(int(championStats['key']))
    SecondaryCommonRunes = commonSecondaryRunes((int(championStats['key'])))
    SecondaryBestRunes = bestSecondaryRunes((int(championStats['key'])))
    position = laneFromDatabase(int(championStats['key']))
    kda = kdaFromDatabase(int(championStats['key']))
   
    bestPlayers = getChampionBestPlayers(int(championStats['key']))

    return render_template('championData.html',championStats = championStats, 
                            ChampionAbilities = ChampionAbilities,wins = ChampWins,
                            totalGames = TotalGames,
                            champKills = ChampKills,
                            position = position,#winRate = winRate,
                            CommonItems = CommonItems,
                            runes = CommonRunes, SecondRunes = SecondaryCommonRunes, 
                            BestRunes = BestRunes, BestSecondRunes = SecondaryBestRunes, 
                            BestItems = BestItems, kda = kda,DmgDealtAvg = DmgDealtAvg
                            , AvgMinions = AvgMinions, DmgTakenAvg = DmgTakenAvg, AvgGold = AvgGold,bestPlayer = bestPlayers)

### Routing for Summoner/champion?summoner=<name>&champion=<championName>
### Searches Database for matches played on champion
### Returns html page
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
    AvgMinionsSumm = avgMinionsSummoner(int(championStats['key']),SummID)
    AvgDmgTakenSumm  = avgDmgTakenSummoner(int(championStats['key']), SummID)
    AvgDmgDealtSumm  = avgDmgDealtSummoner(int(championStats['key']), SummID)
    TotalGoldSumm = avgGoldSummoner(int(championStats['key']),SummID)
 
    position = laneFromDatabaseSummoner(int(championStats['key']), SummID)
    kda = kdaFromDatabaseSummoner(int(championStats['key']),SummID)
    championKills = champKills(SummID)

    AvgMinions = avgMinions(int(championStats['key']))
    DmgTakenAvg = avgDmgTaken(int(championStats['key']))
    DmgDealtAvg = avgDmgDealt(int(championStats['key']))
    AvgGold = avgGold(int(championStats['key']))


    return render_template('summonerChampion.html',championStats = championStats, 
                            ChampionAbilities = ChampionAbilities,wins = ChampWins,totalGames = TotalGames,
                            championKills = championKills,
                            position = position,#winRate = winRate,
                            AvgMinionsSumm = AvgMinionsSumm,
                            TotalGoldSumm = TotalGoldSumm,
                            AvgDmgDealtSumm = AvgDmgDealtSumm,
                            AvgDmgTakenSumm = AvgDmgTakenSumm,
                            kda = kda)


### Directory for Match Prediction Solo
### Returns UI for the Solo Match Prediction Screen
@app.route('/matchPredict', methods = ['GET','POST'])
def matchPredict():
    champ = getAllChampions()
    RoleImages = getRoles()
    return render_template('matchPrediction.html', Champions = champ, RoleSelect = RoleImages)
    
### Routing for GET summonerData
### gets Summoner Data from last 5 games
### Converts to a JSON response, returned to the matchPredict endpoint, which sends to the PredictSolo endPoint for prediction
@app.route('/summData', methods = ['GET'])
def summData():
    summonerName = request.args.get('summoner')
    Region = request.args.get('region')
    champ = request.args.get('champ')
    enemyChamp = request.args.get('enemyChamp')
    lane = request.args.get('lane')
    SummonerInfo = getSummonerDetails(Region,summonerName)
    SummId = SummonerInfo['id']
    print(SummId)
    data = getMatchData5Matches(Region, SummId, SummonerInfo)
    ### Gets Mastery Stats
    mastery = getMasteryStats(Region, SummId)
    mastery = getSingleMasteryScore(champ, mastery)

    ### Find Avg Stats for previous games
    avg = AvgStats(data)
    ### Set Other Values for the Array
    avg['ChampId'] = champ
    avg['masteryPoints'] = mastery
    avg['enemyChamp'] = enemyChamp
    avg['lane'] = lane
    print(avg)

    return jsonify(avg), 200


### Routing for Match Predictor (SOLO)
### Expects a JSON request of 
###    json_data = { 
###     "MinionsKilled": 258,
###     "kills": 25,
###     "assists": 56,
###     "deaths": 1,
###     "TotalGold": 32355,
###     "DmgDealt": 422425,
###     "DmgTaken": 24567,
###     "DragonKills": 4,
###     "BaronKills": 3,
###     "GameDuration": 200,
###      "TurretDmgDealt": 4,
###      "ChampionFk": 1,
###      "masteryPoints": 42257,
###      "EnemyChampionFk":2 ,
###      "lane": 1
###      }
### Calls randomForest Predict and runs the data through the algorithm
### Returns Prediction JSON - Value 1 or 0
@app.route('/predictSolo',methods=['POST','GET'])
def predict():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
     
        data = json.loads(request.data)    

        rf = randomForestSolo.randomForestRun()
        rf = randomForestSolo.randomForestPredict(rf,data['ChampionFk'],data['MinionsKilled'],data['kills'],data['deaths'],data['assists'],data['lane'], data['masteryPoints'],
                                            data['DmgDealt'],data['DmgTaken'],data['TurretDmgDealt'],data['TotalGold'],data['EnemyChampionFk'],
                                            data['GameDuration'],data['DragonKills'],data['BaronKills'])
        Prediction = {
            "pred": str(rf)
        }
        print(Prediction)
        return jsonify(Prediction), 200
    else:
        return "Content type is not supported."


### Routing for the /teamPredict Endpoint
### Returns UI for teamPrediction
### Users can input variables for teams
@app.route('/teamPredict',methods = ['GET'])
def teamPredictor():
    RoleImages = getRoles()
    champ = getAllChampions()
    return render_template('teamMatchPrediction.html', RoleImages = RoleImages, Champions = champ)

### Routing Endpoint for Team Prediction
### Excpects the following JSON format
###   dataset = {
###        "B1Summ": "Mealsz",
###        "B2Summ": "Ehhhh",
###        "B3Summ": "Itwoznotmee",
###        "B4Summ": "Lil Nachty",
###        "B5Summ": "Forza Napøli ",
###        "R1Summ": "Primabel Ayuso",
###        "R2Summ": "NateNatilla",
###        "R3Summ": "sweet af",
###        "R4Summ": "Fedy9 ",
###        "R5Summ": "ChampagneCharlie ",
###        "B1": 44,
###        "B2": 876,
###        "B3": 136,
###        "B4": 221,
###        "B5": 74,
###        "R1": 122,
###        "R2": 20,
###        "R3": 99,
###        "R4": 202,
###        "R5": 412,
###        'Region':"EUW1"
###    }
### Converts Summoner names into desiered team (blue or red) 
### Runs both teams through calculateAvgTeamStats
### Makes the Dataset to be ran through the machine learning algorithm
### returns prediction json
###    {
###     'BlueTeam': x
###       'RedTeam': y 
###   }
@app.route('/teamData', methods = ['GET','POST'])
def teamData():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = json.loads(request.data)    
        Region = data['Region']
        BlueTeam = [str(data['B1Summ']),str(data['B2Summ']),str(data['B3Summ']),
                        str(data['B4Summ']),str(data['B5Summ'])]
        RedTeam = [str(data['R1Summ']),str(data['R2Summ']),str(data['R3Summ']),
                        str(data['R4Summ']),str(data['R5Summ'])]
    
        blueTeam = calculateAvgTeamStats(BlueTeam,Region)
        redTeam = calculateAvgTeamStats(RedTeam, Region)
        dataSet = makeDataSet(blueTeam,redTeam,data)
      
        rf = randomForest.randomForestMultiRun()
        prediction = randomForest.randomForestPredictMulti(rf,dataSet)
        print(prediction)
    return jsonify(prediction) ,200

### Routing for the Main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()