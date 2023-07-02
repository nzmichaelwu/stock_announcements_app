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
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error
from utils.logging import set_up_logging

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
holiday_start = date(2033, 1, 1)


# Get stock quote
def get_stock_price(ticker, startdate, enddate) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    stock_df = pd.DataFrame(stock.history(start=startdate, end=enddate).reset_index())
    stock_df["Date"] = stock_df["Date"].dt.tz_localize(None)
    return stock_df


# Function to return holiday df
def get_holiday() -> pd.DataFrame:
    year_range = [year for year in range(holiday_start.year, holiday_start.year + 1)]

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
def create_dfs(stock_df):
    df = stock_df.drop(
        ["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"],
        axis=1,
    )

    # Change all column headings to be lower case, and remove spacing
    df.columns = [str(x).lower().replace(" ", "_") for x in df.columns]

    ### Prophet ---
    # prepare expected column names
    df.columns = ["ds", "y"]
    df["ds"] = pd.to_datetime(df["ds"])

    # # Visualize data using seaborn
    # sns.set(rc={"figure.figsize": (12, 8)})
    # sns.lineplot(x=df["ds"], y=df["y"])
    # plt.legend(["TLS"])
    # plt.show()

    # Split data into train and test (80% vs 20%)
    test_size = 0.2
    test_split_idx = int(df.shape[0] * (1 - test_size))

    df_train = df.loc[:test_split_idx].copy()
    df_test = df.loc[test_split_idx + 1 :].copy()

    return df_train, df_test


# Baseline Prophet model
def train_baseline_model(df_train, df_test) -> Prophet:
    # Initiate the model
    baseline_model = Prophet()  # Fit the model on the training dataset

    baseline_model.fit(df_train)

    # Cross validation
    baseline_model_cv = cross_validation(
        model=baseline_model,
        initial="60 days",
        period="3 days",
        horizon="3 days",
        parallel="processes",
    )

    # Model performance metrics
    baseline_model_p = performance_metrics(baseline_model_cv, rolling_window=1)

    # Get the performance metric value
    logger.info(f'MAE for baseline model: {baseline_model_p["mae"].values[0]}')
    logger.info(f'RMSE for baseline model: {baseline_model_p["rmse"].values[0]}')

    # Evaluation on test set using the baseline_model
    df_pred_baseline = baseline_model.predict(df_test)
    yhat_baseline = df_pred_baseline["yhat"]
    actuals = df_test["y"]
    logger.info(f"MAE on test set: {mean_absolute_error(actuals, yhat_baseline)}")
    logger.info(
        f"RMSE on test set: {mean_squared_error(actuals, yhat_baseline, squared=False)}"
    )

    # # plots
    # baseline_model.plot(df_pred_baseline)
    # plt.show()

    # baseline_model.plot_components(df_pred_baseline)
    # plt.show()

    return baseline_model


# Hyperparameter tuning
def hyper_param_tune(df_train):
    # Set up parameter grid
    param_grid = {
        "changepoint_prior_scale": [0.001, 0.01, 0.05],
        "seasonality_prior_scale": [0.01, 1, 5, 10],
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
            m,
            initial="60 days",
            period="3 days",
            horizon="3 days",
            parallel="processes",
        )

        # Model performance
        df_p = performance_metrics(df_cv, rolling_window=1)

        # Save model performance metrics
        maes.append(df_p["mae"].values[0])

    # Tuning results
    tuning_results = pd.DataFrame(all_params)
    tuning_results["mae"] = maes  # Find the best parameters
    best_params = all_params[np.argmin(maes)]
    logger.info(f"best_params: {best_params}")

    return best_params


