import json
import logging

from django.conf import settings

from slack import WebClient

log = logging.getLogger(__name__)
slack_client = WebClient(token=settings.SLACK_OAUTH_TOKEN)


def get_file_permalink(slack_event):
    """ Gets the permalink for a file """
    if not slack_event.file_ids:
        log.exception('No file ids found')
        return

    file_id = slack_event.file_ids[0]
    file_info = slack_client.files_info(file=file_id)

    if not file_info.get('ok'):
        log.exception(file_info.get('error'))
        return
    return (file_info.get('file', {}).get('permalink')
            or file_info.get('file', {}).get('url_private'))


def get_channel_permalink(slack_event):
    """ Retrieves the team info and constructs a permalink to the
    Slack channel

    Returns the Slack channel permalink """
    if not slack_event.channel:
        log.exception("No channel id found.")
        return

    team_info = slack_client.team_info(team=slack_event.team_id)
    if not team_info.get('ok'):
        log.exception(team_info.get('error'))
        return

    domain = (team_info.get('team', {}).get('domain') or
              team_info.get('team', {}).get('name'))
    return f'https://{domain}.slack.com/archives/{slack_event.channel}'


def get_message_permalink(slack_event):
    """ Retrieves the permalink for a Slack message """
    event_content = json.loads(slack_event._payload).get('event')
    message_ts = (event_content.get('item', {}).get('event_ts')
                  or event_content.get('message', {}).get('event_ts')
                  or event_content.get('ts')
                  or event_content.get('event_ts'))

    if event_content.get('item'):
        message_ts = event_content.get('item', {}).get('event_ts')
    elif event_content.get('message'):
        message_ts = event_content.get('message', {}).get('event_ts')
    else:
        message_ts = (event_content.get('ts')
                      or event_content.get('event_ts'))

    if not slack_event.channel or not message_ts:
        return

    permalink = slack_client.chat_getPermalink(
        channel=slack_event.channel, message_ts=message_ts)

    if not permalink.get('ok'):
        log.exception(permalink.get('error'))
        return
    return permalink.get('permalink')


def get_reaction_permalink(slack_event):
    """ Retrieves the permalink to the message a reaction was posted """
    payload = json.loads(slack_event._payload)
    item = payload.get('event', {}).get('item')
    if not item:
        log.info('No item found')
        return

    permalink = slack_client.chat_getPermalink(
        channel=item.get('channel'), message_ts=item.get('ts'))

    if not permalink.get('ok'):
        log.exception(permalink.get('error'))
        return
    return permalink.get('permalink')


def get_star_or_pin_permalink(slack_event):
    """ Retrieves the permalink to the message starred or pinned """
    payload = json.loads(slack_event._payload)
    message = payload.get('event', {}).get('item', {}).get('message')
    if not message:
        log.info('No message found')
        return
    return message.get('permalink')
