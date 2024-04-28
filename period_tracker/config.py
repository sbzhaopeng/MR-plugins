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
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'health.db')):
        create_tables()  # 构建数据库


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global message_to_uid
    message_to_uid = config.get('uid')
    global channel
    channel = config.get('ToChannelName')



def send_notify(context):
    if message_to_uid:
        for _ in message_to_uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{body}}', context, to_uid=_, to_channel_name=channel)
