__author__ = 'tinglev@kth.se'

import re
import modules.helpers as helpers
import modules.slack as slack

def run(split_commands, channel, user):
    if len(split_commands) != 3:
        return 'Usage: *health [cluster] [service_name]*'
    else:
        slack.give_me_a_second(channel, user)
        script_path = '/root/util/hemavan.sh'
        cluster = split_commands[1]
        service = split_commands[2]
        response = helpers.run_with_output(f'{script_path} {cluster} {service}')
        try:
            response = response.decode('utf-8')
        except AttributeError:
            pass
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        no_ansi_escapes = ansi_escape.sub('', response)
        return f'Health check for *{service}* on *{cluster}* gave:```{no_ansi_escapes}```'
