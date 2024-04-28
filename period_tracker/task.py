from mbot.core.plugins import plugin
from .track import track_today

@plugin.task('phase_track_task', '每日获取phase信息', cron_expression='0 9 * * *')
def phase_track_task():
    track_today()