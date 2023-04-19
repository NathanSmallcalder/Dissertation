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
    y = pd.DataFrame(df_games['BlueWin'],columns = ['BlueWin'] )
    
    y['RedWin'] = df_games['RedWin'].astype('int')
    y['BlueWin'] = df_games['BlueWin'].astype('int')
    print(y)
    df_games = df_games.drop('RedWin',axis=1)
    df_games = df_games.drop('BlueWin',axis=1)
    X = df_games
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25,stratify=y)
    model = MultiOutputRegressor(SVC(probability=True))
    model.fit(X, y.astype(int))
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    print(classification_report(y_test, y_pred))
    
    mse = mean_squared_error(y_test, y_pred)
    print(mse)
SVMRun()