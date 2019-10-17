import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

forex = pd.read_csv("completehour-p10.csv",index_col="Time")

# forex.info()

forex.index = forex.index.to_datetime()

qnt = 100

x_data = forex.drop(['Value'],axis=1)

y_val = forex['Value']

X_train, X_test, y_train, y_test = train_test_split(x_data,y_val,test_size=0.3,random_state=101)

X_train.index = [i.timestamp() for i in X_train.index]
X_test.index = [i.timestamp() for i in X_test.index]
y_train.index = [i.timestamp() for i in y_train.index]
y_test.index = [i.timestamp() for i in y_test.index]

X_train = X_train.sort_index()
X_test = X_test.sort_index()
y_train = y_train.sort_index()
y_test = y_test.sort_index()

scaler = MinMaxScaler()

scaler.fit(X_train)