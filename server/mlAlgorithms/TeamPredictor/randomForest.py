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
import seaborn as sns
import matplotlib.pyplot as plt

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
    print(df_games.head())
    df_games = df_games.drop('MatchFk',axis=1)
    df_games = df_games.drop('TeamId',axis=1)
    
    y = pd.DataFrame(df_games['RedWin'],columns = ['RedWin','BlueWin'] )
    y['RedWin'] = df_games['RedWin']
    y['BlueWin'] = df_games['BlueWin']
 
    df_games = df_games.drop('RedWin',axis=1)
    df_games = df_games.drop('BlueWin',axis=1)
    X = df_games
    print(X.head())

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
    corr_matrix =  X.corr()
    print(corr_matrix)

    plt.figure(figsize=(16,14))
    plt.title('Correlation Heatmap of riot Dataset')
    a = sns.heatmap(corr_matrix, square=True, annot=True, fmt='.2f', linecolor='black')
    a.set_xticklabels(a.get_xticklabels(), rotation=30)
    a.set_yticklabels(a.get_yticklabels(), rotation=30)           
    plt.savefig("figure.png")

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

randomForestMultiRun()