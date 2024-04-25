import sqlite3
from datetime import datetime

# 连接数据库
def connect_database():
    # 连接到SQLite数据库
    # 如果数据库不存在，那么它就会被创建，最终将返回一个数据库对象。
    conn = sqlite3.connect('health.db')
    cursor = conn.cursor()
    return conn, cursor


# 判断表是否存在
def table_exists(table_name):
    conn, cursor = connect_database()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists


# 新建信息表
def create_tables():
    conn, cursor = connect_database()
    tables = ['user_info', 'menstrual_cycle_info', 'cycle_phase_list']
    for table in tables:
        if not table_exists(table):
            if table == 'user_info':
                cursor.execute('''
                    CREATE TABLE user_info (
                        name TEXT PRIMARY KEY,
                        birthdate DATE
                    )
                ''')
            elif table == 'menstrual_cycle_info':
                cursor.execute('''
                    CREATE TABLE menstrual_cycle_info (
                        name TEXT,
                        start_date DATE,
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

# 向表中插入数据
def insert_data(table_name, data):
    # 连接到数据库
    conn, cursor = connect_database()

    # 构建 SQL 插入语句
    columns = ', '.join(data[0].keys())  # 将数据的第一行（字典）的键（列名）连接成字符串
    placeholders = ', '.join(['?' for _ in range(len(data[0]))])  # 创建与列数相等的占位符字符串
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'  # 构建插入语句

    # 执行插入操作
    for row in data:
        cursor.execute(insert_query, tuple(row.values()))  # 将每一行的值插入到表中

    # 提交更改
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()



# 展示表中的所有数据
#def fetch_all_data(table_name):
    #conn, cursor = connect_database()
    #cursor.execute(f"SELECT * FROM {table_name}")
    #data = cursor.fetchall()
    #conn.close()
    #return data

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
    
    # 如果找不到name列，抛出异常
    if name_index is None:
        raise ValueError("Table does not have a 'name' column")
    
    # 构建SELECT语句，选择所有列，以name列作为索引
    column_names = ", ".join([info[1] for info in table_info])  # 获取所有列名
    select_query = f"SELECT {column_names} FROM {table_name}"
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





table_name = 'menstrual_cycle_info'
all_data = fetch_all_data(table_name)
print(all_data)







