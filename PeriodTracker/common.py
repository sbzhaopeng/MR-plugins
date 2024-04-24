from datetime import datetime, timedelta

# 已知月经周期开始日期记录
start_dates = [
    "2023-07-04",
    "2023-08-01",
    "2023-08-29",
    "2023-09-25",
    "2023-10-21",
    "2023-11-18",
    "2023-12-21",
    "2024-01-16",
    "2024-02-18",
    "2024-03-20"
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

# 输出结果
for date, phase in cycle_phase_list:
    print(f"{date}: {phase}")
