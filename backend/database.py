# import libraries
import pandas as pd
from datetime import date, datetime
import sys, os
import subprocess
import yaml
from backend.src.util import DotDict

from sqlalchemy import create_engine

cfg = DotDict(yaml.safe_load(open('backend/config_db.yml')))


# function to get data from hotcopper table
def get_hotcopper():
  # Get required database params
  DATABASE_URL = 'postgresql://' + cfg.db.user + ":" + cfg.db.password + "@" + cfg.db.host + ":" + str(cfg.db.port) + "/" + cfg.db.name
  postgresql_engine = create_engine(DATABASE_URL)

  cols = ['index', 'ticker', 'announcement', 'price_sensitive', 'date_time']
  d_list = postgresql_engine.execute("Select distinct * from announcements").fetchall()
  df = (
    pd.DataFrame(d_list, columns=cols) \
      .drop('index', axis=1) \
        .sort_values('date_time', ascending=True) \
          .drop_duplicates(subset=['ticker', 'announcement', 'price_sensitive'], keep='first') \
            .reset_index(drop=True)
  )
  
  postgresql_engine.dispose()

  return df


# function to get data from market index table
def get_marketindex():
  # Get required database params
  DATABASE_URL = 'postgresql://' + cfg.db.user + ":" + cfg.db.password + "@" + cfg.db.host + ":" + str(cfg.db.port) + "/" + cfg.db.name
  postgresql_engine = create_engine(DATABASE_URL)

  market_cap_mod = []
  cols = ['index', 'ticker', 'name', 'price', 'market_cap', 'extract_timestamp']
  d_list = postgresql_engine.execute("Select * from market_index").fetchall()
  df = pd.DataFrame(d_list, columns=cols)
  df['market_cap'] = df['market_cap'].str.replace('$','')
  df[['market_cap_num', 'market_cap_unit']] = df['market_cap'].str.split(expand=True)
  for i, unit in enumerate(df['market_cap_unit']):
    if unit == 'B':
      market_cap_mod.append(float(df['market_cap_num'].loc[i]) * 1000000000)
    elif unit == 'M':
      market_cap_mod.append(float(df['market_cap_num'].loc[i]) * 1000000)
    elif unit == 'TH':
      market_cap_mod.append(float(df['market_cap_num'].loc[i]) * 1000)
    else:
      market_cap_mod.append(float(df['market_cap_num'].loc[i]))
  df['market_cap_mod'] = market_cap_mod

  df.drop(['index', 'market_cap_num', 'market_cap_unit'], axis=1, inplace=True)

  postgresql_engine.dispose()

  return df

df_marketindex = get_marketindex()