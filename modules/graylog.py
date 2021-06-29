__author__ = 'tinglev@kth.se'

import urllib.parse    
from datetime import datetime, timedelta
import modules.flottsbro as flottsbro

def get_snippet(monitor_url):

    deployment = flottsbro.get_deployment(monitor_url)

    if not deployment_ok(deployment):
        return ''

    return (
        ':mag: Logs at the time of the incident for {}.\n{}'
        .format(deployment['imageName'], _build_greylog_search_link(deployment))
    )


def _build_greylog_search_link(deploymnet):

    query = _build_search_query(deploymnet)
    query_interval = timedelta(minutes=2)

    to_date = datetime.utcnow()
    from_date = to_date - query_interval

    to_date = url_encode(to_date.isoformat()[:-3] + 'Z')
    from_date = url_encode(from_date.isoformat()[:-3] + 'Z')

    url = (
        'https://graycloud.ite.kth.se/search?rangetype=absolute&'
        'fields=message%2Csource&from={}&to={}&q={}'
        .format(from_date, to_date, query)
    )

    return url

def _build_search_query(deployment):
    if deployment_ok(deployment):
        cluster = deployment['cluster']
        image_name = deployment['imageName']
        version = deployment['version']

        return (
            'source%3A{}+AND+image_name%3A/.%2A'
            '{}%3A{}.%2A/'.format(cluster, image_name, version)
        )

def deployment_ok(deployment):
    if deployment is None:
        return False
        
    return ('cluster' in deployment and
            'imageName' in deployment and
            'version' in deployment)

def url_encode(string):
    return urllib.parse.quote_plus(str(string))