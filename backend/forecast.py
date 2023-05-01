# Import libraries
import itertools
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
import seaborn as sns
import yaml
import yfinance as yf
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
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
end = date(2030, 1, 1)

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

# Change all column headings to be lower case, and remove spacing
df.columns = [str(x).lower().replace(" ", "_") for x in df.columns]

### Prophet ---
# prepare expected column names
df.columns = ["ds", "y"]
df["ds"] = pd.to_datetime(df["ds"])

# Visualize data using seaborn
sns.set(rc={"figure.figsize": (12, 8)})
sns.lineplot(x=df["ds"], y=df["y"])
plt.legend(["TLS"])
plt.show()


# Split data into train and test (80% vs 20%)
test_size = 0.2
test_split_idx = int(df.shape[0] * (1 - test_size))

df_train = df.loc[:test_split_idx].copy()
df_test = df.loc[test_split_idx + 1 :].copy()

# Initiate the model
baseline_model = Prophet()  # Fit the model on the training dataset

baseline_model.fit(df_train)

# Cross validation
baseline_model_cv = cross_validation(
    model=baseline_model,
    initial="200 days",
    period="30 days",
    horizon="30 days",
    parallel="processes",
)
baseline_model_cv.head()

# Model performance metrics
baseline_model_p = performance_metrics(baseline_model_cv, rolling_window=1)
baseline_model_p.head()

# Get the performance metric value
baseline_model_p["mae"].values[0]
baseline_model_p["rmse"].values[0]

# Evaluation on test set using the baseline_model
df_pred_baseline = baseline_model.predict(df_test)
yhat_baseline = df_pred_baseline["yhat"]
actuals = df_test["y"]
print(f"MAE on test set: {mean_absolute_error(actuals, yhat_baseline)}")
print(f"RMSE on test set: {mean_squared_error(actuals, yhat_baseline, squared=False)}")

# Hyperparameter tuning
# Set up parameter grid
param_grid = {
    "changepoint_prior_scale": [0.001, 0.05, 0.08, 0.5],
    "seasonality_prior_scale": [0.01, 1, 5, 10, 12],
    "seasonality_mode": ["additive", "multiplicative"],
}

# Generate all combinations of parameters
all_params = [
    dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())
]

# Create a list to store MAPE values for each combination
maes = []

# Use cross validation to evaluate all parameters
for params in all_params:
    # Fit a model using one parameter combination
    m = Prophet(**params).fit(df_train)

    # Cross-validation
    df_cv = cross_validation(
        m, initial="200 days", period="30 days", horizon="30 days", parallel="processes"
    )

    # Model performance
    df_p = performance_metrics(df_cv, rolling_window=1)

    # Save model performance metrics
    maes.append(df_p["mae"].values[0])

# Tuning results
tuning_results = pd.DataFrame(all_params)
tuning_results["mae"] = maes  # Find the best parameters
best_params = all_params[np.argmin(maes)]
print(best_params)

# Fit the model using the best parameters
auto_model = Prophet(
    changepoint_prior_scale=best_params["changepoint_prior_scale"],
    seasonality_prior_scale=best_params["seasonality_prior_scale"],
    seasonality_mode=best_params["seasonality_mode"],
)

# Fit the model on the training dataset
auto_model.fit(df_train)

# Cross validation
auto_model_cv = cross_validation(
    auto_model,
    initial="200 days",
    period="30 days",
    horizon="30 days",
    parallel="processes",
)

# Model performance metrics
auto_model_p = performance_metrics(auto_model_cv, rolling_window=1)
auto_model_p["mae"].values[0]
auto_model_p["rmse"].values[0]

# Evaluation on test set using the tuned_model
df_pred_tuned = auto_model.predict(df_test)
yhat_tuned = df_pred_tuned["yhat"]
print(f"MAE on test set: {mean_absolute_error(actuals, yhat_tuned)}")
print(f"RMSE on test set: {mean_squared_error(actuals, yhat_tuned, squared=False)}")
