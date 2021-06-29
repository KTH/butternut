import os
import time
import json
import tempfile
import logging
import ast
from pathlib import Path

log = logging.getLogger(__name__)

ONE_SECOND = 1
TEN_SECOND = ONE_SECOND * 10
ONE_MINUTE = ONE_SECOND * 60 
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24
DEFAULT_TIMEOUT = ONE_MINUTE

def fetch(cache_key, timeout=DEFAULT_TIMEOUT):
    if exists(cache_key, timeout):
        log.debug(f"Using cache for '{cache_key}'.")
        return file_read(cache_key)
    return None


def add(cache_key, value):
    log.debug(f"Adding cache item for '{cache_key}'.")
    file_write(cache_key, value)


# --------------------------------------------------------

def exists(cache_key, timeout=DEFAULT_TIMEOUT):
    if cache_file_exists(cache_key):
        return is_cache_item_active(cache_key, timeout)
    return False


def cache_file_exists(cache_key):
    return Path(get_file_path(cache_key)).exists()

def get_file_name(cache_key):
    return f"{cache_key}.json"


def get_file_path(cache_key):
    return f"{tempfile.gettempdir()}/{get_file_name(cache_key)}"


def file_write(cache_key, value):
    file = open(get_file_path(cache_key),  "a")
    file.write(json.dumps(value))
    file.close()


def file_read(cache_key):
    content = None
    with open(get_file_path(cache_key), 'r') as cache_file:
        content = cache_file.read()

    return json.loads(content)


def file_created(cache_key):
    result = os.path.getmtime(get_file_path(cache_key))
    print(f"Created: {result}")
    return result

    
def is_cache_item_active(cache_key, timeout=DEFAULT_TIMEOUT):
    created = file_created(cache_key)
    age = time.time() - created

    log.debug(f"Cache file for key {cache_key} is {age} seconds old, should not be older then {timeout} seconds." )

    if age > timeout :
        log.debug(f"  Cache file for {cache_key} is outdated, removing it." )
        os.remove(get_file_path(cache_key))
        return False

    log.debug(f"  Cache file {cache_key} is still valid, it got {(timeout - age)} seconds left." )
    return True

