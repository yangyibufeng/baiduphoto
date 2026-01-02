import requests
import json
import os

from pybaiduphoto import API
from pybaiduphoto.yybf.WithTime import WithTime


def start(context):
    with open("settings.json", 'r') as f:
        json_data = json.load(f)
    context["clienttype"] = json_data["clienttype"]
    context["bdstoken"]= json_data["bdstoken"]
    context["need_thumbnail"] = json_data["need_thumbnail"]
    context["need_filter_hidden"] = json_data["need_filter_hidden"]
    cookie = json_data["Cookie"]

    if not cookie:
        print("请填写Cookie")
        return

    # 将 Cookie 字符串转换为字典格式
    cookie_dict = {}
    for item in cookie.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookie_dict[key] = value
    context["Cookie"] = cookie_dict

    # os.makedirs(self.path)

    # self.func()

def getOnePicture(context):
    cookie = context["Cookie"]
    
    api = API(cookies=cookie)
    list1 = api.get_self_1page(typeName='Item')

    print(f"items count={len(list1['items'])}")
    
    # 打印info元素的信息
    print("All items:")
    for i, item in enumerate(list1['items']):
        print(f"  {i+1}: {item}")
        print(f"     Info keys: {json.dumps(item.info, indent=4, ensure_ascii=False)}")
        if i > 2 :
            break
    print(f" list.has_more:{list1['has_more']}")
    print(f" list.cursor:{list1['cursor']}")

    num = 1
    for item in list1['items']:
        print(f"{num} - item:{item},item.type:{type(item)}")
        num += 1
        if num > 3:
            return

def getWithTimeRange(context):
    start_time = "2025:10:01"
    end_time = "2025:11:02"

    cookie = context["Cookie"]

    api = API(cookies=cookie)
    
    # 实例化 WithTime 类
    with_time = WithTime()
    
    # 定义单页获取函数
    def single_page_func(cursor=None):
        return api.get_self_1page(typeName='Item', cursor=cursor)
    
    # 调用方法获取结果
    result = with_time.get_photo_with_date_range(single_page_func,
                                                   start_date=start_time, 
                                                   end_date=end_time)
    
    # 从结果中提取 items
    items_list = result['items']
    
    print(f"items count={len(items_list)}")
    for i, item in enumerate(items_list):
        print(f"  {i+1}: {item}")
        print(f"     Info keys: {json.dumps(item.info, indent=4, ensure_ascii=False)}")
        if i > 2 :
            break

    url = api.get_batchDownloadLink(items_list)
    print(f"url:{url}")


if __name__ == '__main__':
    context = {}
    start(context)
    # getOnePicture(context)
    getWithTimeRange(context)
    # pass