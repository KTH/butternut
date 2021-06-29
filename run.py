import time
import sys
import logging
from requests import get
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError
from docker.errors import APIError

import log as log_module
import modules.slack as slack
import modules.docker as docker
import modules.commands.status as cmd_status
import modules.commands.health as cmd_health
import modules.commands.logs as cmd_logs
import modules.commands.services as cmd_services
import modules.commands.tasks as cmd_tasks
import modules.commands.help as cmd_help
import modules.commands.management as cmd_management
import modules.commands.backup as cmd_backup
import modules.commands.who as who
import modules.graylog as graylog
import modules.flottsbro as flottsbro

log_module.init_logging()
log = logging.getLogger(__name__)


def skip_retry_for_url(url):

    retry = False

    if "app.kth.se" in url:
        retry = True

    if "api.kth.se" in url:
        retry = True

    if "www.kth.se" in url:
        retry = True

    if retry:
        log.debug('Url "%s" does not have a _monitor path', url)
        return False

    return True


def get_monitor_response(url, channel):

    result = None

    try:

        result = get(url, timeout=15)

    except (ReadTimeout, ConnectionError) as error:
        slack.send_message(channel, ('UpTimeRobot is correct. I could not connect to {},'
                                     ' the request timed out :weary: ```\n{}\n```'
                                     .format(url, error)))
    except:
        slack.send_message(channel, ('I failed to check if {} is down '
                                     'or not, I got a reponse {} '
                                     .format(url, sys.exc_info()[0])))

    return result

def handle_utr_down(monitor_url, channel):

    if skip_retry_for_url(monitor_url):
        return

    monitor_pattern = flottsbro.get_monitor_pattern(monitor_url)
    response = get_monitor_response(monitor_url, channel)

    log.info('Monitor pattern for "%s" is "%s".', monitor_url, monitor_pattern)
    log.info('Monitor response is "%s".', response)
    
    # Got no response from the monitor url at all
    if response is None:
        slack.send_message(channel, 'Could not get any response from the service.')
        send_importance(monitor_url, channel)
        slack.send_message(channel, graylog.get_snippet(monitor_url))
    # Might work again?
    elif is_monitor_ok_again(response.status_code, response.text, monitor_pattern):
        slack.send_message(channel, 'Looks like an application reload that took to long, works for :robot_face: @Everest Bot! (Could be that a replica died)')
    # The monitor pages says ERROR.
    else:
        message = ""
        if response.text is not None:
            message = response.text[:250]
        slack.send_message(channel, (':face_with_head_bandage: <!here> {} does not contain `{}`: ```\n{}\n```'.format(monitor_url, monitor_pattern, message)))
        send_importance(monitor_url, channel)
        slack.send_message(channel, graylog.get_snippet(monitor_url))

def send_importance(monitor_url, channel):
    deployment = flottsbro.get_deployment(monitor_url)

    # How fast should the service be back?
    if deployment is not None:
        importance = deployment["importance"]
        friendlyName = deployment["friendlyName"]
        if "high" in importance:
            msg = (':importance-high: High priority | *15 minutes* during office hours for action to be started, and within *one hour during On call hours*  for {}.'.format(friendlyName))
            slack.send_message(channel, msg)
        elif "medium" in importance:
            msg = (':importance-medium: Medium | *2 hours* during office hour, *next morning otherwise* for {}.'.format(friendlyName))
            slack.send_message(channel, msg)
        else:
            msg = (':importance-low: Low |  You got a *1 day* to start working on a solution.'.format(friendlyName))
            slack.send_message(channel, msg)


def is_monitor_ok_again(status_code, responseBody, monitor_pattern):
    if status_code == 200:
        if monitor_pattern in responseBody:
            return True
    return False


def ping(split_commands):
    try:
        cmd_status.run(split_commands)
    except:
        log.info('Ping (sevice status) failed.')


def handle_command(command, channel, user):
    try:
        log.info('Handling cmd "%s" on ch "%s" and user "%s"',
                 command, channel, user)
        default_response = 'Not sure what you mean. Use *@Everest Bot help* for help'
        split_commands = command.split(' ')

        cmd = split_commands[0]
        response = None
        if cmd in slack.commands:
            ping(split_commands)
            if cmd == 'services':
                response = cmd_services.run(split_commands, channel, user)
            if cmd == 'tasks':
                response = cmd_tasks.run(split_commands, channel, user)
                if response:
                    response = "{}{}".format(response, cmd_logs.run_as_subtask(split_commands, channel, user))
            if cmd == 'status':
                response = cmd_status.run(split_commands)
            if cmd == 'health':
                response = cmd_health.run(split_commands, channel, user)
            if cmd == 'logs':
                response = cmd_logs.run(split_commands, channel, user)
            if cmd == 'help':
                response = cmd_help.run()
            if cmd == 'management':
                response = cmd_management.run()
            if cmd == 'backup':
                response = cmd_backup.run()
            if cmd == 'who':
                response = who.run(channel, user)
        else:
            response = cmd_help.run()

    except (APIError, ReadTimeout) as docker_err:
        log.error('Got error from docker api: %s', docker_err)
        response = ('Sorry, the :whale: refused to do as it was told. Try again ...\n'
                    '```{}```'.format(docker_err))
    if response is not None:
        slack.send_ephemeral(channel, user, response, default_response)


def main():
    try:
        if slack.init():
            docker.init()
            log.info("Everest Bot connected and running!")

            while True:
                log.debug('Check for new messages sent to the bot.')
                rtm_messages = []
                try:
                    rtm_messages = slack.get_rtm_messages(slack.rtm_read())
                except Exception:
                    log.warn('Timeout when reading from Slack')
                if len(rtm_messages) > 0:
                    log.debug('Got %s messages since last update',
                              len(rtm_messages))
                for message in rtm_messages:
                    log.debug('Handling message "%s"', message)
                    command, user, channel = slack.message_is_direct_mention(
                        message)
                    if command:
                        handle_command(command, channel, user)
                    url, channel = slack.message_is_utr_down(message)
                    if url:
                        handle_utr_down(url, channel)
                time.sleep(slack.rtm_read_delay)
        else:
            log.error("Connection to Slack failed!")
    except Exception as err:
        log.error (f'Oh :poop:, I died and had to restart myself. {err}')
        raise


if __name__ == "__main__":
    main()
