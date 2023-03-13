# import libraries
import os
import re
import subprocess
import sys
from datetime import date, datetime
from re import sub
from turtle import pos

import pandas as pd
import yaml
from extensions import TIMEOUT, cache, logger
from pyparsing import col
from sqlalchemy import column, create_engine
from src.util import DotDict, get_mem

cfg = DotDict(yaml.safe_load(open("config_db.yml")))


# function to get data from hotcopper table
def get_hotcopper():
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
    )
    postgresql_engine = create_engine(DATABASE_URL)

    cols = ["index", "ticker", "announcement", "price_sensitive", "date_time"]
    d_list = postgresql_engine.execute(
        "Select distinct * from announcements"
    ).fetchall()
    df = (
        pd.DataFrame(d_list, columns=cols)
        .drop("index", axis=1)
        .sort_values("date_time", ascending=True)
        .drop_duplicates(
            subset=["ticker", "announcement", "price_sensitive"], keep="first"
        )
        .reset_index(drop=True)
    )

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    return df


# function to get data from market index table
def get_marketindex():
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
    )
    postgresql_engine = create_engine(DATABASE_URL)

    market_cap_mod = []
    cols = ["index", "ticker", "name", "price", "market_cap", "extract_timestamp"]
    d_list = postgresql_engine.execute("Select * from market_index").fetchall()
    df = pd.DataFrame(d_list, columns=cols)
    df["market_cap"] = df["market_cap"].apply(lambda x: x.replace("$", ""))
    df["market_cap"] = df["market_cap"].apply(
        lambda x: re.sub("(\d+(\.\d+)?)", r" \1 ", x)
    )
    df[["market_cap_num", "market_cap_unit"]] = df["market_cap"].str.split(expand=True)
    for i, unit in enumerate(df["market_cap_unit"]):
        if unit == "B":
            market_cap_mod.append(float(df["market_cap_num"].loc[i]) * 1000000000)
        elif unit == "M":
            market_cap_mod.append(float(df["market_cap_num"].loc[i]) * 1000000)
        elif unit == "TH":
            market_cap_mod.append(float(df["market_cap_num"].loc[i]) * 1000)
        else:
            market_cap_mod.append(float(df["market_cap_num"].loc[i]))
    df["market_cap_mod"] = market_cap_mod

    df.drop(["index", "market_cap_num", "market_cap_unit"], axis=1, inplace=True)

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    return df


# function to get data from afr tables
def get_afr():
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
    )
    postgresql_engine = create_engine(DATABASE_URL)

    cols_afr_homepage = ["index", "headline", "date_time"]
    d_list_afr_homepage = postgresql_engine.execute(
        "Select * from afr_homepage"
    ).fetchall()
    df_afr_homepage = (
        pd.DataFrame(d_list_afr_homepage, columns=cols_afr_homepage)
        .drop("index", axis=1)
        .sort_values("date_time", ascending=True)
        .drop_duplicates(subset=["headline"], keep="first")
        .reset_index(drop=True)
    )

    cols_afr_street_talk = ["index", "headline", "summary", "date_time"]
    d_list_afr_street_talk = postgresql_engine.execute(
        "Select * from afr_street_talk"
    ).fetchall()
    df_afr_street_talk = (
        pd.DataFrame(d_list_afr_street_talk, columns=cols_afr_street_talk)
        .drop("index", axis=1)
        .sort_values("date_time", ascending=True)
        .drop_duplicates(subset=["headline"], keep="first")
        .reset_index(drop=True)
    )

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    return df_afr_homepage, df_afr_street_talk


# function to get data from The Australian tables
def get_aus():
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
    )
    postgresql_engine = create_engine(DATABASE_URL)

    cols_aus_homepage = ["index", "category", "headline", "date_time"]
    d_list_aus_homepage = postgresql_engine.execute(
        "Select * from aus_homepage"
    ).fetchall()
    df_aus_homepage = (
        pd.DataFrame(d_list_aus_homepage, columns=cols_aus_homepage)
        .drop("index", axis=1)
        .sort_values("date_time", ascending=True)
        .drop_duplicates(subset=["headline"], keep="first")
        .reset_index(drop=True)
    )

    cols_aus_section = ["index", "category", "headline", "summary", "date_time"]
    sections = ["aus_dataroom", "aus_tradingday"]

    df_dict = {}

    for section in sections:
        d_list = postgresql_engine.execute(f"Select * from {section}").fetchall()
        df = (
            pd.DataFrame(d_list, columns=cols_aus_section)
            .drop("index", axis=1)
            .sort_values("date_time", ascending=True)
            .drop_duplicates(subset=["headline", "summary"], keep="first")
            .reset_index(drop=True)
        )
        df_dict[section] = df

    df_aus_dataroom = df_dict["aus_dataroom"]
    df_aus_tradingday = df_dict["aus_tradingday"]

    postgresql_engine.dispose()

    logger.debug(f"memory being used: {get_mem()}")

    return df_aus_homepage, df_aus_dataroom, df_aus_tradingday
