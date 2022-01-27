import pandas as pd
import numpy as np
import pickle
import warnings
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

warnings.filterwarnings("ignore")

df = pd.read_csv('games_data.csv')
df = df.drop(['odds_home', 'odds_away', 'odds_draw'], axis=1)

x = df[[x for x in df.columns if x != 'result']]
y = df['result']

column_maxes = x.max()
x_max = column_maxes.max()
normalized_x = x / x_max

x_train, x_test, y_train, y_test = train_test_split(normalized_x, y, test_size=0.33, random_state=42, stratify=y)

mlp_classifier = MLPClassifier(solver='lbfgs', max_iter=1000, alpha=0.05, learning_rate='constant')
mlp_classifier.fit(x_train, y_train)

pickle.dump(mlp_classifier, open('mlp_classifier.pkl', 'wb'))
