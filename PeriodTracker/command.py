import logging

from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .period_tracker import tracker

_LOGGER = logging.getLogger(__name__)

@plugin.command(name='period_tracker_command', title='健康监测', desc='点击执行健康监测', icon='AutoAwesome',
                run_in_background=True)
def period_tracker_command(ctx: PluginCommandContext):
    tracker()
    return PluginCommandResponse(True, f'健康监测执行成功')
