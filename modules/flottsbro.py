__author__ = 'tinglev@kth.se'

import os
from json.decoder import JSONDecodeError
import logging
import log as log_module
import urllib.parse    
from requests import get

log_module.init_logging()
log = logging.getLogger(__name__)


def get_deployment(monitor_url):
    logger = logging.getLogger(__name__)
    api_url = os.environ.get('FLOTTSBRO_API_URL')
    if not api_url:
        api_url = 'https://api.kth.se'

    api_key = os.environ.get('FLOTTSBRO_API_KEY')
    if not api_key:
        api_key = '1234'

    endpoint_url = '{}/api/pipeline/v1/monitor/active/{}'.format(api_url, url_encode(monitor_url))

    log.debug('Looking for a monitor pattern using "%s"', endpoint_url)

    try:
        result = get(endpoint_url, headers={'api_key': api_key })
        if result is None:
            logger.info('Got no response for {}'.format(endpoint_url))
            return None

        return result.json()

    except JSONDecodeError as json_err:
        logger.exception('Error when calling flottsbro with endpoint {}.'.format(endpoint_url))
        return None

def url_encode(string):
    return urllib.parse.quote_plus(str(string))

def get_monitor_pattern(monitor_url):
    deployment = get_deployment(monitor_url)
    if deployment is None:
        return 'APPLICATION_STATUS: OK'
    if "monitorPattern" in deployment:
        return deployment["monitorPattern"]
    return 'APPLICATION_STATUS: OK'
