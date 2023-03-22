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
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor

def connection():
    connection = mysql.connector.connect(host=host,
                                        database= sql_user,
                                        user=sql_user,
                                        password=sql_password)
    return connection

def GradientBoostRun():
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

    X_train, X_test, y_train, y_test = train_test_split(X.values, y.values, test_size=0.25)
    rf = MultiOutputClassifier(GradientBoostingClassifier())
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    print(classification_report(y_test, y_pred))
    
    mse = mean_squared_error(y_test, y_pred)
    print(mse)
    return rf

GradientBoostRun()