import mysql.connector
import sys
import requests

sys.path.append('../..')
from config import *

# Data Processing
import pandas as pd
import numpy as np

# Modelling
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay, classification_report
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, log_loss



def connection():
    connection = mysql.connector.connect(host=host,
                                        database= sql_user,
                                        user=sql_user,
                                        password=sql_password)
    return connection

global rf

def randomForestMultiRun():
    conn = connection()
    query = ("SELECT * FROM `TeamMatchTbl`")
    cursor = conn.cursor()

    cursor.execute(query)
    data = cursor.fetchall()
    
    columns = ['TeamId', 'MatchFk','B1','B2','B3','B4','B5',
    'R1','R2','R3','R4','R5',
    'BlueBaronKills', 'BlueRiftHeraldKills','BlueDragonKills',
    'BlueTowerKills','BlueKills',
    'RedBaronKills', 'RedRiftHeraldKills','RedDragonKills',
    'RedTowerKills','RedKills',
    'RedWin','BlueWin']

    df_games = pd.DataFrame(data,columns = columns)
    df_games.sample(frac=1)

    df_games = df_games.drop('MatchFk',axis=1)
    df_games = df_games.drop('TeamId',axis=1)
    
    y = pd.DataFrame(df_games['RedWin'],columns = ['RedWin','BlueWin'] )
    y['RedWin'] = df_games['RedWin']
    y['BlueWin'] = df_games['BlueWin']
 
    df_games = df_games.drop('RedWin',axis=1)
    df_games = df_games.drop('BlueWin',axis=1)
    X = df_games

    X_train, X_test, y_train, y_test = train_test_split(X.values, y.values, test_size=0.15)
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    print(classification_report(y_test, y_pred))

    clf_probs = rf.predict_proba(X_test)
    print(clf_probs[0][0])
    #score = log_loss(y_test, clf_probs)
    predictRed = []


    mse = mean_squared_error(y_test, y_pred)
    print(mse)
    return rf
    # B1,B2,B3,B4,B5,R1,R2,R3,R4,R5,B-Baron,B-Rift,B-Dragon,BTowerKills,BlueKills,RedBaron,R-Rift,R-Dragon,RTowerKills,RedKills
          #<==============><===========>


def randomForestPredictMulti(rf, item):
    print(item)
    row = [[item['B1'],item['B2'],item['B3'],item['B4'],item['B5'],
            item['R1'],item['R2'],item['R3'],item['R4'],item['R5'],
            item['BlueBaronKills'],item['BlueRiftHeraldKills'],item['BlueDragonKills'],
            item['BlueTowerKills'],item['BlueKills'],
            item['RedBaronKills'],item['RedRiftHeraldKills'],item['RedDragonKills'],
            item['RedTowerKills'],item['RedKills'],
            ]]

    print(row)
    prob = rf.predict_proba(row)
    yhat = rf.predict(row)
    print('Prediction:', "Red Team:" ,yhat[0][0] ," Blue Team:", yhat[0][1])
    prediction = {
        "RedTeam":yhat[0][0],
        "BlueTeam":yhat[0][1]
    }
    return prediction


rf = randomForestMultiRun()
dataset = {
        "B1": 44,
        "B2": 876,
        "B3": 136,
        "B4": 221,
        "B5": 74,
        "R1": 122,
        "R2": 20,
        "R3": 99,
        "R4": 202,
        "R5": 412,
        "BlueBaronKills": 1,
        "BlueRiftHeraldKills":2 ,
        "BlueDragonKills": 2.33,
        "BlueTowerKills": 9,
        "BlueKills": 37,

        "RedBaronKills": 0.3333,
        "RedRiftHeraldKills": 0,
        "RedDragonKills": 0,
        "RedTowerKills": 0,
        "RedKills":0,
}
randomForestPredictMulti(rf, dataset)