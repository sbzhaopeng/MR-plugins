import sqlite3
from datetime import datetime

# 连接到SQLite数据库
# 如果数据库不存在，那么它就会被创建，最终将返回一个数据库对象。
conn = sqlite3.connect('women_health.db')
cursor = conn.cursor()

# 创建用户信息表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info (
        name TEXT PRIMARY KEY,
        birthdate TEXT
    )
''')

# 创建月经周期信息表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS menstrual_cycle_info (
        name TEXT,
        start_date TEXT,
        FOREIGN KEY(name) REFERENCES user_info(name)
    )
''')

# 用户输入并验证
def get_validated_input(prompt, data_type, format=None):
    while True:
        user_input = input(prompt)
        if data_type == 'date':
            try:
                valid_date = datetime.strptime(user_input, format)
                return valid_date.strftime('%Y-%m-%d')
            except ValueError:
                print("Invalid date. Correct format: YYYY-MM-DD.")
        else:
            return user_input

# 添加用户信息
name = get_validated_input("Enter the user's name: ", 'text')
birthdate = get_validated_input("Enter the user's birthdate (YYYY-MM-DD): ", 'date', '%Y-%m-%d')

# 插入用户信息
try:
    cursor.execute('INSERT INTO user_info (name, birthdate) VALUES (?, ?)', (name, birthdate))
except sqlite3.IntegrityError:
    print(f"User '{name}' already exists in the database.")

# 循环录入月经周期开始日期至用户输入 'done'
while True:
    start_date_str = get_validated_input("Enter a start date for menstrual cycle (YYYY-MM-DD) or 'done' to finish: ", 'date', '%Y-%m-%d')
    if start_date_str.lower() == 'done':
        break

    # 将日期插入到数据库
    try:
        cursor.execute('INSERT INTO menstrual_cycle_info (name, start_date) VALUES (?, ?)', (name, start_date_str))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"The start date '{start_date_str}' is already recorded for the user '{name}'.")

# 关闭数据库连接
conn.close()
print("All user data entry is complete.")
