import time
from datetime import datetime
import os
import sys
from types import FunctionType
from unittest import result

def trying(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            raise(e)
        finally:
            return result
    return wrapper

def process_batch(*args, **kwargs):
    if len(args) > 0 and type(args[0]) is FunctionType:
        return __decorador(args[0])
    else:
        if len(args) == 1:
            return __decorador_param(args[0])
        elif len(args) > 1:
            raise Exception("Too many arguments")

        if 'log' in kwargs:
            return __decorador_param(kwargs['log'])
        elif 'log_name' in kwargs:
            return __decorador_param(kwargs['log_name'])
        elif 'process' in kwargs:
            return __decorador(kwargs['process'])
        elif 'process_name' in kwargs:
            return __decorador(kwargs['process_name'])
        else:
            raise Exception("No log name received")

def time_elapsed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"[{datetime.now()}] - Inicia la ejecución de {func.__name__}")
        result = func(*args, **kwargs)
        print(f'[{datetime.now()}] - Finaliza la ejecución de {func.__name__}, demoró {time.time() - start} segundos')
        return result
    return wrapper

def __decorador_param(log_name: str = None):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log = f"logs/{log_name}_{datetime.now().strftime('%Y%m%d')}"
    sys.stdout = open(f'{log}.log', 'a')
    sys.stderr = open(f'{log}.err', 'a')
    def wrapper(func):
        def subwrapper(*args, **kwargs):
            start = time.time()
            print(f"[{datetime.now()}] - Inicia la ejecución de {func.__name__}")
            result = func(*args, **kwargs)
            print(f'[{datetime.now()}] - Finaliza la ejecución de {func.__name__}, demoró {time.time() - start} segundos')
            sys.stdout.close()
            sys.stderr.close()
            return result
        return subwrapper
    return wrapper

def __decorador(func):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log = f"logs/{datetime.now().strftime('%Y%m%d')}"
    sys.stdout = open(f'{log}.log', 'a')
    sys.stderr = open(f'{log}.err', 'a')
    def subwrapper(*args, **kwargs):
        start = time.time()
        print(f"[{datetime.now()}] - Inicia la ejecución de {func.__name__}")
        result = func(*args, **kwargs)
        print(f'[{datetime.now()}] - Finaliza la ejecución de {func.__name__}, demoró {time.time() - start} segundos')
        sys.stdout.close()
        sys.stderr.close()
        return result
    return subwrapper
