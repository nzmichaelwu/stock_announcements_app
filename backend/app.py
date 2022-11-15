# import libraries
from crypt import methods
from distutils.debug import DEBUG
import json
import os, time, sys
from unicodedata import category
import pandas as pd
import numpy as np
import yaml
import subprocess
import datetime as dt
from flask import Flask, jsonify
from flask_cors import CORS
from backend.database import get_hotcopper, get_marketindex

sys.path.append('..')
from helper_funcs.helper_funcs import util as hf


cfg = hf.DotDict(yaml.safe_load(open('config.yml')))


# configuration
DEBUG = True

# define app
app = Flask(__name__)
app.config.from_object(__name__)

# CORS(app, resources={r"/*":{'origins':"*"}})
CORS(app)


# load data
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


### Route stuff ----
# display announcements table
@app.route('/contents', methods=['GET'])
def all_data():
  return jsonify(
    items=load_announcements_data(),
    status=200
  )


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=1234)