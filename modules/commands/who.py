__author__ = 'tinglev@kth.se'

import modules.slack as slack

def run(channel_id, user):
    slack.presence(channel_id, user)
