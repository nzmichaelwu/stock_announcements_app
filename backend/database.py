# import libraries
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime
from re import sub
from turtle import pos

import pandas as pd
import polars as pl
import yaml
from extensions import TIMEOUT, cache, logger
from pyparsing import col
from sqlalchemy import column, create_engine
from src.util import DotDict, get_mem

cfg = DotDict(yaml.safe_load(open("config_db.yml")))


# function to get data from hotcopper table
def get_hotcopper():
    start = time.time()
    logger.debug(f"connecting to DB and grabing HotCopper data...")
    # Get required database params
    DATABASE_URL = (
        "postgresql://"
        + cfg.db.user
        + ":"
        + cfg.db.password
        + "@"
        + cfg.db.host
        + ":"
        + str(cfg.db.port)
        + "/"
        + cfg.db.name
        + "?sslmode=require"
    )
    postgresql_engine = create_engine(DATABASE_URL)

    query = "Select distinct * from announcements"
    df = (
        pl.from_pandas(pd.read_sql(query, postgresql_engine))
        .lazy()
        .drop("index")
        .sort("date_time")
        .unique(subset=["ticker", "announcement", "price_sensitive"], keep="first")
        .collect()
    )

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    end = time.time()
    logger.info(f"{end-start} secs used to get announcements data...")
    return df


# function to get data from market index table
def get_marketindex():
    start = time.time()
    logger.debug(f"connecting to DB and grabing Market Index data...")
    # Get required database params
    DATABASE_URL = (
        "postgresql://"
        + cfg.db.user
        + ":"
        + cfg.db.password
        + "@"
        + cfg.db.host
        + ":"
        + str(cfg.db.port)
        + "/"
        + cfg.db.name
        + "?sslmode=require"
    )
    postgresql_engine = create_engine(DATABASE_URL)

    query = "Select * from market_index"
    df = (
        pl.from_pandas(pd.read_sql(query, postgresql_engine))
        .lazy()
        .with_column(pl.col("market_cap").str.replace(r"\$", "").alias("market_cap"))
        .with_columns(
            pl.col("market_cap").str.extract(r"(\d+(\.\d+)?)").alias("market_cap_num"),
            pl.col("market_cap")
            .str.replace(r"(\d+(\.\d+)?)", "")
            .alias("market_cap_unit"),
        )
        .with_column(
            pl.when(pl.col("market_cap_unit") == "B")
            .then(pl.col("market_cap_num").cast(pl.Float64) * 1000000000)
            .otherwise(
                pl.when(pl.col("market_cap_unit") == "M")
                .then(pl.col("market_cap_num").cast(pl.Float64) * 1000000)
                .otherwise(
                    pl.when(pl.col("market_cap_unit") == "TH")
                    .then(pl.col("market_cap_num").cast(pl.Float64) * 1000)
                    .otherwise(pl.col("market_cap_num"))
                )
            )
            .alias("market_cap_mod")
        )
        .drop(["index", "market_cap_num", "market_cap_unit"])
        .collect()
    )

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    end = time.time()
    logger.info(f"{end-start} secs used to get market_index data...")
    return df


# generic function to get news article tables
def get_news(
    query: str, engine, index_col, dt_col, col_to_unique_on: list
) -> pl.DataFrame:
    df = (
        pl.from_pandas(pd.read_sql(query, engine))
        .lazy()
        .drop(index_col)
        .rename({dt_col: "date_time"})
        .sort("date_time")
        .unique(subset=[*col_to_unique_on], keep="first")
        .collect()
    )
    return df


# function to get data from afr tables
def get_afr():
    start = time.time()
    logger.debug(f"connecting to DB and grabing AFR data...")
    # Get required database params
    DATABASE_URL = (
        "postgresql://"
        + cfg.db.user
        + ":"
        + cfg.db.password
        + "@"
        + cfg.db.host
        + ":"
        + str(cfg.db.port)
        + "/"
        + cfg.db.name
        + "?sslmode=require"
    )
    postgresql_engine = create_engine(DATABASE_URL)

    query_homepage = "Select * from afr_homepage"
    query_afr_street_talk = "Select * from afr_street_talk"

    df_afr_homepage = get_news(
        query_homepage, postgresql_engine, "index", "extract_ts", ["headline"]
    )

    df_afr_street_talk = get_news(
        query_afr_street_talk, postgresql_engine, "index", "extract_ts", ["headline"]
    )

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    end = time.time()
    logger.info(f"{end-start} secs used to get afr data...")
    return df_afr_homepage, df_afr_street_talk


# function to get data from The Australian tables
def get_aus():
    start = time.time()
    logger.debug(f"connecting to DB and grabing The Australian data...")
    # Get required database params
    DATABASE_URL = (
        "postgresql://"
        + cfg.db.user
        + ":"
        + cfg.db.password
        + "@"
        + cfg.db.host
        + ":"
        + str(cfg.db.port)
        + "/"
        + cfg.db.name
        + "?sslmode=require"
    )
    postgresql_engine = create_engine(DATABASE_URL)

    query_aus_homepage = "Select * from aus_homepage"
    query_aus_dataroom = "Select * from aus_dataroom"
    query_aus_tradingday = "Select * from aus_tradingday"

    df_aus_homepage = get_news(
        query_aus_homepage, postgresql_engine, "index", "extract_ts", ["heading"]
    )

    df_aus_dataroom = get_news(
        query_aus_dataroom,
        postgresql_engine,
        "index",
        "extract_ts",
        ["heading", "summary"],
    )

    df_aus_tradingday = get_news(
        query_aus_tradingday,
        postgresql_engine,
        "index",
        "extract_ts",
        ["heading", "summary"],
    )

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    end = time.time()
    logger.info(f"{end-start} secs used to get aus data...")
    return df_aus_homepage, df_aus_dataroom, df_aus_tradingday
