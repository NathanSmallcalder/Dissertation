from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from matplotlib import *
import sys
from pylab import *
import seaborn as sns
import mysql.connector
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay, classification_report
import sys
import pytest
import requests
from sklearn import model_selection
from sklearn.metrics import mean_squared_error, log_loss
from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt
import pandas

sys.path.append('../..')
from config import *
from RiotApiCalls import *

warnings.filterwarnings("ignore")

connection = mysql.connector.connect(host=host,
                                     database= sql_user,
                                     user=sql_user,
                                     password=sql_password)
def runxGboost():
    query = ("SELECT `SummonerMatchTbl`.ChampionFk, `MatchStatsTbl`.`MinionsKilled`,`MatchStatsTbl`.Lane,`MatchStatsTbl`.`DmgDealt`,`MatchStatsTbl`.`DmgTaken`,`MatchStatsTbl`.`TurretDmgDealt`,`MatchStatsTbl`.`TotalGold`,`MatchStatsTbl`.EnemyChampionFk,  `MatchTbl`.`GameDuration`,`MatchStatsTbl`.`DragonKills`,`MatchStatsTbl`.`BaronKills` ,`MatchStatsTbl`.`Win` FROM `SummonerMatchTbl` JOIN `MatchStatsTbl`ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk` WHERE `MatchTbl`.`QueueType` = 'CLASSIC';")
    cursor = connection.cursor()

    cursor.execute(query)
    data = cursor.fetchall()

    columns = ['ChampionFk', 'MinionsKilled','lane','DmgDealt','DmgTaken','TurretDmgDealt','TotalGold'
    ,'EnemyChampionFk', 'GameDuration','DragonKills','BaronKills','Win']

    #data = pd.read_csv("data.csv")
    df_games = pandas.DataFrame(data,columns = columns)
    df_games.sample(frac=1)

    df_games['lane'] = df_games['lane'].map({'TOP':0,'JUNGLE':1,'MIDDLE':2,'BOTTOM':3,'NONE':4})
    df_games['Win'] = df_games['Win']
    

    X = df_games.drop('Win', axis=1)
    y = df_games['Win']


    # split data into train and test sets
    seed = 7
    test_size = 0.25
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

    model = XGBClassifier()
    model.fit(X_train, y_train)


    y_pred = model.predict(X_test)
    predictions = [round(value) for value in y_pred]
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))
    print(classification_report(y_test, y_pred))
    getPlotScore(model,X_test,y_test)
    svc_disp = clf_probs = model.predict_proba(X_test)

    score = log_loss(y_test, clf_probs)
    print("Log Loss", score)
    mse = mean_squared_error(y_test, y_pred)
    print("MSE: ", mse)
    return svc_disp

def getPlotScore(model, X_test, y_test):
    svc_disp = RocCurveDisplay.from_estimator(model, X_test, y_test)
    print(svc_disp)
    return svc_disp

runxGboost()