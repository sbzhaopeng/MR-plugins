from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import logging

from .data import connect_database
from .config import send_notify
from .pic import generate_random_image_link

_LOGGER = logging.getLogger(__name__)

today = datetime.now().date()
today_str = today.strftime("%Y年%-m月%-d日")


def fetch_today_phase():
    conn, cursor = connect_database()
    try:
        # 查询最新周期数据
        select_query = '''
            SELECT name, MAX(phase_date) as latest_phase_date
            FROM cycle_phase_list
            GROUP BY name
        '''
        cursor.execute(select_query)
        latest_phases = cursor.fetchall()

        # 存储错误数据
        error_data = {}

        # 存储今天的数据
        today_data = {}

        for name, latest_date_str in latest_phases:
            latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d").date()
            
            if latest_date < today:
                # 如果最新的记录日期早于今天，添加到错误数据
                error_data[name] = latest_date_str

            else:
                cursor.execute('''
                    SELECT name, phase_date, phase, next_phase, days_until_next_phase
                    FROM cycle_phase_list
                    WHERE name = ? AND phase_date = ?
                ''', (name, today,))
                today_records = cursor.fetchall()

                for record in today_records:
                    _, phase_date, phase, next_phase, days_until_next_phase = record
                    today_data[name] = {
                        'phase_date': phase_date,
                        'phase': phase,
                        'next_phase': next_phase,
                        'days_until_next_phase': days_until_next_phase
                    }

        return today_data, error_data
    finally:
        cursor.close()
        conn.close()

# 构建通知内容
def build_notify_context(name, phase_date, phase, days_until_next_phase, pic_url):
    next_phase_date = phase_date + timedelta(days=days_until_next_phase)
    body_templates = {
        '月经期': "{name}正处于大姨妈期间，请加强关心爱护，预计大姨妈将在{next_date}离开，还有{days}天。",
        '月经期后安全期': "{name}姨妈已离开，正处于安全期，可以正常玩耍了，预计易孕期将在{next_date}开始，还有{days}天。",
        '易孕期': "{name}正处于易孕期，请做好安全防护，预计还要持续{days}天，下一阶段安全期预计将在{next_date}开始。",
        '易孕期后安全期': "{name}正处于安全期，可以愉快玩耍，预计大姨妈将在{next_date}到访，还有{days}天，请时刻关注心情变化。",
        '数据错误': "{name}数据有误，请检查数据。"
    }
    
    body = body_templates.get(phase, body_templates['数据错误']).format(
        name=name,
        next_date=next_phase_date.strftime("%Y年%-m月%-d日"),
        days=days_until_next_phase
    )

    return {
        'title': f'{today_str}健康监测',
        'body': body,
        'pic_url': pic_url
    }

# 每日预测
def track_today():
    today_data, error_data = fetch_today_phase()
    if today_data:
        for name, detail in today_data.items():
            pic_url = generate_random_image_link()
            phase_date = datetime.strptime(detail['phase_date'], '%Y-%m-%d')
            context = build_notify_context(
                name, phase_date, detail['phase'], 
                detail['days_until_next_phase'], pic_url)

            send_notify(context)  # 发送通知
            _LOGGER.info(f"{name}{today_str}的健康监测通知已发送")

            
    # 错误处理
    if error_data:
        for name, nearest_phase_date in error_data.items():
            pic_url = generate_random_image_link()
            context = {
                'title': f'{today_str}健康监测',
                'body':  f'{name}的预测数据仅持续至{nearest_phase_date}，已早于今日，请更新健康数据后重新预测！',
                'pic_url': pic_url
            }

            send_notify(context)  # 发送通知
            _LOGGER.info(f"{name}{today_str}健康监测错误通知已发送")


    # 不存在任何记录
    if not today_data and not error_data:
        pic_url = generate_random_image_link()
        context = {
            'title': f'{today_str}健康监测',
            'body': '无预测数据，请检查数据是否正确',
            'pic_url': pic_url
        }

        send_notify(context)  # 发送通知
        _LOGGER.warning("没有找到合适的健康数据记录来发送通知。")
