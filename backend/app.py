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
from flask import Flask, jsonify
from flask_cors import CORS
from backend.database import get_hotcopper, get_marketindex

sys.path.append('..')
from helper_funcs.helper_funcs import util as hf


cfg = hf.DotDict(yaml.safe_load(open('config.yml')))

# pyfile = hf.fileloc(globals())
# logger = hf.setup_logging(__name__, f'{cfg.out.LOGS}/{pyfile}.txt', add_ts=True); logger.l = lambda ls: logger.lbase(ls, globals())
# logname = logger.handlers[1].baseFilename.split('/')[-1].split('.')[0]

# gitstat = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], capture_output=True)
# git_commit_short_sha = gitstat.stdout[:7].decode('utf-8')
# logger.l('git_commit_short_sha')
# logger.info(f"Git Branch:\n{subprocess.check_output(['git', 'branch']).decode('utf8')}")

# configuration
DEBUG = True

# define app
app = Flask(__name__)
app.config.from_object(__name__)

# CORS(app, resources={r"/*":{'origins':"*"}})
CORS(app)

# load data
df_hotcopper = get_hotcopper()
# logger.info(f'the shape of df_hotcopper is {df_hotcopper.shape}.')

df_market_idx = get_marketindex()
# logger.info(f'the shape of df_market_idx is {df_market_idx.shape}.')


# combine into a big df
df_all = df_market_idx.merge(df_hotcopper, how='left', on='ticker')


df_table = df_all[['ticker', 'name', 'price', 'market_cap_mod', 'announcement', 'price_sensitive', 'date_time']] \
  .rename(columns={'market_cap_mod': 'market_cap', 'date_time': 'announcement_time'})
df_table[['announcement', 'price_sensitive', 'announcement_time']] = df_table[['announcement', 'price_sensitive', 'announcement_time']].fillna(value='')

df_table_dict = df_table.to_dict('records') # convert the pandas df into a list of dict
df_table_dict_json = json.dumps(df_table_dict)  # convert the list of dict into a json object

### Route stuff ----
# display table
@app.route('/', methods=['GET'])
def all_data():
  # return df_table.to_json(orient='records')
  # return df_table_dict_json
  return jsonify(
    items=df_table_dict,
    status=200
  )


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=1234)