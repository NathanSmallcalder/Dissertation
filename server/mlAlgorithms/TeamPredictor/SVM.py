import mysql.connector
import sys
import requests

sys.path.append('../..')
from config import *

# Data Processing
import pandas as pd
import numpy as np

# Sklearn modules & classes
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.datasets import make_regression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay, classification_report
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor
from sklearn.metrics import mean_squared_error, log_loss

def connection():
    connection = mysql.connector.connect(host=host,
                                        database= sql_user,
                                        user=sql_user,
                                        password=sql_password)
    return connection

global rf

def SVMRun():
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
    b = pd.DataFrame(df_games['BlueWin'],columns = ['BlueWin'] )
    
    y['RedWin'] = df_games['RedWin']
    b['BlueWin'] = df_games['BlueWin']
 
    df_games = df_games.drop('RedWin',axis=1)
    df_games = df_games.drop('BlueWin',axis=1)
    X = df_games

    X, y = make_regression(n_samples=1000, n_features=20, n_informative=5, n_targets=2, random_state=1, noise=0.5)

    model = MultiOutputRegressor(SVC(probability=True))
    model.fit(X, y)

    clf_probs = svc.predict_proba(X_test)
    print(clf_probs)

    #score = log_loss(y_test, clf_probs)
    #print("Log Loss", score)
    item = {
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
    row = [[item['B1'],item['B2'],item['B3'],item['B4'],item['B5'],
            item['R1'],item['R2'],item['R3'],item['R4'],item['R5'],
            item['BlueBaronKills'],item['BlueRiftHeraldKills'],item['BlueDragonKills'],
            item['BlueTowerKills'],item['BlueKills'],
            item['RedBaronKills'],item['RedRiftHeraldKills'],item['RedDragonKills'],
            item['RedTowerKills'],item['RedKills'],
            ]]

    yhat = model.predict(row)
    print(yhat)

SVMRun()