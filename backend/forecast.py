# Import libraries
import itertools
import logging
import math
import os
import random
import sys
import time
from datetime import date
from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path

import holidays
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import regex as re
import seaborn as sns
import yaml
import yfinance as yf
from box import Box
from dateutil.relativedelta import relativedelta
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
from utils.logging import set_up_logging
from utils.global_functions import add_datepart, add_lags

cfg = Box(yaml.safe_load(open("config_db.yml")))

### set up logging and other params ----
logger = logging.getLogger()
LOG_DIR = Path(f"{cfg.out.LOGS}")
LOG_DIR.mkdir(parents=True, exist_ok=True)

RUN_Date = dt.today().strftime("%Y%m%d")

log_dir_exp = LOG_DIR / f"forecast_{RUN_Date}"
log_dir_exp.mkdir(parents=True, exist_ok=True)
set_up_logging(logger, log_dir_exp / "logs.txt")  # appends to file by default if exists
logging.getLogger("fbprophet").setLevel(logging.WARNING)

# define date range to get holidays in between
holiday_start = date(2023, 1, 1)
holiday_end = date(2033, 1, 1)


# Get stock quote
def get_stock_price(ticker, startdate, enddate) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    stock_df = pd.DataFrame(stock.history(start=startdate, end=enddate).reset_index())
    stock_df["Date"] = stock_df["Date"].dt.tz_localize(None)
    return stock_df


# Function to return holiday df
def get_holiday() -> pd.DataFrame:
    year_range = [year for year in range(holiday_start.year, holiday_end.year + 1)]

    holiday = pd.DataFrame([])
    for date, name in sorted(holidays.Australia(years=year_range).items()):
        holiday = holiday.append(
            pd.DataFrame({"ds": date, "holiday": "AUS-Holidays"}, index=[0]),
            ignore_index=True,
        )
    holiday["ds"] = pd.to_datetime(holiday["ds"], format="%Y-%m-%d", errors="ignore")
    return holiday


def date_by_adding_business_days_l(from_date, add_days) -> list:
    business_days_to_add = add_days
    current_date = from_date
    holidays_l = (
        get_holiday()["ds"].apply(lambda x: dt.strftime(x, "%Y-%m-%d")).to_list()
    )
    future_date_l = []
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5:  # sunday = 6
            continue
        if dt.strftime(current_date, "%Y-%m-%d") in holidays_l:
            continue
        future_date_l.append(current_date)
        business_days_to_add -= 1
    return future_date_l


# Function to get stock price for stock and split data into train and test
def create_dfs(df: pd.DataFrame, N: int):
    """
    Features generation
    - this section is to generate some features for the xgboost regression model to predict the stock price
    """
    # add lags up to N number of days to use as features
    df_lags = add_lags(df, N, ["close"])

    """
        Shift label column and drop invalid samples
    """
    df_lags["close"] = df_lags["close"].shift(-1)

    df_lags = df_lags.loc[10:]  # because of close_lag_10
    df_lags = df_lags[:-1]  # because of shifting close price

    """
        train, validation, test split
        70% on train, 15% on validation, 15% on test
    """
    test_size = 0.15
    val_size = 0.15

    test_split_idx = int(df_lags.shape[0] * (1 - test_size))
    val_split_idx = int(df_lags.shape[0] * (1 - (val_size + test_size)))

    df_train = df_lags.loc[:val_split_idx].copy()
    df_val = df_lags.loc[val_split_idx + 1 : test_split_idx].copy()
    df_test = df_lags.loc[test_split_idx + 1 :].copy()

    # drop unnecessary columns
    drop_cols = ["date", "order_day"]

    df_train = df_train.drop(drop_cols, axis=1)
    df_val = df_val.drop(drop_cols, axis=1)
    df_test = df_test.drop(drop_cols, axis=1)

    # split into features and labels
    X_train = df_train.drop(["close"], axis=1)
    y_train = df_train["close"]

    X_val = df_val.drop(["close"], axis=1)
    y_val = df_val["close"]

    X_test = df_test.drop(["close"], axis=1)
    y_test = df_test["close"]

    return X_train, y_train, X_val, y_val, X_test, y_test


