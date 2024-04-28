from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import logging

from .data import connect_database
from .config import send_notify
from .pic import generate_random_image_link


_LOGGER = logging.getLogger(__name__)

def fetch_today_phase():
    today = datetime.now().date()  # 获取今天的日期
    conn, cursor = connect_database()  # 假设此函数连接数据库并返回游标cursor

    try:
        # 按name分组选择每个人的最新记录
        select_query = f"""
        SELECT name, phase_date, phase, next_phase, days_until_next_phase
        FROM cycle_phase_list
        ORDER BY name, phase_date DESC
        """
        cursor.execute(select_query)
        records = cursor.fetchall()

        data = {}
        error_data = {}

        # 在循环之前准备一个字典，用于跟踪每个人的最新记录日期
        latest_phase_dates = defaultdict(lambda: datetime.min.date())

        for row in records:
            name = row[0]

            phase_date = datetime.strptime(row[1], "%Y-%m-%d").date()

            # 更新当前人的最新记录日期
            latest_phase_dates[name] = max(latest_phase_dates[name], phase_date)


        for row in records:

            name = row[0]
            
            # 跳过已处理的姓名
            #if name == current_name:
                #continue

            # 更新当前正在处理的姓名
            #current_name = name
            phase_date = datetime.strptime(row[1], "%Y-%m-%d").date()


            # 如果记录日期早于今天，则添加错误信息
            if phase_date < today:
                if phase_date == latest_phase_dates[name]:
                    error_data[name] = {
                        'name': name,
                        'nearest_phase_date': row[1]
                    }
                continue

            if phase_date == today:
                data[name] = {
                    'name': name,
                    'phase_date': row[1],
                    'phase': row[2],
                    'next_phase': row[3],
                    'days_until_next_phase': row[4]
                }


        return data, error_data

    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


# 每日预测
def track_today():
    today_records, errors = fetch_today_phase()
    pic_url = generate_random_image_link()
    if today_records:
        for name, detail in today_records.items():
            name = name
            phase_date = datetime.strptime(detail['phase_date'], '%Y-%m-%d')
            phase = detail['phase']
            next_phase = detail['next_phase']
            days_until_next_phase = detail['days_until_next_phase']
            next_phase_date = phase_date+timedelta(days=days_until_next_phase)
            pic_url = generate_random_image_link()
            if phase == '月经期':
                context = {
                    'title': f'{phase_date.strftime("%Y年%m月%d日")}健康监测',
                    'body':  f'{name}正处于大姨妈期间，请加强关心爱护，预计大姨妈将在{next_phase_date.strftime("%Y年%m月%d日")}离开，还有{days_until_next_phase}天。',
                    'pic_url': pic_url
                }
            elif phase == '月经期后安全期':
                context = {
                    'title': f'{phase_date.strftime("%Y年%m月%d日")}健康监测',
                    'body':  f'{name}姨妈已离开，正处于安全期，可以正常玩耍了，预计易孕期将在{next_phase_date.strftime("%Y年%m月%d日")}开始，还有{days_until_next_phase}天。',
                    'pic_url': pic_url
                }
            elif phase == '易孕期':
                context = {
                    'title': f'{phase_date.strftime("%Y年%m月%d日")}健康监测',
                    'body':  f'{name}正处于易孕期，请做好安全防护，预计还要持续{days_until_next_phase}天，下一阶段安全期预计将在{next_phase_date.strftime("%Y年%m月%d日")}开始。',
                    'pic_url': pic_url
                }
            elif phase == '易孕期后安全期':
                context = {
                    'title': f'{phase_date.strftime("%Y年%m月%d日")}健康监测',
                    'body':  f'{name}正处于安全期，可以愉快玩耍，预计大姨妈将在{next_phase_date.strftime("%Y年%m月%d日")}到访，还有{days_until_next_phase}天，请时刻关注心情变化。',
                    'pic_url': pic_url
                }
            else:
                context = {
                    'title': f'{phase_date.strftime("%Y年%m月%d日")}健康监测',
                    'body':  f'{name}数据有误，请检查数据。',
                    'pic_url': pic_url
                }
            send_notify(context)
            # _LOGGER.info(context)
    
    elif errors:
        for name, detail in errors.items():
            name = name
            nearest_phase_date = detail['nearest_phase_date']
            pic_url = generate_random_image_link()
            context = {
                'title': '每日健康监测',
                'body': f'{name}的预测数仅持续至{nearest_phase_date},已早于今日，请更新健康数据后重新预测！',
                'pic_url': pic_url
            }

            send_notify(context)
    
    else:
        context = {
            'title': '每日健康监测',
            'body':  '无预测数据，请检查数据是否正确',
            'pic_url': pic_url
        }

        send_notify(context)


    

