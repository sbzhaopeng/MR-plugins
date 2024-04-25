from datetime import datetime, timedelta
from date import fetch_all_data

def calculate_cycle_phases(start_dates_dict):
    results = {}

    for name, start_dates in start_dates_dict.items():
        cycle_phases = []

        # 将字符串转换为 datetime 对象
        start_dates = [datetime.strptime(date[0], "%Y-%m-%d") for date in start_dates]

        # 计算周期长度
        cycle_lengths = [(start_dates[i + 1] - start_dates[i]).days for i in range(len(start_dates) - 1)]

        # 计算平均周期长度
        average_cycle_length = round(sum(cycle_lengths) / len(cycle_lengths))

        # 预测下一个月经周期开始日期
        predicted_next_start = start_dates[-1] + timedelta(days=average_cycle_length)

        # 定义排卵日，假设排卵日为下次月经开始的前14天
        ovulation_day = predicted_next_start - timedelta(days=14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day + timedelta(days=4)
        period_end = start_dates[-1] + timedelta(days=5)

        # 计算每一天的周期阶段
        for day in daterange(start_dates[-1], predicted_next_start):
            phase, next_phase, days_until_next_phase = assign_cycle_phase(day, period_end, fertile_start, fertile_end, predicted_next_start)
            cycle_phases.append((day.strftime("%Y-%m-%d"), phase, next_phase, days_until_next_phase))

        results[name] = cycle_phases

    return results

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

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

start_dates_dict= fetch_all_data("menstrual_cycle_info")
results=calculate_cycle_phases(start_dates_dict)
print(results)
