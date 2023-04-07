import mysql.connector
import sys
import pytest
import requests

sys.path.append('../..')
from config import *
from RiotApiCalls import *
# Basic packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
 
# Sklearn modules & classes
from sklearn.linear_model import Perceptron, LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import datasets
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay, classification_report
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, log_loss
import sklearn.metrics
from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt

def connection():
    connection = mysql.connector.connect(host=host,
                                        database= sql_user,
                                        user=sql_user,
                                        password=sql_password)
    return connection

def runSVM():
    conn = connection()
    cursor = conn.cursor()

    query = ("SELECT `SummonerMatchTbl`.ChampionFk, `MatchStatsTbl`.`MinionsKilled`,`MatchStatsTbl`.`kills`,`MatchStatsTbl`.`deaths`,`MatchStatsTbl`.`assists`,`MatchStatsTbl`.Lane,  `MatchStatsTbl`.CurrentMasteryPoints, `MatchStatsTbl`.`DmgDealt`,`MatchStatsTbl`.`DmgTaken`,`MatchStatsTbl`.`TurretDmgDealt`,`MatchStatsTbl`.`TotalGold`,`MatchStatsTbl`.EnemyChampionFk,  `MatchTbl`.`GameDuration`,`MatchStatsTbl`.`DragonKills`,`MatchStatsTbl`.`BaronKills` ,`MatchStatsTbl`.`Win` FROM `SummonerMatchTbl` JOIN `MatchStatsTbl`ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk` WHERE `MatchTbl`.`QueueType` = 'CLASSIC';")
    cursor.execute(query)
    data = cursor.fetchall()

    columns = ['ChampionFk', 'MinionsKilled','kills','deaths','assists','lane','CurrentMasteryPoints','DmgDealt','DmgTaken','TurretDmgDealt','TotalGold'
        ,'EnemyChampionFk', 'GameDuration','DragonKills','BaronKills','Win']

    #data = pd.read_csv("data.csv")
    df_games = pd.DataFrame(data,columns = columns)
    df_games.sample(frac=1)


    df_games['lane'] = df_games['lane'].map({'TOP':0,'JUNGLE':1,'MIDDLE':2,'BOTTOM':3,'SUPPORT':4,'NONE':5})
    df_games['Win'] = df_games['Win']
    X = df_games.drop('Win', axis=1)
    y = df_games['Win']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.115)

    sc = StandardScaler()
    sc.fit(X_train)
    X_train_std = sc.transform(X_train)
    X_test_std = sc.transform(X_test)

    # Instantiate the Support Vector Classifier (SVC)
    svc = SVC(probability=True)
    
    # Fit the model
    svc.fit(X_train_std, y_train)

    # Make the predictions
    y_predict = svc.predict(X_test_std)
    
    # Measure the performance
    print(classification_report(y_test, y_predict))

    clf_probs = svc.predict_proba(X_test)
    score = log_loss(y_test, clf_probs)
    print("Log Loss", score)
    mse = mean_squared_error(y_test, y_predict)
    print("MSE: ", mse)
   

def getPlotScore(model, X_test, y_test):
    svc_disp = RocCurveDisplay.from_estimator(model, X_test, y_test)
    return svc_disp

runSVM()