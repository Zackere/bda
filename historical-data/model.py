import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.model_selection import KFold 
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import balanced_accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC

def read_numpy(name):
    print("loading train labels...")
    train_y = np.load("./historical-data/data_for_model/"+name+"_train_y.npy")
    print("train labels loaded")
    print("loading train x...")
    train_x = np.load("./historical-data/data_for_model/"+name+"_train_x.npy")
    print("train x loaded")
    return train_x,train_y

def scale_aqi(y_train, y_test):
    bins = [0, 50, 100, 150, 200, 300, np.inf]
    names = ['good', 'moderate', 'unhealthy for sensitive','unhealthy', 'very unhealthy', 'hazardous']

    y_train = pd.cut(y_train, bins, labels=names)
    y_test = pd.cut(y_test,bins, labels=names)
    return y_train, y_test

def append_result(name, df, accuracy):
    return df.append({'Algorithm': name, 'Accuracy': accuracy}, ignore_index=True)

def run_algorithms(X, y):
    
    df = pd.DataFrame(columns=['Algorithm', 'Accuracy'])

    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)
    X = preprocessing.normalize(X, norm='l2')

    k = 5
    kf = KFold(n_splits = k, shuffle = True)

    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index,:], X[test_index,:]
        y_train, y_test = y[train_index], y[test_index]
        y_train, y_test = scale_aqi(y_train, y_test)
        # - linear svm
        if city != 'berlin':
            clf = LinearSVC(random_state=1, tol=1e-5,max_iter=300).fit(X_train, y_train)
            ba = clf.score(X_test, y_test)
            df = append_result('Linear SVC',df,ba)

        # - decision tree
        clf = DecisionTreeClassifier(random_state=1).fit(X_train, y_train)
        ba = clf.score(X_test, y_test)
        df = append_result('Decision Tree',df,ba)

        # - random forest
        clf = RandomForestClassifier(random_state=1).fit(X_train, y_train)
        ba = clf.score(X_test, y_test)
        df = append_result('Random Forest',df,ba)

        # - multilayer perceptron
        clf = MLPClassifier(random_state=1, max_iter=300).fit(X_train, y_train)
        ba = clf.score(X_test, y_test)
        df = append_result('MLP',df,ba)
      

    df = df.groupby(['Algorithm']).mean().reset_index()
    return df

cities = ['berlin','delhi','moscow','warsaw']
for city in cities:
    train_x_a,train_y_a = read_numpy(city)

    data = pd.DataFrame(train_x_a)
    data["y"] = train_y_a
    corrmat = data.corr()

    f = open(f"./historical-data/results/{city}.txt", "w")
    df = pd.DataFrame()
    #0.03, 0.06, 0.08, 0.1
    for min_corr in [0.03, 0.06, 0.1, 0.2]:
        features_idx = corrmat[np.abs(corrmat["y"]) > min_corr]["y"][:-1].index.tolist()
        result_df = run_algorithms(train_x_a[:,features_idx],train_y_a)
        
        result_df["MinCorr"] = min_corr
        df = df.append(result_df)

        f.write(f"{min_corr}\n")
        f.write(",".join(map(str, features_idx)))
        f.write(f"\n")

    f.close()
    df.to_csv(f"./historical-data/results/{city}_f.txt", index=False)
    


