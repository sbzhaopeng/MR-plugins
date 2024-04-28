import logging

from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from mbot.core.params import ArgSchema, ArgType
from .predict import predict
from .track import track_today
from .data import insert_user_info, insert_cycle_info, get_user_name_list, get_user_info_list, get_cycle_info_list, delete_user_info, delete_cycle_info, delete_cycle_phase_by_name, get_phase_name_list

_LOGGER = logging.getLogger(__name__)

@plugin.command(name='period_command', title='健康预测', desc='点击执行健康预测', icon='AutoAwesome',
                run_in_background=True)
def period_tracker_command(ctx: PluginCommandContext):
    predict()
    return PluginCommandResponse(True, f'健康预测执行成功')


@plugin.command(name='track_command', title='每日健康监测', desc='点击执行每日监测', icon='AutoAwesome',
                run_in_background=True)
def period_tracker_command(ctx: PluginCommandContext):
    track_today()
    return PluginCommandResponse(True, f'每日健康监测执行成功')



@plugin.command(name='insert_user_info', title='新增基本信息', desc='新增基本信息，包括姓名、出生日期', icon='AutoAwesome',
                run_in_background=True)
def insert_info_command(
        ctx: PluginCommandContext,        
        name: ArgSchema(ArgType.String, '姓名', '', required=True),
        birthdate: ArgSchema(ArgType.String, '出生日期', '格式为：YYYY-MM-DD')
):
    try:
        insert_user_info(name, birthdate)
        return PluginCommandResponse(True, f'「{name}」新增成功')
    except Exception as e:
        return PluginCommandResponse(False, f'「{name}」新增失败，错误信息：{e}')
        

@plugin.command(name='insert_cycle_info', title='新增健康信息', desc='新增健康信息，选择对应姓名录入例假开始日期', icon='AutoAwesome',
                run_in_background=True)
def insert_info_command(
        ctx: PluginCommandContext,        
        select_name: ArgSchema(ArgType.Enum, '选择姓名', '选择要录入健康信息的对象', enum_values=lambda: get_user_name_list(), multi_value=False),
        start_date:ArgSchema(ArgType.String, '例假开始时间', '格式为：YYYY-MM-DD')
):
    try:
        insert_cycle_info(select_name, start_date)
        return PluginCommandResponse(True, f'「{select_name}」的{start_date}健康信息新增成功')
    except Exception as e:
        return PluginCommandResponse(False, f'「{name}」的健康信息新增失败，错误信息：{e}')



@plugin.command(name='delete_info', title='删除数据', desc='删除基本信息以或健康信息数据', icon='AutoAwesome', run_in_background=True)
def info_delete(
    ctx: PluginCommandContext,
    select_user_info: ArgSchema(ArgType.Enum, '选择基本详细信息', '选择想修改或删除的基本信息，列表为姓名-出生日期', enum_values=lambda: get_user_info_list(), multi_value=False, required=False),
    select_cycle_info: ArgSchema(ArgType.Enum, '健康详细信息', '选择想删除的健康信息，列表为姓名-例假开始日期', enum_values=lambda: get_cycle_info_list(), multi_value=False, required=False),
    select_phase_by_name: ArgSchema(ArgType.Enum, '健康预测信息', '选择想删除预测信息对应的姓名', enum_values=lambda: get_phase_name_list(), multi_value=False, required=False)
):
    # 初始化响应消息
    response_messages = []

    if select_user_info:
        # 解析用户的输入
        name, birthdate = parse_input(select_user_info)
        # 调用删除user_info信息的函数
        delete_user_info(name, birthdate)
        # 添加操作结果到响应消息列表
        response_messages.append(f"已删除{name}的基本详细信息")

    if select_cycle_info:
        # 解析用户的输入
        name, start_date = parse_input(select_cycle_info)
        # 调用删除cycle_info信息的函数
        delete_cycle_info(name, start_date)
        # 添加操作结果到响应消息列表
        response_messages.append(f"已删除{name}的健康详细信息")

    if select_phase_by_name:
        # 调用删除cycle_phase信息的函数
        delete_cycle_phase_by_name(select_phase_by_name)
        # 添加操作结果到响应消息列表
        response_messages.append(f"已删除{select_phase_by_name}的全部预测信息")

    # 检查是否有执行的操作，并创建相应的响应结果
    if response_messages:
        # 如果有至少一个操作成功执行，返回成功的响应结果
        return PluginCommandResponse(True, ' '.join(response_messages))
    else:
        # 如果没有操作执行，可能是因为没有提供任何输入
        return PluginCommandResponse(False, "未提供足够信息进行操作。")

# 整理delet_info中的输入信息
def parse_input(input_str):
    """
    从输入字符串中解析出名称和日期。
    假设输入是 "b-['1993-12-25']" 的格式。
    """
    name, date_str = input_str.split('-', maxsplit=1)
    # 假设日期只包含在单引号内的一个单一日期
    date = date_str.strip("[]' ")
    return name, date
