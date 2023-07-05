import json
from time import time
from typing import Callable
from interaction.cmd_args import cmd_args
from interaction.metric_printer import print_metric

def run_with_time(fun: Callable, *args, **kwargs):
    start_time = time()
    result = fun(*args, **kwargs)
    end_time = time()
    secs = end_time - start_time
    print_metric({'type': 'time', 'data': {'name': fun.__name__, 'time': secs}})
    return result