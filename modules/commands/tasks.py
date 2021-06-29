__author__ = 'tinglev@kth.se'

import modules.docker as docker
import modules.slack as slack
import modules.helpers as helpers
import modules.commands.services as cmd_services

def run(split_commands, channel, user):

    response = ""

    if len(split_commands) != 3:
        return 'Usage: *tasks [cluster] [service]*'
    else:
        slack.give_me_a_second(channel, user)
        cluster = split_commands[1]
        service_name = split_commands[2]
        client = docker.get_client_for_cluster(cluster)
        
        for service in docker.get_services_for_client(client):
            if service_name in service.name:
                response = ('Tasks for service *{}* running on *{}* are:```'
                            .format(service_name, cluster))
                response += helpers.create_header_row([('Image', 40), ('State', 10),
                                                      ('Since', 35), ('Exit code', 10),
                                                      ('Error', 0)])
                for task in service.tasks():
                    image_name = task['Spec']['ContainerSpec']['Image']
                    image_name = clean_image_name(image_name)
                    state = task['Status']['State']
                    since = task['Status']['Timestamp']
                    if 'ContainerStatus' in task['Status']:
                        exit_code = str(task['Status']['ContainerStatus']['ExitCode'])
                    else:
                        exit_code = 'N/A'
                    err = ''
                    if 'Err' in task['Status']:
                        err = task['Status']['Err']
                    response += helpers.create_row([(image_name, 40), (state, 10),
                                                   (since, 35), (exit_code, 10), (err, 0)])
                return response + '```\n'

    response = 'I could´t find any application matching *{}* in *{}*.\n'.format(service_name, cluster)
    response += 'Use one of the following:\n{}'.format(cmd_services.run_as_subtask(cluster, channel, user))

    return response


def clean_image_name(image_name):
    if '@' in image_name:
        image_name = image_name.split('@')[0]
    if '/' in image_name:
        image_name = image_name.split('/')[1]
    return image_name
