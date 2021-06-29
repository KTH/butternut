__author__ = 'tinglev@kth.se'

import modules.helpers as helpers
import modules.docker as docker
import modules.process as process

def get_system_status(cluster):
    return str(process.run_with_output(f'/root/util/status.sh {cluster}'))


def run(split_commands):
    docker.load_clusters()
    response = 'The current running clusters are: ```'
    # Write header
    response += helpers.create_header_row([('Name', 40), ('Status', 0)])
    for client in docker.clients:
        response += helpers.create_row([(client['data']['name'], 40),
                                       (client['data']['status'], 0)])
                            

    # Does not work, process not run with docker working.
    #response += get_system_status('stage')

    return response + '```'
