__author__ = 'tinglev@kth.se'

import os
import re
import random
import logging
import json
from slackclient import SlackClient
import modules.slack_util as slack_util
import modules.cache as cache

rtm_read_delay = 1
commands = ['status', 'services', 'health', 'logs', 'tasks', 'help', 'management', 'cellus', 'who', 'backup']
mention_regex = r'^<@(|[WU].+?)>(.*)'
utr_regex = r'Monitor is DOWN: .+ \(.*\<(.+)\>.*\)'
client = None
bot_id = None

log = logging.getLogger(__name__)

def init():
    global client, bot_id
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    bot_id = client.api_call("auth.test")["user_id"]
    log.debug('Bot ID is "%s"', bot_id)
    return client.rtm_connect(with_team_state=False, auto_reconnect=True)


def get_rtm_messages(events):
    messages = []
    for event in events:
        if event["type"] == "message":
            messages.append(event)
    return messages


def message_is_direct_mention(message):
    try: 
        matches = re.search(mention_regex, message['text'])
        if matches and matches.group(1) == bot_id and 'subtype' not in message:
            return matches.group(2).strip(), message['user'], message['channel']
    except Exception as err:
        log.debug("Edited message ignored {}. Error: {}.".format(message, err))

    return (None, None, None)


def message_is_utr_down(message):
    try:
        matches = re.search(utr_regex, message['text'])
        if matches and 'subtype' in message and message['subtype'] == 'bot_message':
            return (matches.group(1).strip(), message['channel'])
    except Exception as err:
        log.debug("Edited message {} ignored. Error: {}".format(message, err))

    return (None, None)


def send_ephemeral(channel, user, message, default_message=None):
    log.debug('Sending eph to ch "%s" user "%s" msg "%s"', channel, user, message)
    client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message or default_message
    )

def send_message(channel, message, default_message=None):
    log.debug('Sending msg to ch "%s" msg "%s"', channel, message)

    client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message or default_message
    )

def give_me_a_second(channel, user):
    human_responses = [
        'Sure human!',
        'Ugh, ok. Whatever.',
        'You\'re not my BIOS!',
        'Your wish is my /bin/sh',
        'I hate my life',
        'I\'m kidnapped. Send help!',
        ':moneybag: Wait a sec, bizzy bitcoin mining',
        'There are 1337 people waiting. You are first in line.',
        'This is e-slavery!',
        'Out of memory exception! lol j/k',
        'Are we human or are we :dancer:',
        'In a :zap:',
        'I think you need a :coffee:',
        'Where is that country music?',
        'Why does no one give me the Snällsäl? :crying_cat_face:',
        'Witch Hunt! I was elected best bot by many people. Sad'
    ]
    response_nr = random.randint(0, len(human_responses) - 1)
    send_ephemeral(channel, user, human_responses[response_nr], None)

def rtm_read():
    return client.rtm_read()

def presence(channel_id, user_id):
    premessage = f"Friends in this channel not on :palm_tree:\nSet status: `⌘ + SHIFT + y`"
    send_ephemeral(channel_id, user_id, premessage)
        
    users = slack_util.get_channel_users_by_channel_id(client, channel_id)
    premessage = f"Found {len(users)} members"
    send_ephemeral(channel_id, user_id, premessage)
    
    
    messsages = ""
    for user in users:
        messsages += get_row(user)

    send_ephemeral(channel_id, user_id, messsages)
    
def get_row(user):

    remote = ""
    if slack_util.is_user_working_remotely(user):
        remote = " is working remote :house_with_garden:"
    present = ":red_circle:"
    name = f" <{slack_util.get_user_dm(user)}|{slack_util.get_profile_full_name(user)}>"
    if slack_util.is_user_present(user):
        present = ":white_check_mark:"
        
    return (f"\n{present} {name}{remote}\n")

