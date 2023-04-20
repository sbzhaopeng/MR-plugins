import os
import logging
from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from typing import Dict, Any


_LOGGER = logging.getLogger(__name__)



@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global watch_target_folders_str, watch_target_folders
    watch_target_folders_str = config.get('watch_target_folders')
    watch_target_folders = [t.split(':') for t in watch_target_folders_str.split(',')]
    if not watch_target_folders_str:
        _LOGGER.error("[硬链接整理] 目录还未设置")
    else:
        for watch_folder, target_folder in watch_target_folders:
            _LOGGER.info(f"[硬链接整理] 监控目录: {watch_folder}, 目标目录: {target_folder}")


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global watch_target_folders_str, watch_target_folders
    watch_target_folders_str = config.get('watch_target_folders')
    watch_target_folders = [t.split(':') for t in watch_target_folders_str.split(',')]
    if not watch_target_folders_str:
        _LOGGER.error("[硬链接整理] 目录还未设置")
    else:
        for watch_folder, target_folder in watch_target_folders:
            _LOGGER.info(f"[硬链接整理] 监控目录: {watch_folder}, 目标目录: {target_folder}")


@plugin.on_event(bind_event=[EventType.DownloadCompleted], order=10)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """
    save_path = data.get("source_path")
    _LOGGER.info("[硬链接整理] source_path: %s " % save_path)

    # 遍历每个监控目录及其对应的目标目录，下载地址与监控目录匹配时，建立硬链接
    for watch_folder, target_folder in watch_target_folders:
        if save_path.startswith(watch_folder):
            _LOGGER.info("[硬链接整理] 保存路径与监控目录匹配: %s, 开始整理" % save_path)
            if os.path.isfile(save_path):
                #_LOGGER.info("[硬链接整理] 保存路径为一个文件: %s" % save_path)
                target_path = os.path.join(target_folder, os.path.basename(save_path))#.replace(" ", ".")
                try:
                    os.link(f"{save_path}", f"{target_path}")
                except OSError as e:
                    _LOGGER.warning("[硬链接整理] 处理硬链接失败 %s" % e)
                _LOGGER.info("[硬链接整理] 文件硬链接到: %s" % target_path)
            else:
                for root, dirs, files in os.walk(save_path):
                    for name in files:
                        source_path = os.path.join(root, name)
                        target_path = os.path.join(target_folder, os.path.relpath(source_path, watch_folder))#.replace(" ", ".")
                        target_dir = os.path.dirname(target_path)
                        if not os.path.exists(target_dir):
                            try:
                                os.makedirs(target_dir, exist_ok=True)
                            except OSError as e:
                                _LOGGER.warning("[硬链接整理] 建立目录失败 %s" % e)
                        try:
                            os.link(f"{source_path}", f"{target_path}")
                        except OSError as e:
                            _LOGGER.warning("[硬链接整理] 处理硬链接失败 %s" % e)                
                _LOGGER.info("[硬链接整理] 下载任务硬链接到: %s" % os.path.join(target_folder, os.path.basename(save_path)))