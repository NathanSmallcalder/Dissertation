from sklearn.ensemble import GradientBoostingClassifier
import mysql.connector
import sys
import pytest
import requests

sys.path.append('../..')
from config import *
from RiotApiCalls import *
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay, classification_report
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, log_loss
from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt
connection = mysql.connector.connect(host=host,
                                     database= sql_user,
                                     user=sql_user,
                                     password=sql_password)
def gradientBoostRun():
    query = ("SELECT `SummonerMatchTbl`.ChampionFk, `MatchStatsTbl`.`MinionsKilled`,`MatchStatsTbl`.Lane,`MatchStatsTbl`.`DmgDealt`,`MatchStatsTbl`.`DmgTaken`,`MatchStatsTbl`.`TurretDmgDealt`,`MatchStatsTbl`.`TotalGold`,`MatchStatsTbl`.EnemyChampionFk,  `MatchTbl`.`GameDuration`,`MatchStatsTbl`.`DragonKills`,`MatchStatsTbl`.`BaronKills` ,`MatchStatsTbl`.`Win` FROM `SummonerMatchTbl` JOIN `MatchStatsTbl`ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk` WHERE `MatchTbl`.`QueueType` = 'CLASSIC';")
    cursor = connection.cursor()

    cursor.execute(query)
    data = cursor.fetchall()

    columns = ['ChampionFk', 'MinionsKilled','lane','DmgDealt','DmgTaken','TurretDmgDealt','TotalGold'
    ,'EnemyChampionFk', 'GameDuration','DragonKills','BaronKills','Win']

    #data = pd.read_csv("data.csv")
    df_games = pd.DataFrame(data,columns = columns)
    df_games.sample(frac=1)



    df_games['lane'] = df_games['lane'].map({'TOP':0,'JUNGLE':1,'MIDDLE':2,'BOTTOM':3,'NONE':4})
    df_games['Win'] = df_games['Win']
    df_games = df_games.fillna(0)
    X = df_games.drop('Win', axis=1)
    y = df_games['Win']


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)


    model = GradientBoostingClassifier(learning_rate=0.20)
    model.fit(X,y)
    y_pred = model.predict(X_test)

    print(classification_report(y_test, y_pred))
    clf_probs = model.predict_proba(X_test)
    getPlotScore(model, X_test, y_test)
    score = log_loss(y_test, clf_probs)
    print("Log Loss", score)
    mse = mean_squared_error(y_test, y_pred)
    print("MSE: ", mse)
    return svc_disp

def getPlotScore(model, X_test, y_test):
    svc_disp = RocCurveDisplay.from_estimator(model, X_test, y_test)
    print("eee")
    print(svc_disp)
    return svc_disp