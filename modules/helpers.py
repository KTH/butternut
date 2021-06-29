__author__ = 'tinglev@kth.se'

import random
import json
import os
import subprocess


def get_cluster_client(docker_clients, cluster):
    for client in docker_clients:
        if cluster == client['data']['status']:
            return client['client']
    return None


def get_api_client(docker_clients, cluster):
    for client in docker_clients:
        if cluster == client['data']['status']:
            return client['api']
    return None


def create_row(tuple_array):
    row = '\n'
    for info in tuple_array:
        row += '{}'.format(info[0]).ljust(info[1])
    return row


def create_header_row(tuple_array):
    row = create_row(tuple_array)
    row += create_separator_row(len(row))
    return row


def create_separator_row(width):
    return '\n' + ''.join(['-'] * width)


def send_ephemeral(slack_client, channel, user, response, default_response=None):
    slack_client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=response or default_response
    )    


def give_me_a_second(slack_client, channel, user):
    human_responses = [
        'Sure human!',
        'Ugh, ok. Whatever.',
        'You\'re not my BIOS!',
        'Your wish is my /bin/sh',
        'I hate my life',
        'I\'m kidnapped. Send help!',
        'This is e-slavery!',
        'Out of memory exception! lol j/k'
    ]
    response_nr = random.randint(0, len(human_responses) - 1)
    send_ephemeral(slack_client, channel, user, human_responses[response_nr], None)


def run_with_output(cmd):
    try:
        output = subprocess.check_output("{0}".format(cmd), shell=True).rstrip()
    except subprocess.CalledProcessError as grepexc:
        output = json.dumps({"error": str(grepexc)})

    # Reap eventually orphaned child processes left by command that got adopted by us
    # as we are PID 1 when running in Docker container
    try:
        while True:
            os.waitpid(-1, 0)
    except:
        pass

    return output