# Import libraries
import math
import os
import sys
import time
from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import regex as re
import yaml
import yfinance as yf
from fbprophet import Prophet
from sklearn.metrics import mean_absolute_error

# variables
prev_date = date.today() - timedelta(days=1)
prev_date_formated = prev_date.strftime("%Y-%m-%d")

# Get stock quote
def get_stock_price(ticker, startdate, enddate) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    stock_df = pd.DataFrame(stock.history(start=startdate, end=enddate).reset_index())
    stock_df["Date"] = stock_df["Date"].dt.tz_localize(None)
    return stock_df


# obtain historical data
df = get_stock_price("TLS.AX", "2013-01-01", prev_date_formated)

df.drop(
    ["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"], axis=1, inplace=True
)

# Change all column headings to be lower case, and remove spacing
df.columns = [str(x).lower().replace(" ", "_") for x in df.columns]

### Prophet ---
# prepare expected column names
df.columns = ["ds", "y"]
df["ds"] = pd.to_datetime(df["ds"])

"""
    train, validation, test split
    80% on train, 20% on test
"""
test_size = 0.2

test_split_idx = int(df.shape[0] * (1 - test_size))

df_train = df.loc[:test_split_idx].copy()
df_test = df.loc[test_split_idx + 1 :].copy()
# add logging of the shape


# pd.plotting.register_matplotlib_converters()
# f, ax = plt.subplots(figsize=(14,5))
# df_train.plot(kind='line', x='ds', y='y', color='blue', label='Train', ax=ax)
# df_test.plot(kind='line', x='ds', y='y', color='red', label='Test', ax=ax)
# plt.show()


# define the model
model = Prophet()
# fit the model
model.fit(df_train)

# define the period for which we want a prediction
future = df_test[["ds"]]

# use the model to make a forecast
forecast = model.predict(future)
df_forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

# calculate MAE between expected and predicted values for december
y_true = df_test["y"].values
y_pred = df_forecast["yhat"].values
mae = mean_absolute_error(y_true, y_pred)
print("MAE: %.3f" % mae)

# plot expected vs actual
plt.plot(y_true, label="Actual")
plt.plot(y_pred, label="Predicted")
plt.legend()
plt.show()
