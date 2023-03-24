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


warnings.filterwarnings('ignore')

app = Flask(__name__)

#Config
app.config['SECRET_KEY'] = 'key'
app.config['MYSQL_HOST'] = host 
app.config['MYSQL_USER'] = sql_user
app.config['MYSQL_PASSWORD'] = sql_password
app.config['MYSQL_DB'] = 'o1gbu42_StatTracker'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#Summoner Routing
@app.route('/summoner',methods=['GET','POST'])
def getSummoner():
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
    SummonerName = request.args.get('summoner')
    Region = request.args.get('region')
    Summoners = summonerInGameCheck(Region,SummonerName)
    return render_template('summonerInGame.html', Summoners = Summoners)

#Champion Stats - From Database
@app.route('/champions', methods=['GET','POST'])
def ChampionTablePage():
    data = getChampionAverages()
    players = getBestPlayers()
    print(data)

    #columns = ['ChampionFk', 'kills', 'deaths','assists', 'Win', 'GameDuration']
    
    return render_template('champions.html',data=  data,players = players)


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
    AvgGold = avgGold(int(championStats['key']))

    BestItems = bestItems(int(championStats['key']))
    CommonItems = commonItems(int(championStats['key']))

    CommonRunes = commonRunes(int(championStats['key']))
    BestRunes = bestRunes(int(championStats['key']))

    SecondaryCommonRunes = commonSecondaryRunes((int(championStats['key'])))
    SecondaryBestRunes = bestSecondaryRunes((int(championStats['key'])))
    position = laneFromDatabase(int(championStats['key']))
    kda = kdaFromDatabase(int(championStats['key']))
   

    
    Rank = []
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
                            BestItems = BestItems, kda = kda,DmgDealtAvg = DmgDealtAvg
                            , AvgMinions = AvgMinions, DmgTakenAvg = DmgTakenAvg, AvgGold = AvgGold)

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
    
        return jsonify(Prediction), 200
    else:
        return "Content type is not supported."

    
@app.route('/matchPredict', methods = ['GET','POST'])
def matchPredict():
    champ = getAllChampions()
    RoleImages = getRoles()
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
    data = getMatchData5Matches(Region, SummId, SummonerInfo)
    mastery = getMasteryStats(Region, SummId)
    mastery = getSingleMasteryScore(champ, mastery)
    avg = AvgStats(data)
    avg['ChampId'] = champ
    avg['masteryPoints'] = mastery
    avg['enemyChamp'] = enemyChamp
    avg['lane'] = lane

    return jsonify(avg), 200

@app.route('/teamPredict',methods = ['GET'])
def teamPredictor():
    RoleImages = getRoles()
    champ = getAllChampions()
    return render_template('teamMatchPrediction.html', RoleImages = RoleImages, Champions = champ)

@app.route('/teamData', methods = ['GET','POST'])
def teamData():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = json.loads(request.data)    
        Region = data['Region']
        print(data)
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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()