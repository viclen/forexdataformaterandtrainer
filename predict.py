import datetime
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import os
import json

forex = pd.read_csv("dataforprediction.csv",index_col="Time")

forex.index = pd.to_datetime(forex.index)

X_test = forex.drop(['Value'],axis=1)
y_test = forex['Value']

X_test.index = [i.timestamp() for i in X_test.index]
y_test.index = [i.timestamp() for i in y_test.index]

X_test = X_test.sort_index()
y_test = y_test.sort_index()

scaler = MinMaxScaler()
data_for_scale = pd.read_csv("rates-p/completehour.csv",index_col="Time").drop(["Value"],axis=1)
scaler.fit(data_for_scale)

X_test = pd.DataFrame(data=scaler.transform(X_test),columns = X_test.columns,index=X_test.index)

ema = tf.feature_column.numeric_column('EMA')
sma = tf.feature_column.numeric_column('SMA')
rsi = tf.feature_column.numeric_column('RSI')
hbb = tf.feature_column.numeric_column('HBB')
lbb = tf.feature_column.numeric_column('LBB')

feat_cols = [ema, sma, rsi, hbb, lbb]

optimizer = tf.train.AdagradOptimizer(learning_rate=0.01)

model = tf.estimator.DNNRegressor(hidden_units=[1024, 512, 256],
                                feature_columns=feat_cols,
                                model_dir=os.getcwd()+'/models',
                                activation_fn=tf.nn.relu,
                                optimizer=optimizer)

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
    print(pred['predictions'][0])

error = mean_squared_error(y_test,final_preds)**0.5

print("\nError: {}".format(error))