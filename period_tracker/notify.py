import logging

from mbot.openapi import mbot_api
from .config import message_to_uid, channel, img_url

server = mbot_api

_LOGGER = logging.getLogger(__name__)

def send_notify(context):
    if message_to_uid:
        for _ in message_to_uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{body}}', context, to_uid=_, to_channel_name=channel)
            _LOGGER.info(f'每日健康监测通知发送成功')
