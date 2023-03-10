import json
import logging
import os
import re
import sys
import typing as T
import urllib
from datetime import datetime as dt
from socket import timeout

import ipykernel
import pandas as pd
import psutil
from jupyter_server import serverapp
from notebook import notebookapp
from traitlets.config import MultipleInstanceError


class DotDict(T.Dict[str, T.Any]):
    """Allows dot notation for access to dictionary attributes

    Both get and set attributes are available

    Examples:
        ::

            dd = DotDict({'a': 1, 'b':2})
            dd.a + dd.b # 3

            dd2 = DotDict(msg1 = 'hello', msg2 = 'world')
            print(f'{dd2.msg1} {dd2.msg2}') # hello world

            dd3 = DotDict(longer_name = spark.createDataFrame(pd.DataFrame({'a': [1,2]})))
            dd3.alias('longer_name', 'short_name')
            dd3.short_name
    """

    def __getattr__(self, *args: T.Any):
        val = self.get(*args)
        return DotDict(val) if type(val) is dict else val

    def __setattr__(self, key: str, val: T.Any) -> None:
        return self.__setitem__(key, val)

    def __delattr__(self, key):
        return self.__delitem__(key)

    def alias(self, tname, newname):
        self[newname] = self[tname]
        return self


def notebook_path(verbose=False):
    """Returns the absolute path of the Notebook or None if it cannot be determined
    NOTE: works only when the security is token-based or there is also no password

    see https://stackoverflow.com/a/52187331


    tested on python file run as a notebook via jupytext. Will give a RunTimeError if just calling the file as a module

    verbose: if True, prints a ton of output, don't use normally. To remove when functionality bedded down

    """
    connection_file = os.path.basename(ipykernel.get_connection_file())
    if verbose:
        print(connection_file)
    kernel_id = connection_file.split("-", 1)[1].split(".")[0]
    if verbose:
        print("---connection file and associated kernelid:---")
        print(connection_file)
        print(f"kernel_id:{kernel_id}")
        print("------------")

    # support both jupyterlab v2 and v3:
    oldstyle_servers = [x for x in notebookapp.list_running_servers()]
    newstyle_servers = [x for x in serverapp.list_running_servers()]
    if verbose:
        print("---notebookapp servers (Jlab v <3):---")
        print(oldstyle_servers)
        print("---serverapp servers (Jlab v >= 3):---")
        print(newstyle_servers)
        print("---end servers---")

    if verbose:
        print("---begin iterating through servers---")

    for srv in oldstyle_servers + newstyle_servers:
        nbkdir = srv.get("notebook_dir", srv.get("root_dir"))
        try:
            if (
                srv["token"] == "" and not srv["password"]
            ):  # No token and no password, but token may be present in env
                envtoken = os.environ.get(
                    "JPY_API_TOKEN", os.environ.get("JUPYTERHUB_API_TOKEN")
                )

                if verbose:
                    print("--No token listed, get token from environment")
                # TO DO: handle case where this key is not present, e.g. ben setup from console
                req = urllib.request.urlopen(
                    srv["url"] + f"api/sessions?token={envtoken}", timeout=2
                )  # sometimes seems to stall, hence timeout
            else:
                if verbose:
                    print("---assuming token, requesting sessions from:---")
                    print(f"url:{srv['url']+'api/sessions?token='+srv['token']}")

                    print("---^end url to request sessions from---")
                req = urllib.request.urlopen(
                    srv["url"] + "api/sessions?token=" + srv["token"], timeout=2
                )

            sessions = json.load(req)
            if verbose:
                print(f"sessions:{sessions}")

            for sess in sessions:
                if verbose:
                    print(f"kernelid:{sess['kernel']['id']}")
                if sess["kernel"]["id"] == kernel_id:
                    if verbose:
                        print("a hit!")
                        print(f"notebook_dir:{nbkdir}")
                        # original has sess['notebook']['path'] - maybe different b/c jupytext?
                        print(f"sess notebook path:{sess['path']}")
                    return os.path.join(nbkdir, sess["path"])
        except (
            urllib.error.URLError,
            TimeoutError,
            timeout,
        ) as inst:  # think we have the relevant ones! # 2021-07-23 added timeout from socket
            if verbose:
                print("exception handled:")
                print(type(inst))  # the exception instance
                print(inst.args)  # arguments stored in .args
                print(inst)
            pass  # There may be stale entries in the runtime directory
    return "unknown_source."  # if we got here, we didn't find a match


