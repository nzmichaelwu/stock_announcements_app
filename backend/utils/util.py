import os

import psutil


# function to format long number into human readable format
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return "%.2f%s" % (num, ["", "K", "M", "B"][magnitude])


def get_mem():
    return psutil.Process(os.getpid()).memory_info().rss / 1024**2
