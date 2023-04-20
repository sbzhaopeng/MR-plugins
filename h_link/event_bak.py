import os
import logging
from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext
from typing import Dict


_LOGGER = logging.getLogger(__name__)

watch_folder = "/HHD2/PT/Video"

target_folder = "/HHD2/Video"


@plugin.on_event(bind_event=[EventType.DownloadCompleted], order=10)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """

    save_path = data.get("source_path")
    _LOGGER.info("[视频整理] source_path: %s " % save_path)
    if not save_path:
        return

    _LOGGER.info("[视频整理] watch_folder: %s " % watch_folder)

    # 检查是否匹配监控目录配置
    if not save_path.startswith(watch_folder):
        return

    _LOGGER.info("[视频整理] 下载地址与监控目录匹配: %s, 开始整理" % save_path)
    
    for root, dirs, files in os.walk(save_path):
        for name in dirs:
            source_path = os.path.join(root, name)
            target_path = os.path.join(target_folder, os.path.relpath(source_path, watch_folder))
            os.makedirs(target_path, exist_ok=True)
        for name in files:
            source_path = os.path.join(root, name)
            target_path = os.path.join(target_folder, os.path.relpath(source_path, watch_folder))
            os.link(source_path, target_path)
            
    _LOGGER.info("[视频整理] 下载任务硬链接到: %s" % target_path)