# def main():
def do_forecast(ticker: str) -> pl.DataFrame:
    ticker_code = ticker

    # variables
    prev_date = (
        date.today()
    )  # dont need the "-timedelta(days=1)" as the end in stock.history already takes T-1 day
    date_3_years_ago = date.today() - timedelta(days=1) - relativedelta(years=3)
    prev_date_formatted = prev_date.strftime("%Y-%m-%d")
    date_3_years_ago_formatted = date_3_years_ago.strftime("%Y-%m-%d")

    try:
        stock_df = get_stock_price(
            ticker_code, date_3_years_ago_formatted, prev_date_formatted
        )
        logger.info(f"obtained stock df, with the shape of {stock_df.shape}...")
    except AttributeError:
        logger.info("incorrect ticker code provided, please enter again...")
        ticker_code = ticker
        stock_df = get_stock_price(
            ticker_code, date_3_years_ago_formatted, prev_date_formatted
        )
        logger.info("obtained stock df...")
    except:
        logger.error("something else went wrong...")

    stock_df_mod = stock_df.drop(
        ["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"],
        axis=1,
    )

    # Change all column headings to be lower case, and remove spacing
    stock_df_mod.columns = [
        str(x).lower().replace(" ", "_") for x in stock_df_mod.columns
    ]

    N = 10  # define number of days to lag
    X_train, y_train, X_val, y_val, X_test, y_test = create_dfs(stock_df_mod, N)

    logger.info("split stock_df into training, val, and test sets...")
    logger.info(f"the shape for X_train is {X_train.shape}")
    logger.info(f"the shape for X_val is {X_val.shape}")
    logger.info(f"the shape for df_test is {X_test.shape}")

    start = time.time()
    eval_set = [(X_train, y_train), (X_val, y_val)]
    model = xgb.XGBRegressor(
        colsample_bytree=0.9,
        learning_rate=0.03,
        max_depth=8,
        min_child_weight=3,
        n_estimators=200,
        subsample=0.65,
    )

    model.fit(X_train, y_train, eval_set=eval_set, verbose=True)

    # Forecast 3 business days into future
    future = date_by_adding_business_days_l(
        prev_date - timedelta(days=1), 4
    )  # here we need to do prev_date - timedelta(days=1) because we still want to forecast for the current day (i.e. today)
    df_future = pd.DataFrame(future, columns=["date"])

    df_future_pred = pd.concat([stock_df_mod, df_future], axis=0).reset_index(drop=True)
    df_future_pred_lags = add_lags(df_future_pred, N, ["close"])
    drop_cols = ["date", "order_day"]
    df_future_pred_lags = df_future_pred_lags.drop(drop_cols, axis=1)
    X_future_pred = df_future_pred_lags.drop(["close"], axis=1)[-4:]

    # NOTE: Can only predict next day good, subsequent dates aren't great...
    forecast = model.predict(X_future_pred)
    df_forecast = df_future_pred[-4:].copy()
    df_forecast["close"] = forecast

    logger.info(f"prediction for the next day is {forecast[0]}")
    end = time.time()
    logger.info(f"XGB regression model and prediction took {end-start} seconds")

    # wrangle dataframe to return
    df_hist = stock_df[["Date", "Close"]].rename(
        columns={"Date": "date", "Close": "value"}
    )
    df_forecast = df_forecast.rename(columns={"close": "value"})
    df_full = pd.concat([df_hist, df_forecast], axis=0).reset_index(drop=True)
    df_full["date"] = pd.to_datetime(df_full["date"]).dt.date

    # convert the pandas df into a list of dict
    df_full_dict = df_full.to_dict("records")

    return df_full_dict


# if __name__ == "__main__":
#     main()
