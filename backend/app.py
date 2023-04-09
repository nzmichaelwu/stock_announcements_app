# import libraries
import json
import logging
import time
from datetime import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
import yaml
from box import Box
from database import get_afr, get_aus, get_hotcopper, get_marketindex
from flask import Flask, jsonify
from flask_cors import CORS
from utils.logging import set_up_logging
from utils.util import get_mem

cfg = Box(yaml.safe_load(open("config_db.yml")))

### set up logging and other params ----
logger = logging.getLogger()
LOG_DIR = Path(f"{cfg.out.LOGS}")
LOG_DIR.mkdir(parents=True, exist_ok=True)

RUN_Date = dt.today().strftime("%Y%m%d")

log_dir_exp = LOG_DIR / f"app_logs_{RUN_Date}"
log_dir_exp.mkdir(parents=True, exist_ok=True)
set_up_logging(logger, log_dir_exp / "logs.txt")  # appends to file by default if exists


# configuration
DEBUG = True

logger.info("starting the app")

# define app
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


# load announcements data
def load_announcements_data():
    logger.info(f"Loading announcement data...")
    start_time = time.time()

    # call get_hotcopper
    df_hotcopper = get_hotcopper()

    # call get_marketindex
    df_market_idx = get_marketindex()

    # combine into a big df
    df_table = (
        df_market_idx.join(df_hotcopper, on="ticker", how="left")
        .select(
            "ticker",
            "name",
            "$" + pl.col("price").cast(pl.Utf8),
            "market_cap_mod",
            pl.col("announcement").fill_null(""),
            pl.col("price_sensitive").fill_null(""),
            pl.col("date_time").fill_null(""),
        )
        .rename(
            {
                "literal": "price",
                "market_cap_mod": "market_cap",
                "date_time": "announcement_time",
            }
        )
    )

    df_table_dict = df_table.to_pandas().to_dict(
        "records"
    )  # convert the pandas df into a list of dict

    end_time = time.time()

    if len(df_table_dict) != 0:
        logger.info(
            f"Loaded announcement data... time taken: {end_time - start_time} seconds, memory being used: {get_mem()}"
        )
    else:
        logger.warning(f"No announcement data, size = {len(df_table_dict)}")

    return df_table_dict


# load news data
def load_news_data():
    logger.debug(f"Loading news data...")
    start_time = time.time()

    # call get_afr
    df_afr_homepage, df_afr_street_talk = get_afr()

    # call get_aus
    df_aus_homepage, df_aus_dataroom, df_aus_tradingday = get_aus()

    # combine the Aus section dfs
    df_aus_sections = pl.concat([df_aus_dataroom, df_aus_tradingday])

    # create a dictionary to store all dfs in JSON
    dfs_dict = {}
    jsdf_afr_homepage = df_afr_homepage.to_pandas().to_json(orient="records")
    jsdf_afr_street_talk = df_afr_street_talk.to_pandas().to_json(orient="records")
    jsdf_aus_homepage = df_aus_homepage.to_pandas().to_json(orient="records")
    jsdf_aus_sections = df_aus_sections.to_pandas().to_json(orient="records")

    dfs_dict["afr_homepage"] = json.loads(jsdf_afr_homepage)
    dfs_dict["afr_street_talk"] = json.loads(jsdf_afr_street_talk)
    dfs_dict["aus_homepage"] = json.loads(jsdf_aus_homepage)
    dfs_dict["aus_sections"] = json.loads(jsdf_aus_sections)

    end_time = time.time()

    if len(dfs_dict) != 0:
        logger.info(
            f"Loaded news data... time taken: {end_time - start_time} seconds, memory being used: {get_mem()}"
        )
    else:
        logger.warning(f"No news data, size = {len(dfs_dict)}")

    return dfs_dict


### Route stuff ----
# display announcements table
@app.route("/api/contents", methods=["GET"])
async def announcements_data():
    return jsonify(items=load_announcements_data(), status=200)


# display news tables
@app.route("/api/contents/news", methods=["GET"])
async def news_data():
    return jsonify(items=load_news_data(), status=200)


if __name__ == "__main__":
    app.run(port=1234)
