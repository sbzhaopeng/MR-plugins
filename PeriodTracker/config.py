import logging
from typing import Dict, Any

from mbot.core.plugins import plugin, PluginContext, PluginMeta
from mbot.openapi import mbot_api
server = mbot_api

_LOGGER = logging.getLogger(__name__)

@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global message_to_uid
    message_to_uid = config.get('uid')
    global channel
    channel = config.get('ToChannelName')
    global img_url
    img_url = config.get('img_url')
    if not img_url:
        img_url = 'https://api.r10086.com/樱道随机图片api接口.php?图片系列=少女写真5'


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global message_to_uid
    message_to_uid = config.get('uid')
    global channel
    channel = config.get('ToChannelName')
    global img_url
    img_url = config.get('img_url')
    if not img_url:
        img_url = 'https://api.r10086.com/樱道随机图片api接口.php?图片系列=少女写真5'


def send_notify(content):
    if message_to_uid:
        for _ in message_to_uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{body}}', {
                'title': '每日健康监测',
                'body': content,
                'pic_url': img_url
            }, to_uid=_, to_channel_name=channel)
