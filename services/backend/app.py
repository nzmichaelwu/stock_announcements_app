# import libraries
import json
import os, time, sys
import pandas as pd
import numpy as np
import yaml
import subprocess
from datetime import datetime

from quart import Quart, jsonify
from quart_cors import cors
# from flask import Flask, jsonify
# from flask_cors import CORS

from database import get_hotcopper, get_marketindex, get_afr, get_aus

# configuration
DEBUG = True

# define app
app = Quart(__name__)
# app.config.from_object(__name__)

# CORS(app, resources={r"/*":{'origins':"*"}})
app = cors(app, allow_origin="*")


# load announcements data
def load_announcements_data():
  # call get_hotcopper
  df_hotcopper = get_hotcopper()

  # call get_marketindex
  df_market_idx = get_marketindex()

  # combine into a big df
  df_all = df_market_idx.merge(df_hotcopper, how='left', on='ticker')
  df_table = df_all[['ticker', 'name', 'price', 'market_cap_mod', 'announcement', 'price_sensitive', 'date_time']] \
    .rename(columns={'market_cap_mod': 'market_cap', 'date_time': 'announcement_time'})

  # add $ sign in front of the price
  df_table['price'] = df_table['price'].apply(lambda x: '$' + str(x))

  df_table[['announcement', 'price_sensitive', 'announcement_time']] = df_table[['announcement', 'price_sensitive', 'announcement_time']].fillna(value='')

  df_table_dict = df_table.to_dict('records') # convert the pandas df into a list of dict

  return df_table_dict


# load news data
def load_news_data():
  # call get_afr
  df_afr_homepage, df_afr_street_talk = get_afr()

  # call get_aus
  df_aus_homepage, df_aus_dataroom, df_aus_tradingday = get_aus()

  # combine the Aus section dfs
  df_aus_sections = pd.concat([df_aus_dataroom, df_aus_tradingday], axis=0)

  # create a dictionary to store all dfs in JSON
  dfs_dict = {}
  jsdf_afr_homepage = df_afr_homepage.to_json(orient='records')
  jsdf_afr_street_talk = df_afr_street_talk.to_json(orient='records')
  jsdf_aus_homepage = df_aus_homepage.to_json(orient='records')
  jsdf_aus_sections = df_aus_sections.to_json(orient='records')

  dfs_dict['afr_homepage'] = json.loads(jsdf_afr_homepage)
  dfs_dict['afr_street_talk'] = json.loads(jsdf_afr_street_talk)
  dfs_dict['aus_homepage'] = json.loads(jsdf_aus_homepage)
  dfs_dict['aus_sections'] = json.loads(jsdf_aus_sections)

  return dfs_dict


### Route stuff ----
# display announcements table
@app.route('/contents', methods=['GET'])
async def announcements_data():
  return jsonify(
    items=load_announcements_data(),
    status=200
  )

# display news tables
@app.route('/contents/news', methods=['GET'])
async def news_data():
  return jsonify(
    items=load_news_data(),
    status=200
  )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=1234)