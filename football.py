import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

import seaborn as sns
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

df =  pd.read_csv(r"eplmatches.csv")
standing = pd.read_csv(r"league_tables.csv")

df["Date"] = pd.to_datetime(df["Date"])

standing = standing[(standing["Season_End_Year"] > "10-08-2018")].reset_index(drop=True)
standing["Season_End_Year"] = pd.to_datetime(standing["Season_End_Year"])


standing = standing.set_index(["Season_End_Year"]).groupby(['Team'], group_keys= False).resample('D').first().fillna(method='ffill').reset_index()
standing["Year"] = pd.DatetimeIndex(standing["Season_End_Year"]).year

standing_Epl = pd.pivot_table(data = standing,
                            values = 'Pts',
                            index= 'Team',
                            columns='Year',
                           ).fillna(0.0)
            
fig = go.Figure()

for i in range(len(standing_Epl.values)):
    fig.add_trace(go.Scatter(x = standing_Epl.columns, 
                             y = standing_Epl.iloc[i],
                             name = standing_Epl.index[i]))

fig.show()


# <===== SEASON 18/19 ======>
home = df[['Date','Home', 'HomeGoals']].rename(columns={'Home':'team', 'HomeGoals':'score'})
latestSeasonH = (home['Date'] >= '2018-08-10') & (home['Date'] <= '2019-05-12')
away = df[['Date','AwayGoals', 'Away']].rename(columns={'Away':'team', 'AwayGoals':'score'})
latestSeasonA = (away['Date'] >= '2018-08-10') & (away['Date'] <= '2019-05-12')
home18_19 = home.loc[latestSeasonH].groupby(['team'], as_index=False)['score'].sum()
away18_19 = away.loc[latestSeasonA].groupby(['team'], as_index=False)['score'].sum()
teamGoals18_19 = home18_19.append(away18_19).reset_index(drop=True)
plt.figure(figsize = (15,10))
sns.set_style("whitegrid")
goalsScored = teamGoals18_19.groupby('team')['score'].agg(['sum']).reset_index()
goalsScored = goalsScored.rename(columns={'sum':'nb_goals'})
goalsScored['count'] = 38
goalsScored['goal_avg'] = goalsScored['nb_goals'] / goalsScored['count']
plt_data = goalsScored.sort_values(by='goal_avg', ascending=False)[:10]
ax = sns.barplot(x="team", y="goal_avg", data=plt_data, palette="Blues_r")
ax.set_xlabel('Team', size=16)
ax.set_ylabel('Goal average per match', size=16)
ax.set_title("TOP 10 OF GOAL AVERAGE PER MATCH 2018/19 Season", fontsize=18)
#plt.show()


# <===== SEASON 19/20 ======>
home = df[['Date','Home', 'HomeGoals']].rename(columns={'Home':'team', 'HomeGoals':'score'})
latestSeasonH = (home['Date'] > '2019-08-09') & (home['Date'] <= '2020-07-26')
away = df[['Date','AwayGoals', 'Away']].rename(columns={'Away':'team', 'AwayGoals':'score'})
latestSeasonA = (away['Date'] > '2019-08-09') & (away['Date'] <= '2020-07-26')
home19_20 = home.loc[latestSeasonH].groupby(['team'], as_index=False)['score'].sum()
away19_20 = away.loc[latestSeasonA].groupby(['team'], as_index=False)['score'].sum()
teamGoals19_20 = home19_20.append(away19_20).reset_index(drop=True)
plt.figure(figsize = (15,10))
sns.set_style("whitegrid")
goalsScored = teamGoals19_20.groupby('team')['score'].agg(['sum']).reset_index()
goalsScored = goalsScored.rename(columns={'sum':'nb_goals'})
goalsScored['count'] = 38
goalsScored['goal_avg'] = goalsScored['nb_goals'] / goalsScored['count']
plt_data = goalsScored.sort_values(by='goal_avg', ascending=False)[:10]
ax = sns.barplot(x="team", y="goal_avg", data=plt_data, palette="Blues_r")
ax.set_xlabel('Team', size=16)
ax.set_ylabel('Goal average per match', size=16)
ax.set_title("TOP 10 OF GOAL AVERAGE PER MATCH 19/20 Season", fontsize=18)
#plt.show()


# <===== SEASON 20/21 ======>
home = df[['Date','Home', 'HomeGoals']].rename(columns={'Home':'team', 'HomeGoals':'score'})
latestSeasonH = (home['Date'] > '2020-09-12') & (home['Date'] <= '2021-05-23')
away = df[['Date','AwayGoals', 'Away']].rename(columns={'Away':'team', 'AwayGoals':'score'})
latestSeasonA = (away['Date'] > '2020-09-12') & (away['Date'] <= '2021-05-23')
home20_21 = home.loc[latestSeasonH].groupby(['team'], as_index=False)['score'].sum()
away20_21 = away.loc[latestSeasonA].groupby(['team'], as_index=False)['score'].sum()
teamGoals20_21 = home20_21.append(away20_21).reset_index(drop=True)
plt.figure(figsize = (15,10))
sns.set_style("whitegrid")
goalsScored = teamGoals20_21.groupby('team')['score'].agg(['sum']).reset_index()
goalsScored = goalsScored.rename(columns={'sum':'nb_goals'})
goalsScored['count'] = 38
goalsScored['goal_avg'] = goalsScored['nb_goals'] / goalsScored['count']
plt_data = goalsScored.sort_values(by='goal_avg', ascending=False)[:10]
ax = sns.barplot(x="team", y="goal_avg", data=plt_data, palette="Blues_r")
ax.set_xlabel('Team', size=16)
ax.set_ylabel('Goal average per match', size=16)
ax.set_title("TOP 10 OF GOAL AVERAGE PER MATCH 19/20 Season", fontsize=18)
#plt.show()


#GET PL POINTS / FINISH DIVIDE BY NUM OF GAMES


#TrainData = home.merge(away,left_on='team',right_on='team')
#TrainData.rename(columns={"score_x":"HomeGoals", "score_y":"AwayGoals"})

# <----- AVG POINTS ------>
#standing_Epl['AvgPoints'] = standing_Epl.sum(axis=1) / (standing_Epl > 0).sum(axis=1)
#standing_Epl['team'] = standing_Epl.index.values 

#avg = standing_Epl[['team','AvgPoints']]
#TrainData = TrainData.merge(avg,left_on='team',right_on='team')
#print(TrainData)
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from scipy import stats
from sklearn.linear_model import LogisticRegression
from collections import Counter
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestRegressor
import warnings


#X, y = TrainData.loc[:,['score_x','score_y','AvgPoints']]

#X_train, X_test, y_train, y_test = train_test_split(
   #X, y, test_size=0.2, random_state=42)

#def plot_roc_cur(fper, tper):  
#    plt.plot(fper, tper, color='orange', label='ROC')
#    plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')
#    plt.xlabel('False Positive Rate')
#    plt.ylabel('True Positive Rate')
#    plt.title('Receiver Operating Characteristic (ROC) Curve')
#    plt.legend()
#    plt.show()