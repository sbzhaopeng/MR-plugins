import os
import logging
import sqlite3
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

# 连接数据库
def connect_database():
    # 连接到SQLite数据库
    # 如果数据库不存在，那么它就会被创建，最终将返回一个数据库对象。
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'health.db'))
    cursor = conn.cursor()
    return conn, cursor


# 新建信息表
def create_tables():
    conn, cursor = connect_database()
    tables = ['user_info', 'cycle_info', 'cycle_phase_list']
    for table in tables:
        if table == 'user_info':
            cursor.execute('''
                CREATE TABLE user_info (
                    name TEXT PRIMARY KEY,
                    birthdate DATE
                )
            ''')
        elif table == 'cycle_info':
            cursor.execute('''
                CREATE TABLE cycle_info (
                    name TEXT,
                    start_date DATE,
                    UNIQUE(name, start_date),
                    FOREIGN KEY(name) REFERENCES user_info(name)
                )
            ''')
        elif table == 'cycle_phase_list':
            cursor.execute('''
                CREATE TABLE cycle_phase_list (
                    name TEXT,
                    phase_date DATE,
                    phase TEXT,
                    next_phase TEXT,
                    days_until_next_phase INTEGER,
                    FOREIGN KEY(name) REFERENCES user_info(name)
                )
            ''')
    conn.commit()
    cursor.close()
    conn.close()

# 向user_info表中插入数据
def insert_user_info(name, birthdate):
    # 连接到数据库
    conn, cursor = connect_database()
    try:
        # 试图插入新的用户信息
        cursor.execute("INSERT INTO user_info (name, birthdate) VALUES (?, ?)", (name, birthdate,))
        _LOGGER.info(f"{birthdate}出生的{name}基本信息添加成功")
    except sqlite3.IntegrityError as e:
        # 如果违反了唯一性约束（name已存在），则打印提示
        _LOGGER.error(f" 用户'{name}' 已存在")
    
    # 提交更改
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()

# 向cycle_info表中插入数据
def insert_cycle_info(name, start_date):
    # 连接到数据库
    conn, cursor = connect_database()
    try:
        # 试图插入新的周期信息
        cursor.execute("INSERT INTO cycle_info (name, start_date) VALUES (?, ?)", (name, start_date,))
        _LOGGER.info(f"{name}：{start_date}的例假开始时间添加成功")
    except sqlite3.IntegrityError as e:
        # 如果违反了唯一性约束（已存在相同的name和start_date），则打印提示
        _LOGGER.error(f"用户 '{name}' 的例假开始时间 '{start_date}' 已存在")
    
    # 提交更改
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()


# 向cycle_phase_list表中插入数据
def insert_phase_list_data(data, table_name='cycle_phase_list'):
    # 连接到数据库
    conn, cursor = connect_database()

    # 构建 SQL 插入语句
    columns = ', '.join(data[0].keys())  # 将数据的第一行（字典）的键（列名）连接成字符串
    placeholders = ', '.join(['?' for _ in range(len(data[0]))])  # 创建与列数相等的占位符字符串
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'  # 构建插入语句

    # 执行插入操作
    for row in data:
        name = row['name']
        phase_date = row['phase_date']
        existing_data = cursor.execute(f"SELECT * FROM {table_name} WHERE name = ? AND phase_date = ?", (name, phase_date)).fetchone()

        if existing_data:
            # 如果存在相同的 name 和 phase_date，则更新整行数据
            update_query = f"UPDATE {table_name} SET phase = ?, next_phase = ?, days_until_next_phase = ? WHERE name = ? AND phase_date = ?"
            cursor.execute(update_query, (row['phase'], row['next_phase'], row['days_until_next_phase'], name, phase_date))
        else:
            # 否则执行插入操作
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?' for _ in range(len(row))])
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(row.values()))

    # 提交更改
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()


