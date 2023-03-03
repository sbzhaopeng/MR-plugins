from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from mbot.openapi import mbot_api
from mbot.core.params import ArgSchema, ArgType
import logging

from .dayima import menses_day_notify_manual

_LOGGER = logging.getLogger(__name__)


@plugin.command(name='dayima', title='女友小助手', desc='推送女友生理期信息', icon='StarRate', run_in_background=True)
def dayima_echo(ctx: PluginCommandContext):
    try:
        _LOGGER.info('开始获取女友生理期信息')
        menses_day_notify_manual()
        _LOGGER.info('女友生理期信息获取完成')
        return PluginCommandResponse(True, f'女友生理期信息获取成功')
    except Exception as e:
        _LOGGER.error(f'出错了,{e}')
        return PluginCommandResponse(False, f'生理期信息获取失败，原因：{e}')