def fileloc(input_globals, depth=2, verbose=False):
    """Return the name of the running file, suitable for use as a logfile name

    Tested on:
        - running python -m filename
        - Private and Official Jupyterlab instances, v2 & v3
        - Running actual .ipynb notebook
        - running filename.py as a notebook in Jupyterlab via jupytext
        - running filename.py in Jupyterlab console
        - running individual lines via commandline
        - running individual lines via IPython

    arg:
        input_globals: pass globals() from the calling module so we get the right filename
        depth: (int) number of directory/file levels to roll up
        verbose: whether to spill a lot of debug info

    """

    if "__file__" in input_globals:
        if verbose:
            print("__file__ in globals, use that")
        pyfile = input_globals["__file__"]
    else:
        try:
            pyfile = notebook_path(verbose=verbose)
        except (
            RuntimeError,
            MultipleInstanceError,
        ):  # multiple instance if running ipython shell
            pyfile = "manual_run."

    return "_".join(".".join(pyfile.split(".")[:-1]).split("/")[(-1 * depth) :])


def setup_logging(loggername, filename=None, add_ts=False):
    """Common logging setup

    loggername: Typically pass __name__ from calling module
    filename:   Output logfile to write, in addition to stderr
    add_ts:     Boolean, whether to treat the filename like a prefix and add timestamp.
                Extension will be preserved if present.

    Example usage in calling script/notebook, assuming a config file loaded as cfg:
        import bidsutil as hf
        pyfile = hf.fileloc(globals())
        logger = hf.setup_logging(__name__, f'{cfg.out.LOGS}/{pyfile}.txt', add_ts=True)
        logger.l = lambda ls: logger.lbase(ls, globals())
        logname = logger.handlers[1].baseFilename.split('/')[-1].split('.')[0]

    """

    def lbase(logstring, g):
        """simple logging of counts etc"""
        rslt = eval(logstring, g)
        nl = "\n" if type(rslt) == pd.core.frame.DataFrame else " "
        internal_logger.info(f"{logstring}:{nl}{rslt}")

    internal_logger = logging.getLogger(loggername)
    logger_format = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch = logging.StreamHandler()
    ch.setFormatter(logger_format)
    ch.setLevel(logging.DEBUG)

    log_time = dt.now().strftime("%Y%m%d%H%M%S")

    # determining the filename to write:
    filename = filename or "run_logger.txt"
    if add_ts:
        name_parts = filename.split(".")
        if len(name_parts) == 1:
            name_parts += ["txt"]
        filename = f'{".".join(name_parts[:-1])}_{log_time}.{name_parts[-1]}'

    # create dirs if needed
    if len(filename.split("/")) > 1:
        fpath = "/".join(filename.split("/")[:-1])
        os.makedirs(fpath, exist_ok=True)

    fh = logging.FileHandler(filename, mode="w")
    fh.setFormatter(logger_format)
    fh.setLevel(logging.DEBUG)

    internal_logger.addHandler(ch)
    internal_logger.addHandler(fh)
    internal_logger.setLevel(logging.DEBUG)

    print(f"logging to:{filename}", file=sys.stderr)

    internal_logger.lbase = lbase

    return internal_logger


# function to format long number into human readable format
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return "%.2f%s" % (num, ["", "K", "M", "B"][magnitude])


def get_mem():
    return psutil.Process(os.getpid()).memory_infor().rss / 1024**2
