import mysql.connector
import sys
import pytest
import requests

sys.path.append('..')
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
from sklearn import metrics


connection = mysql.connector.connect(host=host,
                                     database= sql_user,
                                     user=sql_user,
                                     password=sql_password)

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
print(df_games)

X = df_games.drop('Win', axis=1)
y = df_games['Win']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)

sc = StandardScaler()
sc.fit(X_train)
X_train_std = sc.transform(X_train)
X_test_std = sc.transform(X_test)

# Instantiate the Support Vector Classifier (SVC)
svc = SVC(C=1.0, random_state=1, kernel='linear')
 
# Fit the model
svc.fit(X_train_std, y_train)

# Make the predictions
y_predict = svc.predict(X_test_std)

# Measure the performance
print("Accuracy score %.3f" %metrics.accuracy_score(y_test, y_predict))