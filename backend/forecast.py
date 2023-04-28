# Import libraries
import math
import os
import random
import sys
import time
from datetime import date, timedelta

import holidays
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import regex as re
import yaml
import yfinance as yf
from fbprophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import ParameterGrid

# variables
prev_date = date.today() - timedelta(days=1)
prev_date_formated = prev_date.strftime("%Y-%m-%d")


# Get stock quote
def get_stock_price(ticker, startdate, enddate) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    stock_df = pd.DataFrame(stock.history(start=startdate, end=enddate).reset_index())
    stock_df["Date"] = stock_df["Date"].dt.tz_localize(None)
    return stock_df


# create a AUS Holiday dataframe
start = date(2013, 1, 1)
end = date(2023, 1, 1)

year_range = [year for year in range(start.year, end.year + 1)]

holiday = pd.DataFrame([])
for date, name in sorted(holidays.Australia(years=year_range).items()):
    holiday = holiday.append(
        pd.DataFrame({"ds": date, "holiday": "AUS-Holidays"}, index=[0]),
        ignore_index=True,
    )
holiday["ds"] = pd.to_datetime(holiday["ds"], format="%Y-%m-%d", errors="ignore")

# obtain historical data
df = get_stock_price("TLS.AX", "2013-01-01", prev_date_formated)

df.drop(
    ["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"], axis=1, inplace=True
)

plt.plot(df["Date"], df["Close"])
plt.show()

# Change all column headings to be lower case, and remove spacing
df.columns = [str(x).lower().replace(" ", "_") for x in df.columns]

### Prophet ---
# prepare expected column names
df.columns = ["ds", "y"]
df["ds"] = pd.to_datetime(df["ds"])


# Split data into train and test (80% vs 20%)
test_size = 0.2
test_split_idx = int(df.shape[0] * (1 - test_size))

df_train = df.loc[:test_split_idx].copy()
df_test = df.loc[test_split_idx + 1 :].copy()

# define the model
model = Prophet()
# fit the model
model.fit(df_train)

# define the period for which we want a prediction - in sample
future_in_sample = df_train[["ds"]].tail(90).reset_index(drop=True)

# use the model to make a forecast
forecast_in_sample = model.predict(future_in_sample)
# summarize the forecast
print(forecast_in_sample[["ds", "yhat", "yhat_lower", "yhat_upper"]].head())
# plot forecast
model.plot(forecast_in_sample)
plt.show()


# Evaludate the model on the last 90 samples
predictions = forecast_in_sample["yhat"]
actuals = df_train.tail(90)["y"].reset_index(drop=True)

print(f"RMSE: {mean_squared_error(actuals, predictions)}")
print(f"MAE: {mean_absolute_error(actuals, predictions)}")

# Forecast on test set
future_test = df_test[["ds"]].reset_index(drop=True)
forecast_test = model.predict(future_test)

# summarize the forecast
print(forecast_test[["ds", "yhat", "yhat_lower", "yhat_upper"]].head())
# plot forecast
model.plot(forecast_test)
plt.show()

# Evaluate on test set
pred_test = forecast_test["yhat"]
print(f"RMSE: {mean_squared_error(df_test['y'].reset_index(drop=True), pred_test)}")
print(f"MAE: {mean_absolute_error(df_test['y'].reset_index(drop=True), pred_test)}")


### Hyperparameter tuning with ParameterGrid
params_grid = {
    "seasonality_mode": ("multiplicative", "additive"),
    "changepoint_prior_scale": [0.1, 0.2, 0.3, 0.4, 0.5],
    "holidays_prior_scale": [0.1, 0.2, 0.3, 0.4, 0.5],
    "n_changepoints": [100, 150, 200],
}
grid = ParameterGrid(params_grid)
cnt = 0
for p in grid:
    cnt = cnt + 1

print("Total Possible Models", cnt)

model_parameters = pd.DataFrame(columns=["RMSE", "MAE", "Parameters"])
for p in grid:
    test = pd.DataFrame()
    print(p)
    random.seed(1234)
    train_model = Prophet(
        changepoint_prior_scale=p["changepoint_prior_scale"],
        holidays_prior_scale=p["holidays_prior_scale"],
        n_changepoints=p["n_changepoints"],
        seasonality_mode=p["seasonality_mode"],
        weekly_seasonality=True,
        daily_seasonality=True,
        yearly_seasonality=True,
        holidays=holiday,
        interval_width=0.95,
    )
    train_model.add_country_holidays(country_name="AU")
    train_model.fit(df_train)
    train_forecast = df_train[["ds"]].tail(90).reset_index(drop=True)
    train_forecast = train_model.predict(train_forecast)
    train_pred = train_forecast["yhat"]
    train_actuals = df_train.tail(90)["y"].reset_index(drop=True)

    RMSE = mean_squared_error(actuals, predictions)
    MAE = mean_absolute_error(actuals, predictions)

    print(
        f"Root Mean Square Error (RMSE)------------------------------------ {RMSE}",
    )
    print(
        f"Mean Absolute Error (MAE)------------------------------------ {MAE}",
    )
    model_parameters = model_parameters.append(
        {"RMSE": RMSE, "MAE": MAE, "Parameters": p}, ignore_index=True
    )

parameters = model_parameters.sort_values(by=["RMSE"])
parameters = parameters.reset_index(drop=True)
parameters["Parameters"][0]

# tuned model
tuned_model = Prophet(
    holidays=holiday,
    changepoint_prior_scale=0.1,
    holidays_prior_scale=0.1,
    n_changepoints=100,
    seasonality_mode="multiplicative",
    weekly_seasonality=True,
    daily_seasonality=True,
    yearly_seasonality=True,
    interval_width=0.95,
)
tuned_model.add_country_holidays(country_name="AU")

tuned_model.fit(df_train)

# use the tuned model to make a forecast
forecast_in_sample_tuned = tuned_model.predict(future_in_sample)
# summarize the forecast
print(forecast_in_sample_tuned[["ds", "yhat", "yhat_lower", "yhat_upper"]].head())
# plot forecast
tuned_model.plot(forecast_in_sample_tuned)
plt.show()


# Evaludate the model on the last 90 samples
predictions_tuned = forecast_in_sample_tuned["yhat"]
actuals = df_train.tail(90)["y"].reset_index(drop=True)

print(f"RMSE: {mean_squared_error(actuals, predictions_tuned)}")
print(f"MAE: {mean_absolute_error(actuals, predictions_tuned)}")


# Forecast on test set
forecast_test_tuned = tuned_model.predict(future_test)

# summarize the forecast
print(forecast_test_tuned[["ds", "yhat", "yhat_lower", "yhat_upper"]].head())
# plot forecast
model.plot(forecast_test_tuned)
plt.show()

# Evaluate on test set
pred_test_tuned = forecast_test_tuned["yhat"]
print(
    f"RMSE: {mean_squared_error(df_test['y'].reset_index(drop=True), pred_test_tuned)}"
)
print(
    f"MAE: {mean_absolute_error(df_test['y'].reset_index(drop=True), pred_test_tuned)}"
)
