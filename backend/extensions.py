import logging
import os

import yaml
from flask_caching import Cache
from src.util import DotDict

cfg = DotDict(yaml.safe_load(open("config_db.yml")))
TIMEOUT = cfg.timeout
environment = os.getenv("ENV")

cache = Cache()

FORMAT = "[%(asctime)s %(filename)s:%(lineno)s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
log_level = logging.DEBUG if environment == "DEBUG" else logging.INFO
logger.setLevel(log_level)
