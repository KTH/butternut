__author__ = 'tinglev@kth.se'

import logging

import modules.cache as cache

log = logging.getLogger(__name__)

def get_channels(client):
    '''
    Gets public Channels (https://api.slack.com/types/channel) and the channels where the 
    application has read rights or is invited as a member.
    '''
    call_name = "conversations.list"
    cache_key = f"{call_name}-client"

    cache_item = cache.fetch(cache_key, cache.ONE_DAY)

    if cache_item is not None:
        return cache_item

    channels = client.api_call(call_name)
    
    cache.add(cache_key, channels)

    return channels

def get_channel(client, channel_name):
    '''
    Gets a Channel (https://api.slack.com/types/channel) for a channel name like 'general'.
    '''
    channels = get_channels(client)
    for channel in channels["channels"]:
        if channel["name"] == channel_name:
            return channel


def get_channel_id(client, channel_name):
    '''
    Gets a Channel (https://api.slack.com/types/channel) id like U0DTX9MJ5 for a channel name like 'general'.
    '''
    channel = get_channel(client, channel_name)
    if channel is not None:
        return channel["id"]


def get_channel_members(client, channel_id):
    '''
    Gets a list of User id strings that are user_idsfor a channel name like 'general'.
    '''
    call_name = "conversations.members"
    cache_key = f"{call_name}-{channel_id}"

    cache_item = cache.fetch(cache_key, cache.ONE_DAY)

    if cache_item is not None:
        return cache_item

    result = list()

    channel = client.api_call(
        call_name,
        channel=channel_id
    )
    result = channel["members"]
    cache.add(cache_key, result)

    return result

def get_channel_users_by_channel_id(client, channel_id):
    '''
    Gets the members of a channel as list of Users (https://api.slack.com/types/user).
    '''
    result = list()

    user_ids = get_channel_members(client, channel_id)
    if user_ids is None:
        return result

    for user_id in user_ids:
        user = get_user(client, user_id)
        if user is not None:
            result.append( add_user_presence(client, user))

    return result

def get_channel_users_by_channel_name(client, channel_name):
    '''
    Gets the members of a channel as list of Users (https://api.slack.com/types/user).
    '''
    return get_channel_members(client, get_channel_id(client, channel_name))

def get_user(client, user_info_id):
    '''
    Gets a User (https://api.slack.com/types/user) for its id (i.e: U02KDKE01).
    If the Users exists, but the user has been deleted, None will be returned.
    Also not bots are considered beeing a human. Sorry HAL. 
    '''
    call_name = "users.info"
    cache_key = f"{call_name}-{user_info_id}"

    cache_item = cache.fetch(cache_key, cache.ONE_HOUR)

    if cache_item is not None:
        return cache_item

    result = list()

    response = client.api_call(
        call_name,
        user=user_info_id
    )

    if response["ok"]:
        user = response["user"]

        if user["is_bot"]:
            return None

        if user["deleted"]:
            return None

        if is_status_emoji(user, ":palm_tree:"):
            return None

        cache.add(cache_key, user)

        return user

def get_user_attribute(user, attribute_name):
    if user is not None:
        return user[attribute_name]


def is_user_working_remotely(user):
    '''
    If the userhas set her status emoji to 
    :house_with_garden:, she is considerd to be working remotely.
    '''
    if is_status_emoji(user, ":house_with_garden:"):
        return True
    return False


def get_users_working_remotely(client, channel_name):
    '''
    If the member of a channel has set her status emoji to 
    :house_with_garden:, she is considerd to be working remotely.
    '''
    result = list()
    users = get_channel_users_by_channel_name(client, channel_name)
    for user in users:
        if is_user_working_remotely(user):
            result.append(user)

    return result
    
def add_user_presence(client, user):
    '''
    Adds a users presence. Active or Away.
    '''
    call_name = "users.getPresence"
    cache_key = f"{call_name}-{user['id']}"

    cache_item = cache.fetch(cache_key, cache.ONE_MINUTE)

    if cache_item is not None:
        user["presence"] = cache_item
        return user

    response = client.api_call(
        call_name,
        user=user["id"]
    )

    cache.add(cache_key, response["presence"])
    user["presence"] = response["presence"]
    
    return user

def get_user_dm(user):
    return f'slack://user?team={get_user_attribute(user, "team_id")}&id={get_user_attribute(user, "id")}'

def is_user_present(user):
    if "active" in get_user_attribute(user, "presence"):
        return True
    return False


def get_profile(user):
    '''
    Gets the profile attribute from the User (https://api.slack.com/types/user). 
    '''
    if user is not None:
        return user["profile"]


def get_profile_attribute(user, attribute_name):
    if user is not None:
        profile = get_profile(user)
        if profile is not None:
            return profile[attribute_name]


def get_profile_status_emoji(user):
    '''
    Gets the status emoji from user.profile.
    '''

    return get_profile_attribute(user, "status_emoji")


def get_profile_full_name(user):
    '''
    Gets the real name from user.profile.
    '''
    return get_profile_attribute(user, "real_name")


def get_profile_avatar(user):
    '''
    Gets the avtar from user.profile.
    '''

    return get_profile_attribute(user, "image_24")


def is_status_emoji(user, status_emoji):
    '''
    Check if the users profiles status emoji is of a certain type.
    '''
    profile_status_emoji = get_profile_status_emoji(user)
    if profile_status_emoji is not None:
       if status_emoji in profile_status_emoji:
            return True
    return False