def train_tuned_model(df_train, df_test, best_params) -> Prophet:
    # Fit the model using the best parameters
    tuned_model = Prophet(
        changepoint_prior_scale=best_params["changepoint_prior_scale"],
        seasonality_prior_scale=best_params["seasonality_prior_scale"],
        seasonality_mode=best_params["seasonality_mode"],
    )

    # Fit the model on the training dataset
    tuned_model.fit(df_train)

    # Cross validation
    tuned_model_cv = cross_validation(
        tuned_model,
        initial="60 days",
        period="3 days",
        horizon="3 days",
        parallel="processes",
    )

    # Model performance metrics
    tuned_model_p = performance_metrics(tuned_model_cv, rolling_window=1)

    # Get the performance metric value
    logger.info(f'MAE for tuned model: {tuned_model_p["mae"].values[0]}')
    logger.info(f'RMSE for tuned model: {tuned_model_p["rmse"].values[0]}')

    # Evaluation on test set using the tuned_model
    df_pred_tuned = tuned_model.predict(df_test)
    yhat_tuned = df_pred_tuned["yhat"]
    actuals = df_test["y"]
    logger.info(f"MAE on test set: {mean_absolute_error(actuals, yhat_tuned)}")
    logger.info(
        f"RMSE on test set: {mean_squared_error(actuals, yhat_tuned, squared=False)}"
    )

    # # plots
    # tuned_model.plot(df_pred_baseline)
    # plt.show()

    # tuned_model.plot_components(df_pred_baseline)
    # plt.show()
    return tuned_model


# def main():
def do_forecast(ticker: str) -> pl.DataFrame:
    ticker_code = ticker

    # variables
    prev_date = (
        date.today()
    )  # dont need the "-timedelta(days=1)" as the end in stock.history already takes T-1 day
    date_3_mths_ago = date.today() - timedelta(days=1) - relativedelta(months=3)
    prev_date_formatted = prev_date.strftime("%Y-%m-%d")
    date_3_mths_ago_formatted = date_3_mths_ago.strftime("%Y-%m-%d")

    try:
        stock_df = get_stock_price(
            ticker_code, date_3_mths_ago_formatted, prev_date_formatted
        )
        logger.info("obtained stock df...")
    except AttributeError:
        logger.info("incorrect ticker code provided, please enter again...")
        ticker_code = ticker
        stock_df = get_stock_price(
            ticker_code, date_3_mths_ago_formatted, prev_date_formatted
        )
        logger.info("obtained stock df...")
    except:
        logger.error("something else went wrong...")

    df_train, df_test = create_dfs(stock_df)

    logger.info("split stock_df into training and test set...")
    logger.info(f"the shape for df_train is {df_train.shape}")
    logger.info(f"the shape for df_test is {df_test.shape}")

    start = time.time()
    # baseline_model = train_baseline_model(df_train, df_test)
    best_params = hyper_param_tune(df_train)
    tuned_model = train_tuned_model(df_train, df_test, best_params)

    # Forecast 3 business days into future
    future = date_by_adding_business_days_l(
        prev_date - timedelta(days=1), 4
    )  # here we need to do prev_date - timedelta(days=1) because we still want to forecast for the current day (i.e. today)
    df_future = pd.DataFrame(future, columns=["ds"])

    logger.info(f"best_params: \n{best_params}")
    forecast = tuned_model.predict(df_future)
    logger.info("prediction for the next day...")
    logger.info(f"\n{forecast.loc[0]}")
    # tuned_model.plot(forecast)
    # plt.show()
    end = time.time()
    logger.info(f"hyper tuned model and prediction took {end-start} seconds")

    # wrangle dataframe to return
    df_hist = stock_df[["Date", "Close"]].rename(
        columns={"Date": "labels", "Close": "values"}
    )
    df_forecast = forecast[["ds", "yhat"]].rename(
        columns={"ds": "labels", "yhat": "values"}
    )
    df_full = pd.concat([df_hist, df_forecast], axis=0).reset_index(drop=True)

    # convert pandas into polars
    df_full_pl = pl.from_pandas(df_full)
    return df_full_pl


# if __name__ == "__main__":
#     main()
