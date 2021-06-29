__author__ = 'tinglev@kth.se'

import modules.slack as slack
import modules.docker as docker
import logging
import modules.commands.services as cmd_services

log = logging.getLogger(__name__)

def run(split_commands, channel, user):
    if len(split_commands) != 4:
        return 'Usage: *logs [cluster] [service] [nr of rows (default 30)]*\n I.e: logs active kopps-public 40'
    else:
        slack.give_me_a_second(channel, user)
        cluster = split_commands[1]
        service_name = split_commands[2]
        nr_of_rows = split_commands[3]

        response = run_query(channel, user, cluster, service_name, nr_of_rows)

        if response:
            return response

        response = 'I could´t find any application matching *{}* in *{}*.\n'.format(service_name, cluster)
        response += 'Use one of the following:\n{}'.format(cmd_services.run_as_subtask(cluster, channel, user))

        return response

def run_as_subtask(split_commands, channel, user):
    if len(split_commands) != 3:
        return ""

    cluster = split_commands[1]
    service_name = split_commands[2]
    result = run_query(channel, user, cluster, service_name, nr_of_rows=5)

    if result:
        return result

    return ""

def run_query(channel, user, cluster, service_name, nr_of_rows=5):
    cluster_client = docker.get_client_for_cluster(cluster)
    api_client = docker.get_api_for_cluster(cluster)
    services = docker.get_services_for_client(cluster_client)

    if services:
        if (int(nr_of_rows) > 200):
            return "I say :zipper_mouth_face:, maximum number of rows to show is *200*, "
        
        for service in services:
            if service_name in service.name:
                response = ""
                header = ('Here are the last *{}* lines of logs for *{}* on *{}*, hope it helps :kissing_heart:'
                            .format(nr_of_rows, service.name, cluster))
                for row in docker.get_logs_for_api(api_client, service.name, nr_of_rows):
                    response += '\n{}'.format(row.decode('utf8', 'ignore'))

                response_length = len("{}".format(response))
                if response_length > 10000:
                    return '{}\n```{}```\n:scissors: Only showing the last 10 000 lines of log.'.format(header, response[(response_length - 10000):])
                
                return '{}\n```{}```'.format(header, response)

    return None
