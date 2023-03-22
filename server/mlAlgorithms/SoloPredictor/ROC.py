from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt
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
from xgboost import XGBClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier

def connection():
    connection = mysql.connector.connect(host=host,
                                        database= sql_user,
                                        user=sql_user,
                                        password=sql_password)
    return connection

conn = connection()
cursor = conn.cursor()
query = ("SELECT `SummonerMatchTbl`.ChampionFk, `MatchStatsTbl`.`MinionsKilled`,`MatchStatsTbl`.Lane,`MatchStatsTbl`.`DmgDealt`,`MatchStatsTbl`.`DmgTaken`,`MatchStatsTbl`.`TurretDmgDealt`,`MatchStatsTbl`.`TotalGold`,`MatchStatsTbl`.EnemyChampionFk,  `MatchTbl`.`GameDuration`,`MatchStatsTbl`.`DragonKills`,`MatchStatsTbl`.`BaronKills` ,`MatchStatsTbl`.`Win` FROM `SummonerMatchTbl` JOIN `MatchStatsTbl`ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk` WHERE `MatchTbl`.`QueueType` = 'CLASSIC';")
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

XGB = XGBClassifier()
XGB.fit(X_train, y_train)
XGB_disp = RocCurveDisplay.from_estimator(XGB, X_test, y_test)

svc = SVC(probability=True)
svc.fit(X_train, y_train)
ax = plt.gca()
svc_disp = RocCurveDisplay.from_estimator(svc, X_test, y_test,ax= ax, alpha=0.8)

Gradient = GradientBoostingClassifier(learning_rate=0.20)
Gradient.fit(X_train,y_train)
ax = plt.gca()
Gradient_disp = RocCurveDisplay.from_estimator(Gradient, X_test, y_test,ax= ax, alpha=0.8)

Naive = GaussianNB()
Naive.fit(X_train,y_train)
Naive_disp = RocCurveDisplay.from_estimator(Naive, X_test, y_test,ax= ax, alpha=0.8)

rf = RandomForestClassifier()
rf.fit(X_train, y_train)
rf_disp = RocCurveDisplay.from_estimator(rf, X_test, y_test,ax= ax, alpha=0.8)

abc = AdaBoostClassifier(n_estimators=50,
                            learning_rate=1)
abc = abc.fit(X_train, y_train)
abc_disp = RocCurveDisplay.from_estimator(abc, X_test, y_test,ax= ax, alpha=0.8)

plt.savefig("figure.png")