# 展示表中的所有数据以name列为索引构建字典
def fetch_all_data(table_name):
    conn, cursor = connect_database()
    cursor.execute(f"PRAGMA table_info({table_name})")  # 获取表结构信息
    table_info = cursor.fetchall()
    name_index = None
    
    # 找到name列的索引
    for info in table_info:
        if info[1] == 'name':
            name_index = info[0]
            break
    
    # 如果找不到name列，返回空字典
    if name_index is None:
        create_tables()
        _LOGGER.info("每日健康监测数据库初始化成功")
        return {}
    
    # 构建SELECT语句，选择所有列，以name列作为索引
    column_names = ", ".join([info[1] for info in table_info])  # 获取所有列名
    select_query = f"SELECT {column_names} FROM {table_name} ORDER BY name"
    rows = cursor.execute(select_query).fetchall()
    conn.close()
    
    # 整理数据
    data = {}
    for row in rows:
        name = row[name_index]  # 获取name列的值
        if name not in data:
            data[name] = []
        data[name].append(list(row[:name_index] + row[name_index+1:]))  # 去除name列的数据并添加到列表中
        
    return data

    # 关闭连接
    cursor.close()
    conn.close()



cycle_phase_list_data = fetch_all_data('cycle_phase_list')

# 构建command所需姓名列表
def get_user_name_list():
    user_info_data = fetch_all_data('user_info')
    user_name_list = [{'name': key, 'value': key} for key in user_info_data.keys()]
    return user_name_list

# 构建command所需姓名-出生日期列表
def get_user_info_list():
    user_info_data = fetch_all_data('user_info')
    user_info_list = [{'name': f"{name}-{date}", 'value': f"{name}-{date}"} 
                  for name, dates in user_info_data.items() for date in dates]
    return user_info_list

# 构建command所需姓名-例假开始时间列表
def get_cycle_info_list():
    cycle_info_data = fetch_all_data('cycle_info')
    cycle_info_list = [{'name': f"{name}-{date}", 'value': f"{name}-{date}"} 
                  for name, dates in cycle_info_data.items() for date in dates]
    return cycle_info_list


# 构建command所需phase表姓名列表
def get_phase_name_list():
    phase_name_data = fetch_all_data('cycle_phase_list')
    phase_name_list = [{'name': key, 'value': key} for key in phase_name_data.keys()]
    return phase_name_list

# 构建从user_info删除数据的函数
def delete_user_info(name, birthdate):
    conn, cursor = connect_database()
    try:
        # 执行删除操作
        cursor.execute("DELETE FROM user_info WHERE name = ? AND birthdate = ?", (name, birthdate))
        # 提交事务
        conn.commit()
        _LOGGER.info(f"成功删除姓名为 {name} 出生日期为 {birthdate} 的用户。")
    except sqlite3.Error as e:
        # 出现错误时打印错误并回滚
        conn.rollback()
        _LOGGER.error(f"删除用户失败: {e}")
    
    # 关闭连接
    cursor.close()
    conn.close()

# 构建从cycle_info删除数据的函数
def delete_cycle_info(name, start_date):
    conn, cursor = connect_database()
    try:
        # 执行删除操作
        cursor.execute("DELETE FROM cycle_info WHERE name = ? AND start_date = ?", (name, start_date))
        # 提交事务
        conn.commit()
        _LOGGER.info(f"成功删除{name}的{start_date}例假开始记录。")
    except sqlite3.Error as e:
        # 出现错误时打印错误并回滚
        conn.rollback()
        _LOGGER.error(f"删除例假记录失败: {e}")

    # 关闭连接
    cursor.close()
    conn.close()

# 构建从cycle_phase_list删除指定用户预测数据的函数
def delete_cycle_phase_by_name(name):
    conn, cursor = connect_database()
    try:
        # 执行删除操作
        cursor.execute("DELETE FROM cycle_phase_list WHERE name = ?", (name,))
        # 提交事务
        conn.commit()
        _LOGGER.info(f"成功删除{name}的所有预测记录。")
    except sqlite3.Error as e:
        # 出现错误时打印错误并回滚
        conn.rollback()
        _LOGGER.error(f"删除记录失败: {e}")

    # 关闭连接
    cursor.close()
    conn.close()
