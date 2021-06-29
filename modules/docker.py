__author__ = 'tinglev@kth.se'

import os
import logging
from requests import get
from docker import DockerClient, tls, APIClient

log = logging.getLogger(__name__)
clusters = None
clients = []
local_client = None
timeout = 5
tls_config=tls.TLSConfig(
        client_cert=('/root/.docker/cert.pem', '/root/.docker/key.pem'),
        ca_cert='/root/.docker/ca.pem',
        verify=True
    )

def init():
    if not os.environ.get('KEYSTONE_API_URL'):
        return

    global local_client
    local_client = DockerClient(base_url='unix://var/run/docker.sock', timeout=timeout)
    load_clusters()

def get_clusters():
    return get('{}/status'.format(os.environ.get('KEYSTONE_API_URL'))).json()

def load_clusters():
    clients.clear()
    for cluster in get_clusters():
        log.debug('Loading cluster: {}'.format(cluster))
        clients.append({
            'data': cluster,
            'client': DockerClient(base_url=cluster['load_balancer_ip'], tls=tls_config, timeout=timeout),
            'api': APIClient(base_url=cluster['load_balancer_ip'], tls=tls_config, timeout=timeout)
        })


def get_client_for_cluster(cluster):
    if not local_client:
        log.debug('Keystone not configured')

    load_clusters()

    for client in clients:
        if client['data']['status'] == cluster.lower():
            return client['client']


def get_api_for_cluster(cluster):
    if not local_client:
        log.debug('Keystone not configured')

    for client in clients:
        if client['data']['status'] == cluster.lower():
            return client['api']


def get_services_for_client(client):
    if client is None:
        return None
    
    return client.services.list()


def get_logs_for_api(api, service_name, nr_of_rows):
    return api.service_logs(service_name, stderr=True, stdout=True, tail=nr_of_rows)

def get_local_containers():
    return local_client.containers.list()
