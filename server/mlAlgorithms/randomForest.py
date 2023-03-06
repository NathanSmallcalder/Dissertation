import mysql.connector
import sys
import pytest
import requests

sys.path.append('..')
from config import *
from RiotApiCalls import *

# Data Processing
import pandas as pd
import numpy as np

# Modelling
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint

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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

rf = RandomForestClassifier()
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

row = [["154", "757" ,"3","245888","2568","4","0","0 ","0 ","0","0"]]

yhat = rf.predict(row)
print('Prediction: %d' % yhat[0])