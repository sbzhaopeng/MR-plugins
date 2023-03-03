from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from mbot.openapi import mbot_api
import logging
from typing import Dict, Any

import random
from datetime import datetime, date
import datetime as pt

server = mbot_api
_LOGGER = logging.getLogger(__name__)


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global message_to_uid
    message_to_uid = config.get('uid')
    global menses_day
    menses_day = config.get('menses_day')
    global round_day
    round_day = config.get('round_day')


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global message_to_uid
    message_to_uid = config.get('uid')
    global menses_day
    menses_day = config.get('menses_day')
    global round_day
    round_day = config.get('round_day')


@plugin.task('dayima', '定时获取女友生理期', cron_expression='0 18 * * *')
def task():
    menses_day_notify(menses_day, today, round_day, tempday)

    


def menses_day_notify_manual():
    today = datetime.today()
    tempday = int(random.uniform(-2, 2))
    menses_day_notify(menses_day, today, round_day, tempday)


def menses_day_notify(menses_day, today, round_day, tempday):
    today = datetime.today()
    tempday = int(random.uniform(-2, 2))
    menses_day_date = datetime.strptime(menses_day, "%Y-%m-%d")
    days = int((today - menses_day_date).days) + 1
    safe_day = menses_day_date + pt.timedelta(int(round_day) + tempday - 9)
    safe_day_content = safe_day.strftime("%Y-%m-%d")
    if days >= 0 and days <= 4 :
        title = '每日女友心情监测'
        content = '姨妈期间，请不要惹她生气！'
        send_notify(title, content)
    elif days >= 5 and days <= 7 :
        title = '每日女友心情监测'
        content = '安全期，可用吃好吃的，注意防护措施。'
        send_notify(title, content)
    elif days >= 8 and days <= int(round_day) + tempday - 10 :
        title = '每日女友心情监测'
        content = '危险期，严格注意防护。最近的安全期预计为:' + safe_day_content
        send_notify(title, content)
    elif days >= int(round_day) + tempday - 9 and days <= int(round_day) + tempday - 1 :
        title = '每日女友心情监测'
        content = '安全期，姨妈将要来临。'
        send_notify(title, content)
    else:
        title = '每日女友心情监测'
        conten = '数据有误。'
        send_notify(title, conten)
    return
 
def send_notify(title, content):
    if message_to_uid:
        for _ in message_to_uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{content}}', {
                'title': title,
                'content': content
            }, to_uid=_)
    else:
        server.notify.send_message_by_tmpl('{{title}}', '{{conten}}', {
                'title': title,
                'content': content
            })
    return
    

def main():
    menses_day_notify_manual()