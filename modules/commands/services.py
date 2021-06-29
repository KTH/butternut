__author__ = 'tinglev@kth.se'

import modules.helpers as helpers
import modules.slack as slack
import modules.docker as docker
import logging

log = logging.getLogger(__name__)

def run(split_commands, channel, user):
    if len(split_commands) != 2:
        return 'Usage: *services [cluster]*'
    else:
        cluster = split_commands[1]
        return run_query(cluster, channel, user)
 
def run_as_subtask(cluster, channel, user):
    return run_query(cluster, channel, user)

def run_query(cluster, channel, user):

    log.info("Getting services in cluster{}".format(cluster))

    client = docker.get_client_for_cluster(cluster)
    services = docker.get_services_for_client(client)

    if services:
        response = '```'
        response += helpers.create_header_row([('Name', 50), ('Mode', 15),
                                                ('Replicas', 0)])

        for service in services:
            if 'Replicated' in service.attrs['Spec']['Mode']:
                replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
                response += helpers.create_row([(service.name, 50), 
                                                ('Replicated', 15), (replicas, 0)])
            else:
                response += helpers.create_row([(service.name, 50), ('Global', 0)])
        
        return '{}```\n'.format(response)

    return None