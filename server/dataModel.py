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

i = 0
predictionsArray = []
while i < 5:
    df_games = pd.read_csv(r'data.csv',encoding='latin-1') 
    df_games = df_games.sample(frac=1)
    winner = df_games['win']
    print(df_games)
    df_games = df_games.drop('champion', axis=1)

    print(df_games)
    X = df_games
    y = winner - 1
    X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.20, random_state=1)

    print(X_train)
    print(y)

    model = SVC(gamma='auto')
    model.fit(X_train, Y_train)
    predictions = model.predict(X_validation)
    # Evaluate predictions
    predictionsArray.append(accuracy_score(Y_validation, predictions))
    print(accuracy_score(Y_validation, predictions))
    print(confusion_matrix(Y_validation, predictions))
    print(classification_report(Y_validation, predictions))
    i = i + 1



fig, ax = plt.subplots()

x = 1,2,3,4,5
ax.plot(x,predictionsArray, linewidth=2.0)
ax.set_title('Model Accuracy')
plt.show()


df_for_corr_first = df_games.iloc[:, [4, 5, 6, 7, 8, 9, 10]] 
ax = plt.axes()
sns.set(font_scale=1.4)
sns.heatmap(df_for_corr_first.corr(), annot=True, cmap="YlGnBu")
ax.set_title('Feature Importance')
plt.show()

