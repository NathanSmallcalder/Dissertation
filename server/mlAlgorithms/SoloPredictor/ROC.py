from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt
from randomForestSolo import *
from xgBoost import *

randomForestRun()
runxGboost()


plt.savefig("figure.png")