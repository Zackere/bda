import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.metrics import mean_squared_error
import statistics
from sklearn.neural_network import MLPClassifier
import dataframe_image as dfi
from sklearn.linear_model import LinearRegression

path_plots = '/Users/adaklimczak/Desktop/bda/bda/historical-data/plots'
path = '/Users/adaklimczak/Desktop/bda/bda/historical-data/weather/'
path2 = '/Users/adaklimczak/Desktop/bda/bda/historical-data/pollution/'

def join_on_city(path,path2,city):
    df = pd.read_json(path+city+'.json')
    df = df.drop(['lat','lon'],axis=1)
    df2 = pd.read_json(path2+city+'.json')
    df2 = df2.drop(['lat','lon'],axis=1)
    df = pd.merge(df,df2,on='measured')
    return df

def histogram(aqi,city):
    fig, ax = plt.subplots(figsize = (6,4))

    aqi.plot(kind = "hist", density = True, alpha = 0.65, bins = 15) # change density to true, because KDE uses density
    aqi.plot(kind = "kde")

    quant_5, quant_25, quant_50, quant_75, quant_95 = aqi.quantile(0.05), aqi.quantile(0.25), aqi.quantile(0.5), aqi.quantile(0.75), aqi.quantile(0.95)
    quants = [[quant_5, 0.6, 0.16], [quant_25, 0.8, 0.26], [quant_50, 1, 0.36],  [quant_75, 0.8, 0.46], [quant_95, 0.6, 0.56]]
    for i,name in zip(quants,["5th","25th","50th","75th","95th Percentile"]):
        ax.axvline(i[0], alpha = i[1], ymax = i[2], linestyle = ":")
        ax.text(i[0], i[2]/100, name, size = 10, alpha = 0.8)

    ax.set_xlabel(f"aqi")
    ax.set_ylabel("")

    # Overall
    ax.grid(False)
    ax.set_title(f"Aqi distribution {city}", size = 10, pad = 10)

    ax.tick_params(left = False, bottom = False)
    for ax, spine in ax.spines.items():
        spine.set_visible(False)

def scale_aqi(y_train, y_test):
    bins = [0, 50, 100, 150, 200, 300, np.inf]
    names = ['good', 'moderate', 'unhealthy for sensitive','unhealthy', 'very unhealthy', 'hazardous']
    y_train = pd.cut(y_train, bins, labels=names)
    y_test = pd.cut(y_test,bins, labels=names)
    return y_train, y_test

def compute_basic_statistics(df,city):
    print(df.head(5))
    print(df.shape)
    with pd.option_context('display.float_format', '{:0.2f}'.format):
        df2 = df.describe().transpose()
        print(df2) #Descriptive statistics of the data-sets
        ax = plt.subplot(111, frame_on=False) # no visible frame
        ax.xaxis.set_visible(False)  # hide the x axis
        ax.yaxis.set_visible(False)  # hide the y axis
        dfi.export(df2, f'{path_plots}/{city}_stat.png')
    print(df.corr()) #Checking about the correlation between features in a dataset
    print(df.isnull().sum())
    duplicate_rows_df = df[df.duplicated()] #Dropping the duplicate rows
    df = df.drop_duplicates()

    print('number of duplicate rows: ', duplicate_rows_df.shape)

    plt.clf()
    sns.boxplot(x=df['aqi']) #outliers
    plt.savefig(f'{path_plots}/{city}_outliers.png')

    print("before IQR",df.shape)
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df < (Q1-1.5 * IQR)) |(df > (Q3 + 1.5 * IQR))).any(axis=1)]
    print("after IQR",df.shape)

    plt.clf()
    # Plotting a Histogram
    histogram(df['aqi'],city)
    plt.savefig(f'{path_plots}/{city}_hist.png')

    # Finding the relations between the variables.
    plt.figure(figsize=(20,10))
    c = df.corr()
    sns.heatmap(c,cmap=sns.cubehelix_palette(start=.5, rot=-.75, as_cmap=True),annot=True)
    plt.savefig(f'{path_plots}/{city}_correlation.png')

    # Plotting a scatter plot
    fig, ax = plt.subplots(figsize=(7,6))
    ax.scatter(df['measured'],df['aqi'])
    ax.set_xlabel('measured')
    ax.set_ylabel('aqi')
    plt.savefig(f'{path_plots}/{city}_scatter.png')

    return df

cities = ['berlin','delhi','moscow','warsaw']
for city in cities:
    print(f'################# {city} #################')
    df = join_on_city(path,path2,city)
    df = compute_basic_statistics(df,city)

    data_df = df['aqi']
    df = df.drop(columns=['aqi'])
    
    X_train, X_test, y_train, y_test = train_test_split(df, data_df, test_size=0.2)
    np.save(f'./historical-data/data_for_model/{city}_train_x.npy',X_train)
    np.save(f'./historical-data/data_for_model/{city}_test_x.npy',X_test)
    np.save(f'./historical-data/data_for_model/{city}_train_y.npy',y_train)
    np.save(f'./historical-data/data_for_model/{city}_test_y.npy',y_train)
    
    
    model = LinearRegression().fit(np.asarray(X_train),np.asarray(y_train))
    predict = model.predict(np.asarray(X_test))
    print(f'MSE {mean_squared_error(np.asarray(y_test),predict)}')
    print(f'RMSE {math.sqrt(mean_squared_error(np.asarray(y_test),predict))}')
    print(f'RRMSEP {math.sqrt(mean_squared_error(np.asarray(y_test),predict))/statistics.stdev(y_test)}')
    print(f'accuracy {model.score(np.asarray(X_test),np.asarray(y_test))}')

    y_train, y_test = scale_aqi(y_train, y_test)
    clf = MLPClassifier(random_state=1, max_iter=300).fit(X_train, y_train)
    print(clf.score(X_test, y_test))