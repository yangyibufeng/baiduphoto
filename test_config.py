import sys
sys.path.insert(0, 'D:/resources/pycharm_code/baiduphoto')

from myself.down_all.config_loader import load_cookies_from_settings

print('测试配置加载:')
cookies = load_cookies_from_settings()
if cookies:
    print('成功加载cookies')
    print(f'BDUSS_BFESS: {cookies.get("BDUSS_BFESS", "NOT FOUND")[:50]}...')
    print(f'BAIDUID: {cookies.get("BAIDUID", "NOT FOUND")}')
    print(f'STOKEN: {cookies.get("STOKEN", "NOT FOUND")[:50]}...')
    print(f'所有键: {list(cookies.keys())}')
else:
    print('未能加载cookies')