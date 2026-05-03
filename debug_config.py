import sys
import json
import os

# 模拟load_config_from_toml
def load_config_from_toml():
    print("尝试加载TOML配置...")
    # 假设没有TOML文件，返回None
    print("未找到TOML配置文件")
    return None


# 模拟load_config_from_json
def load_config_from_json():
    print("尝试加载JSON配置...")
    # 模拟从settings.json加载
    config = {
        'clienttype': 70,
        'bdstoken': 'e0bfaedf7a37d6ca6eab48e0146624b5',
        'need_thumbnail': 1,
        'need_filter_hidden': 0,
        'Cookie': 'PSTM=1755786229; MAWEBCUID=web_DKYjqczwHbcpxGQQNBjaYsvBmGrFbLYSCQkXiBEPhLjNWNncyi; BIDUPSID=175DE1A795F1F131D427946F16EF5E54; BDUSS=I1flZmWFNCYlphWDJ-eUtjZ214R2pBbjQyQkl-cW9HdEVSM2JFWU1oTn5BU2RwRVFBQUFBJCQAAAAAAQAAAAEAAABKTjw7eXliZjIyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH90~2h~dP9oWW; BDUSS_BFESS=I1flZmWFNCYlphWDJ-eUtjZ214R2pBbjQyQkl-cW9HdEVSM2JFWU1oTn5BU2RwRVFBQUFBJCQAAAAAAQAAAAEAAABKTjw7eXliZjIyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH90~2h~dP9oWW; STOKEN=dcf7a805ac5b21a42213da62bcfca3eabd8054157cc9360c3992c85bab535cde; BAIDUID=8E6A72FBC9B26193363CB387A6DF9AEB:FG=1; H_PS_PSSID=63147_64008_66588_66594_66694_66684_66851_66961_66985_67005_67040_67048_67092_67055_67044_67109_67130_67146_67151_67159_67177_67171; H_WISE_SIDS=63147_64008_66588_66594_66694_66684_66851_66961_66985_67005_67040_67048_67092_67055_67044_67109_67130_67146_67151_67159_67177_67171; csrfToken=Wg6qasnMcgDQ0nN8b3FcBgZ_; PANPSC=15564593827564601942%3Au9Rut0jYI4q3t%2FyPRelfalcS2d9ns3O5C61tf8CKQkjia%2Bkz7e6H9A3MPJHnDhkC%2FbxY8VzpdwgUjv0lYQ12WM%2FNbbUaC9LQIlcWVgoyoWziRClWYPNr2RAwtHVXjStQtpvLsQmrbYjZ81l%2BOzvAFvaPhNW%2FPAiQ7BoPl0l%2BOK2GEazXAT3bTfsKHAFiGrIySUc5rpaWKb1toLnfYC42LfDSJFbrrClxn%2Bsm3OdmtaiJQPEbk0B1UDRe%2FTbrIHmu26t7pNjyggy4CqAVuJnNT49TP9LiBms3krFWWqsgPEw%3D; BAIDUID_BFESS=8E6A72FBC9B26193363CB387A6DF9AEB:FG=1; PANWEB=1; PANWEB.sig=mEnYrSeaQqssYZire89rFPmLY9htA0FzmyWp6jBsV1U'
    }
    print("从settings.json加载配置成功")
    return config


# 模拟load_cookies_from_settings
def load_cookies_from_settings():
    print("开始加载cookies...")
    
    # 优先尝试TOML
    config = load_config_from_toml()
    print(f"TOML配置结果: {config}")
    
    # 如果TOML加载失败，尝试JSON
    if config is None:
        print("TOML配置失败，尝试JSON配置...")
        config = load_config_from_json()
    
    # 如果都没有找到配置文件，提供示例格式
    if not config:
        print("警告：未找到配置文件，使用示例格式。")
        # 返回示例值（这不应该发生）
        return {
            'BDUSS_BFESS': 'your_bdsuss_here',
            'BAIDUID': 'your_baiduid_here',
            'STOKEN': 'your_stoken_here'
        }
    
    print(f"加载的配置: {list(config.keys())}")
    
    # 从配置中获取cookies
    cookies = {}
    if 'cookies' in config:
        cookies = config['cookies']
    elif 'Cookie' in config:
        # 从settings.json的Cookie字段解析cookies
        cookie_string = config['Cookie']
        # 解析Cookie字符串
        cookie_parts = cookie_string.split('; ')
        parsed_cookies = {}
        for part in cookie_parts:
            if '=' in part:
                key, value = part.split('=', 1)
                parsed_cookies[key.strip()] = value.strip()
        
        print(f"解析后的cookies键: {list(parsed_cookies.keys())}")
        
        # 从解析的cookies中提取关键字段
        cookies['BDUSS_BFESS'] = parsed_cookies.get('BDUSS_BFESS') or parsed_cookies.get('BDUSS')
        cookies['BAIDUID'] = parsed_cookies.get('BAIDUID', parsed_cookies.get('BAIDUID_BFESS', ''))
        cookies['STOKEN'] = parsed_cookies.get('STOKEN', '')
    elif 'BDUSS_BFESS' in config or 'BDUSS' in config or 'BAIDUID' in config or 'STOKEN' in config:
        # 直接在顶层找到cookies
        cookies = {k: v for k, v in config.items() if k in ['BDUSS_BFESS', 'BDUSS', 'BAIDUID', 'STOKEN']}
    
    print(f"最终cookies: {cookies}")
    return cookies


# 执行测试
result = load_cookies_from_settings()
print("\n最终结果:")
for key, value in result.items():
    print(f"  {key}: {value[:50] if len(str(value)) > 50 else value}...")