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

# 定义排卵日，假设排卵日为下次月经开始的前14天
ovulation_day = predicted_next_start - timedelta(days=14)
fertile_start = ovulation_day - timedelta(days=5)
fertile_end = ovulation_day + timedelta(days=4)
period_end = start_dates[-1] + timedelta(days=5)

def assign_cycle_phase(day, period_end, fertile_start, fertile_end, predicted_next_start):

    if day < period_end:
        phase = "月经期"
        next_phase = "月经期后安全期"
        days_until_next_phase = (period_end - day).days
    elif day < fertile_start:
        phase = "月经期后安全期"
        next_phase = "易孕期" 
        days_until_next_phase = (fertile_start - day).days
    elif day <= fertile_end:
        phase = "易孕期"
        next_phase = "易孕期后安全期" 
        days_until_next_phase = (fertile_end - day).days
    elif day < predicted_next_start:
        phase = "易孕期后安全期"
        next_phase = "月经期"
        days_until_next_phase = (predicted_next_start - day).days

    return (phase, next_phase, days_until_next_phase)

cycle_phase_list = [
    (day.strftime("%Y-%m-%d"),
     *assign_cycle_phase(day, period_end, fertile_start, fertile_end, predicted_next_start))
    for day in daterange(start_dates[-1], predicted_next_start)
]

def tracker():

    today = datetime.now().strftime("%Y-%m-%d")
    today_in_chinese = datetime.now().strftime("%Y年%m月%d日")
    # 遍历周期相位列表，查找当天的相位
    for phase_date, phase, next_phase, days_until_next_phase in cycle_phase_list:
        if phase_date == today:
            # 找到当天的相位信息，记录日志并结束循环
            send_notify(f'今日{today_in_chinese}，处于{phase}，距离{next_phase}还有{days_until_next_phase}天')
            break
    
    # 如果未找到当天的相位信息，记录日志
    else:
        send_notify(f'今日是{today_in_chinese}，健康数据有误，请及时更新！')


