from datetime import datetime, timedelta
import logging

from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from mbot.openapi import mbot_api
from .config import send_notify


_LOGGER = logging.getLogger(__name__)
server = mbot_api

# 已知月经周期开始日期记录
start_dates = [
    "2024-02-22",
    "2024-03-26",
    "2024-04-23"
]

# 将字符串转换为 datetime 对象
start_dates = [datetime.strptime(date, "%Y-%m-%d") for date in start_dates]

# 计算周期长度
cycle_lengths = [(start_dates[i + 1] - start_dates[i]).days for i in range(len(start_dates) - 1)]

# 计算平均周期长度
average_cycle_length = round(sum(cycle_lengths) / len(cycle_lengths))

# 预测下一个月经周期开始日期
predicted_next_start = start_dates[-1] + timedelta(days=average_cycle_length)

# 遍历一个时间范围内的每一天
def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

# 将周期按日期作标记的功能函数
def assign_cycle_phase(day, last_period_start, next_period_start):
    # 定义易孕期，假设排卵日为下次月经开始的前14天
    ovulation_day = next_period_start - timedelta(days=14)
    # 易孕期为排卵前5天到排卵后4天
    fertile_start = ovulation_day - timedelta(days=5)
    fertile_end = ovulation_day + timedelta(days=4)
    # 月经期，假设为周期开始的5天
    period_end = last_period_start + timedelta(days=5)
    
    if last_period_start <= day < period_end:
        return '月经期'
    elif fertile_start <= day <= fertile_end:
        return '易孕期' if day != ovulation_day else '排卵日'
    else:
        return '安全期'

# 最后一个周期开始到预测下个周期开始之前的每一天
cycle_phase_list = [(day.strftime("%Y-%m-%d"), assign_cycle_phase(day, start_dates[-1], predicted_next_start))
                for day in daterange(start_dates[-1], predicted_next_start)]
        

def tracker():

    today = datetime.now().strftime("%Y-%m-%d")
    # 遍历周期相位列表，查找当天的相位
    for phase_date, phase in cycle_phase_list:
        if phase_date == today:
            # 找到当天的相位信息，记录日志并结束循环
            send_notify(f'今日是{today}，处于{phase}')
            break
    
    # 如果未找到当天的相位信息，记录日志
    else:
        send_notify(f'今日是{today}，健康数据有误，请及时更新！')


