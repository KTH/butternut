__author__ = 'tinglev@kth.se'

import modules.helpers as helpers


def run():
    help_text = 'Hi! These are commands that I :robot_face: understand: \n\n'
    help_text += 'Shows the status of all clusters\n_@Everest Bot_ `status`\n\n'
    help_text += 'Runs a healthcheck for a given service and cluster\n_@Everest Bot_ `health active niseko-api_api`\n\n'
    help_text += 'Show services running on the given cluster\n_@Everest Bot_ `services stage`\n\n'
    help_text += 'Show the tasks associated with the given service\n_@Everest Bot_ `tasks active kopps-web_web`\n\n'
    help_text += 'Show the last number of loglines for a service\n_@Everest Bot_ `logs active kopps-web_web 40`\n\n'
    help_text += 'Shows info on containers running on the management vm\n_@Everest Bot_ `management`\n\n'
    help_text += 'Shows list of configured backups\n_@Everest Bot_ `backup`\n\n'
    help_text += 'Who is online in this channel?\n_@Everest Bot_ `who`\n\n'

    return help_text


