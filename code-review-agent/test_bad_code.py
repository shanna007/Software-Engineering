def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def get_user_info(user_id):
    # 硬编码数据库密码
    db = connect_db("admin", "123456")
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    return user

def process_list(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item)
    # 重复代码
    result2 = []
    for item in items:
        if item > 0:
            result2.append(item)
    return result
