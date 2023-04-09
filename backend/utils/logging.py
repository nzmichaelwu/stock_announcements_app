import logging
import sys
from pathlib import Path


def set_up_logging(
    logger: logging.Logger, file_loc: Path, level: int = logging.INFO
) -> None:
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(funcName)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream_handler.setFormatter(formatter)

    logger.handlers = []  # remove any old handlers in case run multiple times
    logger.addHandler(stream_handler)
    if file_loc:
        file_handler = logging.FileHandler(file_loc)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
