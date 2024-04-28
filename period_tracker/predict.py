from datetime import datetime, timedelta

import logging

# from mbot.core.plugins import plugin
# from mbot.core.plugins import PluginContext, PluginMeta
# from mbot.openapi import mbot_api

from .data import fetch_all_data, insert_phase_list_data


_LOGGER = logging.getLogger(__name__)
# server = mbot_api

# 预测下一周期，迭代下一周期每一天所处类型
def calculate_cycle_phases(start_dates_dict):
    results = []

    for name, start_dates in start_dates_dict.items():
        
        # 如果存在两个或两个以上的周期开始日期
        if len(start_dates) > 1:
            
            # 将字符串转换为 datetime 对象
            start_dates = [datetime.strptime(date[0], "%Y-%m-%d") for date in start_dates]

            # 计算周期长度
            cycle_lengths = [(start_dates[i + 1] - start_dates[i]).days for i in range(len(start_dates) - 1)]

            # 计算平均周期长度
            average_cycle_length = round(sum(cycle_lengths) / len(cycle_lengths))

            # 预测下一个月经周期开始日期
            predicted_next_start = start_dates[-1] + timedelta(days=average_cycle_length)

        # 如果只有一个开始日期
        elif len(start_dates) == 1:

            # 将字符串转换为 datetime 对象
            start_dates = [datetime.strptime(date[0], "%Y-%m-%d") for date in start_dates]

            # 设定周期长度为28天
            default_cycle_length = 28

            # 预测下一个月经周期开始日期
            predicted_next_start = start_dates[-1] + timedelta(days=default_cycle_length)

        else:
            predicted_next_start = None
            _LOGGER.error(f"用户 '{name}' 的例假数据缺失，无法预测周期开始日期")
            return


        # 定义排卵日，假设排卵日为下次月经开始的前14天
        ovulation_day = predicted_next_start - timedelta(days=14)
        fertile_start = ovulation_day - timedelta(days=6)
        fertile_end = ovulation_day + timedelta(days=5)
        period_end = start_dates[-1] + timedelta(days=6)

        # 计算每一天的周期阶段
        for day in daterange(start_dates[-1], predicted_next_start):
            phase, next_phase, days_until_next_phase = assign_cycle_phase(day, period_end, fertile_start, fertile_end, predicted_next_start)
            results.append({
                'name': name,
                'phase_date': day.strftime("%Y-%m-%d"),
                'phase': phase,
                'next_phase': next_phase,
                'days_until_next_phase': days_until_next_phase
            })

    return results


# 历遍每一天
def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)


# 周期分段
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

    return phase, next_phase, days_until_next_phase


# 构建predict主函数
def predict():
    start_dates_dict= fetch_all_data("cycle_info")
    phases_list=calculate_cycle_phases(start_dates_dict)
    if phases_list:
        insert_phase_list_data(phases_list)
        logged_names = set()
        for item in phases_list:
            name = item['name']
            # 如果这个名字还没有被记录过，那么记录它并加入到集合中
            if name not in logged_names:
                _LOGGER.info(f"成功预测姓名为 {name} 的健康信息并写入数据库。")
                logged_names.add(name)  # 添加已记录的名称
    else:
        _LOGGER.error(f"无数据，请添加健康信息")
