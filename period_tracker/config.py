import os
import logging
from typing import Dict, Any

from mbot.core.plugins import plugin, PluginContext, PluginMeta
from mbot.openapi import mbot_api
from .data import create_tables


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
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'health.db')):
        create_tables()  # 构建数据库


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



def send_notify(context):
    if message_to_uid:
        for _ in message_to_uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{body}}', context, to_uid=_, to_channel_name=channel)
            _LOGGER.info(f'每日健康监测通知发送成功')
