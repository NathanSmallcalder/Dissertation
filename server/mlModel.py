from pandas import read_csv
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from matplotlib import *
import sys
from pylab import *
import seaborn as sns
import mysql.connector
from config import *
import pandas
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from matplotlib import pyplot as plt

connection = mysql.connector.connect(host=host,
                                     database= sql_user,
                                     user=sql_user,
                                     password=sql_password)
                    
query = ("SELECT `SummonerMatchTbl`.ChampionFk, `MatchStatsTbl`.`MinionsKilled`,`MatchStatsTbl`.`DmgDealt`,`MatchStatsTbl`.`DmgTaken`,`MatchStatsTbl`.`TurretDmgDealt`,`MatchStatsTbl`.`TotalGold`,`MatchStatsTbl`.EnemyChampionFk,`MatchStatsTbl`.item1,`MatchStatsTbl`.item2,`MatchStatsTbl`.item3,`MatchStatsTbl`.item4,`MatchStatsTbl`.item5,`MatchStatsTbl`.item6,`MatchStatsTbl`.PrimaryKeyStone,`MatchStatsTbl`.PrimarySlot1, `MatchStatsTbl`.PrimarySlot2 , `MatchStatsTbl`.PrimarySlot3 ,  `MatchStatsTbl`.SecondarySlot1, `MatchStatsTbl`.SecondarySlot1, `MatchStatsTbl`.`Win`, `MatchTbl`.`GameDuration`,`MatchStatsTbl`.`DragonKills`,`MatchStatsTbl`.`BaronKills`FROM `SummonerMatchTbl` JOIN `MatchStatsTbl`ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk` WHERE `MatchTbl`.`QueueType` = 'CLASSIC';")
cursor = connection.cursor()

cursor.execute(query)
data = cursor.fetchall()

columns = ['ChampionFk', 'MinionsKilled','DmgDealt','DmgTaken','TurretDmgDealt','TotalGold'
,'EnemyChampionFk','item1','item2','item3','item4','item5','item6','PrimaryKeyStone',
'PrimarySlot1', 'PrimarySlot2' , 'PrimarySlot3' ,  'SecondarySlot1','SecondarySlot1', 'Win', 'GameDuration','DragonKills','BaronKills']

df_games = pandas.DataFrame(data,columns = columns)
df_games.sample(frac=1)
winner = df_games['Win']

print(df_games)

X = df_games
y = winner 

X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.25, random_state=1)

print(X_train)
print(y)
model = SVC(gamma='auto')
model.fit(X_train, Y_train)
predictions = model.predict(X_validation)
# Evaluate predictions
print(accuracy_score(Y_validation, predictions))
print(confusion_matrix(Y_validation, predictions))
print(classification_report(Y_validation, predictions))


query = ("SELECT `SummonerMatchTbl`.ChampionFk, `MatchStatsTbl`.`MinionsKilled`,`MatchStatsTbl`.`DmgDealt`,`MatchStatsTbl`.`DmgTaken`,`MatchStatsTbl`.`TurretDmgDealt`,`MatchStatsTbl`.`TotalGold`,`MatchStatsTbl`.EnemyChampionFk, `MatchStatsTbl`.`Win`, `MatchTbl`.`GameDuration`,`MatchStatsTbl`.`DragonKills`,`MatchStatsTbl`.`BaronKills`FROM `SummonerMatchTbl` JOIN `MatchStatsTbl`ON `MatchStatsTbl`.SummonerMatchFk = `SummonerMatchTbl`.SummonerMatchId JOIN `MatchTbl` ON `MatchTbl`.`MatchId` = `SummonerMatchTbl`.`MatchFk` WHERE `MatchTbl`.`QueueType` = 'CLASSIC';")
cursor = connection.cursor()

cursor.execute(query)
data = cursor.fetchall()

columns = ['ChampionFk', 'MinionsKilled','DmgDealt','DmgTaken','TurretDmgDealt','TotalGold'
,'EnemyChampionFk', 'Win', 'GameDuration','DragonKills','BaronKills']

df_games = pandas.DataFrame(data,columns = columns)
df_games.to_csv('data.csv')
df_games.sample(frac=1)
winner = df_games['Win']

print(df_games)

X = df_games
y = winner 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
rf = RandomForestRegressor(n_estimators=150)
rf.fit(X_train, y_train)

sort = rf.feature_importances_.argsort()
plt.barh(columns[sort], rf.feature_importances_[sort])
plt.xlabel("Feature Importance")
plt.savefig('HEATMAP.PNG')