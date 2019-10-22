import datetime
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import os
import time

forex = pd.read_csv("rates-p/completehour.csv",index_col="Time")

forex.index = pd.to_datetime(forex.index)

x_data = forex.drop(['Value'],axis=1)
y_val = forex['Value']

X_train, X_test, y_train, y_test = train_test_split(x_data,y_val,test_size=0.000001)

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

X_train = pd.DataFrame(data=scaler.transform(X_train),columns = X_train.columns,index=X_train.index)
X_test = pd.DataFrame(data=scaler.transform(X_test),columns = X_test.columns,index=X_test.index)

ema = tf.feature_column.numeric_column('EMA')
sma = tf.feature_column.numeric_column('SMA')
rsi = tf.feature_column.numeric_column('RSI')
hbb = tf.feature_column.numeric_column('HBB')
lbb = tf.feature_column.numeric_column('LBB')

feat_cols = [ema, sma, rsi, hbb, lbb]

input_func = tf.estimator.inputs.pandas_input_fn(x=X_train,y=y_train,batch_size=100,num_epochs=2000,shuffle=True)

optimizer = tf.train.AdagradOptimizer(learning_rate=0.01)

model = tf.estimator.DNNRegressor(hidden_units=[1024, 512, 256],
                                feature_columns=feat_cols,
                                model_dir=os.getcwd()+'/models',
                                activation_fn=tf.nn.relu,
                                optimizer=optimizer)

# model = tf.estimator.DNNRegressor(hidden_units=[1024, 512, 256],
#                                 optimizer=tf.train.ProximalAdagradOptimizer(
#                                     learning_rate=0.1,
#                                     l1_regularization_strength=0.001
#                                 )
#                                 feature_columns=feat_cols,
#                                 model_dir=os.getcwd()+'/models',
#                                 activation_fn=tf.nn.relu)

print("Starting train")
millis = time.time()
model.train(input_fn=input_func,steps=50000)
print("Total time: {} s".format(round(time.time() - millis, 3)))

predict_input_func = tf.estimator.inputs.pandas_input_fn(
      x=X_test,
      batch_size=10,
      num_epochs=1,
      shuffle=False)

pred_gen = model.predict(predict_input_func)
predictions = list(pred_gen)

final_preds = []
for pred in predictions:
    final_preds.append(pred['predictions'])

error = mean_squared_error(y_test,final_preds)**0.5

print("Done\nError rate: {}".format(error))