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
df = df[(df["Date"] >= "2018-09-11")].reset_index(drop=True)

standing = standing[(standing["Season_End_Year"] > "10-08-2018")].reset_index(drop=True)
standing["Season_End_Year"] = pd.to_datetime(standing["Season_End_Year"])
print(standing.head())


standing = standing.set_index(["Season_End_Year"]).groupby(['Team'], group_keys= False).resample('D').first().fillna(method='ffill').reset_index()
standing["Year"] = pd.DatetimeIndex(standing["Season_End_Year"]).year

standing_Epl = pd.pivot_table(data = standing,
                            values = 'Pts',
                            index= 'Team',
                            columns='Year',
                           ).fillna(0.0)
            
print(standing_Epl.head())
fig = go.Figure()

for i in range(len(standing_Epl.values)):
    fig.add_trace(go.Scatter(x = standing_Epl.columns, 
                             y = standing_Epl.iloc[i],
                             name = standing_Epl.index[i]))

#fig.show()
    
print(df.columns)
print(standing_Epl.columns)


home = df[['Date','Home', 'HomeGoals']].rename(columns={'Home':'team', 'HomeGoals':'score'})
home['Date'] = pd.to_datetime(home['Date'])


latestSeasonH = (home['Date'] > '2018-10-26') & (home['Date'] <= '2019-05-12')
print(home.loc[latestSeasonH])

away = df[['Date','AwayGoals', 'Away']].rename(columns={'Away':'team', 'AwayGoals':'score'})
latestSeasonA = (away['Date'] > '2018-10-26') & (away['Date'] <= '2019-05-12')


home = home.loc[latestSeasonH].groupby(['team'], as_index=False)['score'].sum()
away = away.loc[latestSeasonA].groupby(['team'], as_index=False)['score'].sum()

team_score = home.append(away).reset_index(drop=True)
plt.figure(figsize = (15,10))
sns.set_style("whitegrid")

country_info = team_score.groupby('team')['score'].agg(['sum','count','mean']).reset_index()
country_info = country_info.rename(columns={'sum':'nb_goals', '38':'nb_matches', 'mean':'goal_avg'})
print(country_info)
plt_data = country_info.sort_values(by='goal_avg', ascending=False)[:10]
ax = sns.barplot(x="team", y="goal_avg", data=plt_data, palette="Blues_r")
ax.set_xlabel('Team', size=16)
ax.set_ylabel('Goal average per match', size=16)
ax.set_title("TOP 10 OF GOAL AVERAGE PER MATCH", fontsize=18)
plt.show()