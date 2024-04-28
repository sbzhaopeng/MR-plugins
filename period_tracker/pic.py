import random

def generate_random_image_link():
    # 基础图片链接
    base_url = 'https://api.r10086.com/%E5%9B%BE%E5%8C%85/%E5%B0%91%E5%A5%B3%E5%86%99%E7%9C%9F5/mom%20({}).jpg'
    # 起始数字和结束数字
    start_num = 100
    end_num = 1810
    # 生成随机数字
    random_num = random.randint(start_num, end_num)
    # 格式化为图片链接
    random_image_link = base_url.format(random_num)
    return random_image_link

